import logging
import re
import time
import threading
import os
from typing import List, Tuple, Dict, Any, Optional
from langchain_core.documents import Document
from app.services.rag.vector_store import get_vector_store
from app.core.config import DEBUG_RAG
from app.services.rag.debug_logger import get_debug_store
from app.services.rag.query_normalizer import STOP_WORDS

logger = logging.getLogger("rag_retriever")

# Global cache for documents to optimize keyword/acronym matching speed
_docs_cache: List[Document] = []
_docs_cache_count: int = 0
_docs_cache_last_updated: float = 0.0
_docs_cache_hits: int = 0
_docs_cache_misses: int = 0


def clear_retriever_cache():
    """Clears the retriever documents cache to force reload on the next query."""
    global _docs_cache, _docs_cache_count, _docs_cache_last_updated
    _docs_cache = []
    _docs_cache_count = 0
    _docs_cache_last_updated = 0.0


def normalize_query_text(query: str) -> str:
    """Normalizes and expands standard student queries to target canonical terms."""
    if not query:
        return ""
    query_lower = query.lower().strip()
    
    # 1. Direct synonym expansions to ensure strong semantic & keyword matches
    replacements = {
        # Exams & Calendar
        r"\bend\s+sems?\b": "end semester examination schedule",
        r"\bend\s+semesters?\b": "end semester examination schedule",
        r"\bmid\s+sems?\b": "mid semester examination schedule",
        r"\bmid\s+semesters?\b": "mid semester examination schedule",
        r"\bexam\s+schedules?\b": "examination schedule",
        r"\bexam\s+dates?\b": "examination schedule",
        r"\bwhen\s+is\s+end\s+sem\b": "end semester examination schedule",
        r"\bwhen\s+are\s+exams\b": "examination schedule",
        r"\bexam\s+schedu\b": "examination schedule",
        
        # Placements
        r"\bplacement\s+seasons?\b": "placement process recruitment",
        r"\bplacements?\b": "placement process recruitment",
        r"\bhave\s+placements\s+started\b": "placement process recruitment commencement start",
        
        # Hostels & Facilities
        r"\bhostel\s+fees?\b": "hostel fee payment details",
        r"\blibrary\s+timings?\b": "library hours timing schedule",
        r"\bbus\s+timings?\b": "bus transport schedule timing",
        r"\bscholarships?\b": "scholarship financial aid details",
    }
    
    normalized = query_lower
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized)
        
    return normalized.strip()


def detect_intent(query: str) -> str | None:
    """Detects user intent based on keywords in the query."""
    query_lower = query.lower()

    intents = {
        "club": [
            "technical club", "cultural club", "club", "coding", "programming",
            "robotics", "hackathon"
        ],
        "department": [
            "department", "aiml", "cse", "ece", "mechanical", "civil",
            "biotechnology"
        ],
        "hostel": [
            "hostel", "mess", "room", "accommodation"
        ],
        "facility": [
            "medical", "doctor", "healthcare", "bank", "atm", "gym",
            "cafeteria", "canteen"
        ],
        "building": [
            "library", "building", "auditorium", "lecture hall"
        ],
        "notice": [
            "notice", "announcement", "circular"
        ],
        "calendar": [
            "exam", "quiz", "semester", "academic calendar", "registration date"
        ]
    }

    for intent, keywords in intents.items():
        if intent == "facility" and "leave" in query_lower:
            continue
        for kw in keywords:
            # Match multi-word phrases directly or match single words at boundaries (supporting optional plurals)
            if " " in kw:
                if kw in query_lower or (kw + "s") in query_lower:
                    return intent
            else:
                pattern = r"\b" + re.escape(kw) + r"s?\b"
                if re.search(pattern, query_lower):
                    return intent

    return None


def get_acronym(text: str) -> str:
    """Generates acronym for a text, ignoring non-alphabetic chars."""
    clean_text = "".join(c if c.isalnum() or c.isspace() else " " for c in text)
    words = clean_text.split()
    if len(words) <= 1:
        return ""
    return "".join(w[0] for w in words if w[0].isupper()).lower()


class ContextString(str):
    """A string subclass that carries source metadata."""
    source: str
    def __new__(cls, content: str, source: str):
        instance = super().__new__(cls, content)
        instance.source = source
        return instance


# Thread-local storage to cache the sources from the last retrieve_with_scores run
_local_retrieval_data = threading.local()


def get_last_retrieval_sources() -> List[str]:
    """Retrieve the cached sources of the last retrieve_with_scores execution."""
    return getattr(_local_retrieval_data, "sources", [])


def get_last_retrieved_docs() -> List[Document]:
    """Retrieve the cached documents of the last retrieve_with_scores execution."""
    return getattr(_local_retrieval_data, "documents", [])



def is_reasoning_query(query: str) -> bool:
    """
    Checks if the query is a reasoning (recommendation, comparison, guidance, etc.) query.
    """
    if not query:
        return False
    query_lower = query.lower()
    reasoning_keywords = [
        "best", "recommend", "recommendation", "suggest", "suggestion",
        "compare", "comparison", "difference", "different", "pros", "cons",
        "advantages", "disadvantages", "better", "which is better", "guide",
        "advice", "overview", "summarize", "summary", "explain", "help me choose",
        "suitable", "ideal"
    ]
    return any(kw in query_lower for kw in reasoning_keywords)


def is_recommendation_query(query: str) -> bool:
    """Fallback alias for compatibility."""
    return is_reasoning_query(query)


def classify_query(query: str, docs_cache: List[Document]) -> str:
    """
    Classifies a query into 'document', 'campus', or 'mixed'.
    Uses static keyword dictionaries and checks against clean filenames in the cache.
    """
    query_lower = query.lower()
    
    # 1. Keywords indicating document queries
    doc_keywords = {
        "resume", "candidate", "cv", "sop", "uploaded", "document", "file", 
        "pdf", "project", "profile", "portfolio", "uploaded file", "this document",
        "my document", "academic resume", "placement resume", "cvs", "resumes", "documents"
    }
    has_doc_kw = any(re.search(r"\b" + re.escape(kw) + r"\b", query_lower) for kw in doc_keywords)
    
    # Check if query contains terms from any dynamic document filenames
    has_filename_match = False
    for doc in docs_cache:
        if doc.metadata.get("source") == "kb_document":
            filename = doc.metadata.get("filename", "")
            if filename:
                base_name = os.path.splitext(filename.lower())[0]
                clean_base = re.sub(r"[^\w\s]", " ", base_name)
                filename_words = set(clean_base.split())
                sig_words = {w for w in filename_words if len(w) > 2 and w not in ["pdf", "docx", "doc", "txt", "md"]}
                if sig_words and all(re.search(r"\b" + re.escape(w) + r"\b", query_lower) for w in sig_words):
                    has_filename_match = True
                    break

    # 2. Keywords indicating campus queries
    campus_keywords = {
        "club", "department", "hostel", "mess", "room", "facility", "building",
        "library", "canteen", "notice", "announcement", "circular", "exam", "quiz",
        "semester", "academic calendar", "registration", "placement process",
        "scholarship", "timing", "admission", "course", "fees", "placement cutoff"
    }
    has_campus_kw = any(re.search(r"\b" + re.escape(kw) + r"\b", query_lower) for kw in campus_keywords)
    
    is_doc = has_doc_kw or has_filename_match
    is_campus = has_campus_kw
    
    if is_doc and is_campus:
        return "mixed"
    elif is_doc:
        return "document"
    elif is_campus:
        return "campus"
    else:
        # Fallback terms for dynamic resumes/profiles
        resume_terms = {"cgpa", "gpa", "skills", "experience", "education", "internship", "project", "technologies", "graduated"}
        if any(re.search(r"\b" + re.escape(w) + r"\b", query_lower) for w in resume_terms):
            return "mixed"
        return "campus"


def compile_chroma_filter(metadata_filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not metadata_filters:
        return None
        
    cleaned_filters = {}
    for k, v in metadata_filters.items():
        if v is not None:
            if k == "tags" and isinstance(v, list) and v:
                if len(v) == 1:
                    cleaned_filters["tags"] = v[0]
                else:
                    cleaned_filters["tags"] = {"$in": v}
            else:
                cleaned_filters[k] = v
                
    if not cleaned_filters:
        return None
    if len(cleaned_filters) == 1:
        return cleaned_filters
    else:
        return {"$and": [{k: v} for k, v in cleaned_filters.items()]}


SEMANTIC_EXPANSIONS = {
    "placement": ["placement", "placements", "recruitment", "hiring", "ppo", "job", "career", "interview", "salary", "package", "companies", "placement process", "placement cutoff", "recruitment season"],
    "recruitment": ["placement", "placements", "recruitment", "hiring", "ppo", "job", "career", "interview", "salary", "package", "companies", "placement process", "placement cutoff", "recruitment season"],
    "hostel": ["hostel", "hostels", "accommodation", "room", "residence", "mess", "dormitory", "dorms", "dorm", "hostel fee", "hostel rules"],
    "accommodation": ["hostel", "hostels", "accommodation", "room", "residence", "mess", "dormitory", "dorms", "dorm", "hostel fee"],
    "library": ["library", "libraries", "books", "reading room", "study hall", "book"],
    "exam": ["exam", "exams", "semester", "midsem", "endsem", "quiz", "examination", "mid semester", "end semester", "quizzes", "examination regulations"],
    "semester": ["exam", "exams", "semester", "midsem", "endsem", "quiz", "examination", "mid semester", "end semester", "quizzes"],
    "calendar": ["calendar", "calendars", "schedule", "events", "holidays", "academic calendar", "registration date"],
    "scholarship": ["scholarship", "scholarships", "financial aid", "fee waiver", "grant", "grants", "tuition fee waiver"],
    "admission": ["admission", "admissions", "apply", "enrollment", "registration", "eligibility", "counselling"],
    "club": ["club", "clubs", "society", "societies", "student activity", "technical club", "cultural club", "club recruitment"],
    "transport": ["transport", "bus", "shuttle", "vehicle", "travel", "commute", "transportation", "cycle", "cycle sharing", "parking"],
    "mess": ["mess", "food", "hostel mess", "dining", "meal", "hostel food"]
}

def get_query_expansions(query_lower: str) -> List[str]:
    expansions = []
    for key, values in SEMANTIC_EXPANSIONS.items():
        if key in query_lower or any(val in query_lower for val in values):
            expansions.extend(values)
    return list(set(expansions))

def calculate_metadata_score(doc_metadata: dict, query_lower: str, detected_intent: str = "General") -> float:
    score = 0.0
    category = doc_metadata.get("category", "").lower()
    source = doc_metadata.get("source", "").lower()
    source_type = doc_metadata.get("source_type", "").lower()
    title = (
        doc_metadata.get("title") or 
        doc_metadata.get("filename") or 
        doc_metadata.get("name") or 
        ""
    ).lower()

    # Intent to category mapping for weighted intent routing boosts
    INTENT_TO_CATEGORY = {
        "Academic Calendar": ["academic", "calendar"],
        "Notice": ["notice"],
        "Department": ["department"],
        "Hostel": ["hostel", "mess"],
        "Facility": ["facility"],
        "Building": ["building"],
        "FAQ": ["faq"],
        "Placement": ["placement"],
        "Club": ["club"],
        "Navigation": ["building", "facility"],
    }
    
    # Intent Match Boost
    if detected_intent in INTENT_TO_CATEGORY:
        target_categories = INTENT_TO_CATEGORY[detected_intent]
        if category in target_categories or source in target_categories or source_type in target_categories:
            score += 0.05  # Moderate, non-overpowering intent boost

    # 1. Prioritization for calendar / exam queries
    calendar_query_terms = {"calendar", "schedule", "timeline", "exam", "semester", "date"}
    if any(term in query_lower for term in calendar_query_terms):
        if category == "calendar" or source == "calendar" or category == "academic" or source == "academic":
            score += 0.12  # Mild boost for academic/calendar documents
        if any(term in title for term in ["calendar", "schedule", "timeline", "exam", "semester"]):
            score += 0.08  # Boost if title contains keywords
        if category == "notice" or source == "notice":
            score -= 0.05  # Slight penalty for notices in calendar queries

    # 2. Prioritization for placement queries
    placement_query_terms = {"placement", "recruitment", "hiring", "ppo", "job", "career", "salary"}
    if any(term in query_lower for term in placement_query_terms):
        if category == "placement" or source == "placement":
            score += 0.12
        if "placement" in title or "recruitment" in title:
            score += 0.08

    # 3. Prioritization for hostel queries
    hostel_query_terms = {"hostel", "mess", "dorm", "room", "accommodation"}
    if any(term in query_lower for term in hostel_query_terms):
        if category == "hostel" or source == "hostel":
            score += 0.12
        if "hostel" in title or "mess" in title:
            score += 0.08

    # 4. Prioritization for library queries
    library_query_terms = {"library", "book", "reading room"}
    if any(term in query_lower for term in library_query_terms):
        if category == "library" or source == "library":
            score += 0.12
        if "library" in title:
            score += 0.08

    # 5. Prioritization for club queries
    club_query_terms = {"club", "society", "societies", "student activity"}
    if any(term in query_lower for term in club_query_terms):
        if category == "club" or source == "club":
            score += 0.12
        if "club" in title or "society" in title:
            score += 0.08

    # 6. Prioritization for FAQ / informational queries
    informational_terms = {"how", "what", "why", "who", "procedure", "process", "rule", "rules", "policy", "policies"}
    if any(term in query_lower for term in informational_terms):
        if source == "faq" or source_type == "faq":
            score += 0.08  # Additional boost for FAQ documents on informational queries

    # 7. Penalize notices slightly for specific entity queries (club, department)
    if "club" in query_lower or "department" in query_lower:
        if category == "notice" or source == "notice":
            score -= 0.08

    # 8. Category mapping keywords (backward compatibility)
    category_keywords = {
        "placement": ["placement", "placements", "recruitment", "hiring", "ppo", "job", "career", "interview", "salary", "package", "companies", "placement process", "placement cutoff", "recruitment season"],
        "hostel": ["hostel", "hostels", "accommodation", "room", "residence", "mess", "dormitory", "dorms", "dorm", "hostel fee", "hostel rules"],
        "academic": ["exam", "exams", "semester", "midsem", "endsem", "registration", "credits", "cgpa", "course", "syllabus", "academics", "academic calendar"],
        "club": ["club", "clubs", "society", "societies", "student activity", "technical club", "cultural club", "club recruitment"],
        "library": ["library", "libraries", "books", "reading room", "study hall", "book"],
        "transport": ["transport", "bus", "shuttle", "commute", "cycle", "cycle sharing", "parking", "vehicle"],
        "admission": ["admission", "admissions", "apply", "eligibility", "counselling"],
        "scholarship": ["scholarship", "scholarships", "financial aid", "fee waiver", "grant", "grants", "tuition fee waiver"]
    }
    
    for cat_name, keywords in category_keywords.items():
        if any(kw in query_lower for kw in keywords):
            if category == cat_name or source == cat_name or source_type == cat_name:
                score += 0.10
            elif category in ["other", "faq", "general", "academic", ""] or not category:
                pass
            else:
                score -= 0.05
                
    # 9. Department check
    dept = doc_metadata.get("department", "")
    if dept:
        dept_lower = dept.lower()
        if dept_lower in query_lower:
            score += 0.05
            
    # 10. Tags check
    tags = doc_metadata.get("tags", [])
    if isinstance(tags, list):
        for tag in tags:
            if tag.lower() in query_lower:
                score += 0.03
                
    # 11. Priority check
    priority = doc_metadata.get("priority", 3)
    if priority == 1:
        score += 0.02
    elif priority == 2:
        score += 0.01
        
    # 12. Version check
    version = doc_metadata.get("version", 1)
    score += min(0.01, version * 0.002)
    
    # 13. Resume check
    filename = doc_metadata.get("filename", "").lower()
    if "resume" in filename or "cv" in filename or source == "resume" or source_type == "resume":
        profile_keywords = ["resume", "cv", "experience", "education", "project", "work", "job", "career", "skills", "profile", "gpa", "internship"]
        if not any(k in query_lower for k in profile_keywords):
            score -= 0.50

    return score


def matches_metadata_filters(metadata: dict, filters: dict | None) -> bool:
    """Helper to check if a document's metadata matches the active filters."""
    if not filters:
        return True
    for k, v in filters.items():
        if v is None:
            continue
        if k == "tags":
            tags = metadata.get("tags", [])
            if isinstance(v, list):
                if not any(tag in tags for tag in v):
                    return False
            else:
                if v not in tags:
                    return False
        else:
            if metadata.get(k) != v:
                return False
    return True


def merge_retrieved_chunks(results: List[Dict], limit_k: int = 2) -> List[Dict]:
    """
    Groups retrieved chunks by parent document, sorts them by their original sequential position
    in Chroma, merges overlapping or adjacent texts, and keeps only the highest-scoring unique groups.
    """
    if not results:
        return []
        
    from collections import defaultdict
    groups = defaultdict(list)
    for item in results:
        doc = item["doc"]
        meta = doc.metadata or {}
        doc_id = (
            meta.get("id") or 
            meta.get("filename") or 
            meta.get("title") or 
            meta.get("name") or 
            meta.get("question") or 
            meta.get("event") or 
            "generic"
        )
        groups[doc_id].append(item)
        
    def get_cache_index(doc: Document) -> int:
        for idx, cache_doc in enumerate(_docs_cache):
            if cache_doc.page_content == doc.page_content:
                return idx
        return 999999
        
    def are_consecutive(item_a: Dict, item_b: Dict) -> bool:
        meta_a = item_a["doc"].metadata or {}
        meta_b = item_b["doc"].metadata or {}
        
        # Try chunk_number first
        num_a = meta_a.get("chunk_number")
        num_b = meta_b.get("chunk_number")
        if num_a is not None and num_b is not None:
            try:
                return abs(int(num_a) - int(num_b)) == 1
            except (ValueError, TypeError):
                pass
                
        # Try chunk_index
        idx_a = meta_a.get("chunk_index")
        idx_b = meta_b.get("chunk_index")
        if idx_a is not None and idx_b is not None:
            try:
                return abs(int(idx_a) - int(idx_b)) == 1
            except (ValueError, TypeError):
                pass

        # Try cache index
        cache_a = get_cache_index(item_a["doc"])
        cache_b = get_cache_index(item_b["doc"])
        if cache_a != 999999 and cache_b != 999999:
            return abs(cache_a - cache_b) == 1
            
        return False

    def merge_two_texts_if_overlap(text_a: str, text_b: str, max_overlap: int = 150) -> Optional[str]:
        text_a_strip = text_a.strip()
        text_b_strip = text_b.strip()
        
        # Suffix-prefix overlap detection
        for length in range(min(len(text_a_strip), len(text_b_strip), max_overlap), 9, -1):
            suffix = text_a_strip[-length:]
            prefix = text_b_strip[:length]
            if suffix == prefix:
                return text_a_strip + text_b_strip[length:]
                
        # Substring redundancy check
        if text_b_strip in text_a_strip:
            return text_a_strip
        if text_a_strip in text_b_strip:
            return text_b_strip
            
        return None
        
    merged_results = []
    
    for doc_id, items in groups.items():
        # Sort sequentially
        items.sort(key=lambda x: get_cache_index(x["doc"]))
        
        # We will build runs of mergeable chunks
        current_run = [dict(items[0])]
        
        for item in items[1:]:
            prev_item = current_run[-1]
            if are_consecutive(prev_item, item):
                # Try to merge
                merged_text = merge_two_texts_if_overlap(prev_item["doc"].page_content, item["doc"].page_content)
                if merged_text is not None:
                    # Merge them in-place in current_run's last item
                    prev_item["doc"] = Document(
                        page_content=merged_text,
                        metadata=prev_item["doc"].metadata
                    )
                    prev_item["final_score"] = min(prev_item["final_score"], item["final_score"])
                    prev_item["raw_score"] = min(prev_item["raw_score"], item["raw_score"])
                    continue
            
            # If not consecutive or no overlap, start a new run
            current_run.append(dict(item))
            
        for run_item in current_run:
            merged_results.append(run_item)
            
    merged_results.sort(key=lambda x: x["final_score"])
    return merged_results[:limit_k]


def retrieve_with_scores(
    query: str,
    k: int = 5,
    metadata_filters: Optional[Dict[str, Any]] = None
) -> List[Tuple[Document, float]]:
    global _docs_cache, _docs_cache_count, _docs_cache_last_updated, _docs_cache_hits, _docs_cache_misses

    start_total = time.time()
    
    # Telemetry
    debug_store = get_debug_store() if DEBUG_RAG else None
    
    # 1. Production Query Normalization & Intent Routing (Task 1 & 2)
    from app.services.rag.query_normalizer import QueryNormalizer
    normalization_result = QueryNormalizer.normalize(query)
    normalized_query = normalization_result["normalized_query"]
    query_lower = normalized_query
    detected_intent = normalization_result["detected_intent"]
    
    if debug_store:
        debug_store.original_query = query
        debug_store.normalized_query = normalized_query
        t_embed_start = time.time()
        try:
            get_vector_store().embeddings.embed_query(normalized_query)
        except Exception:
            pass
        debug_store.embedding_time_ms = (time.time() - t_embed_start) * 1000.0
        
        t_meta_start = time.time()
        cf = compile_chroma_filter(metadata_filters)
        debug_store.metadata_filtering_time_ms = (time.time() - t_meta_start) * 1000.0
        debug_store.metadata_filtering_details = str(cf) if cf else "None"

    vector_store = get_vector_store()
    
    # 2. Synchronize all documents cache from Chroma
    start_chroma_count = time.time()
    time_chroma_count = 0.0
    time_cache_sync = 0.0
    
    now = time.time()
    if not _docs_cache or (now - _docs_cache_last_updated > 10.0):
        _docs_cache_misses += 1
        try:
            current_count = vector_store._collection.count()
        except Exception as e:
            logger.error(f"Error counting Chroma collection: {e}")
            current_count = 0
        time_chroma_count = time.time() - start_chroma_count

        start_cache_sync = time.time()
        try:
            if not _docs_cache or current_count != _docs_cache_count:
                all_chroma = vector_store.get(limit=10000)
                _docs_cache = []
                for idx, doc_id in enumerate(all_chroma["ids"]):
                    metadata = all_chroma["metadatas"][idx]
                    page_content = all_chroma["documents"][idx]
                    _docs_cache.append(
                        Document(page_content=page_content, metadata=metadata)
                    )
                _docs_cache_count = current_count
            _docs_cache_last_updated = time.time()
        except Exception as e:
            logger.error(f"Error fetching documents from ChromaDB: {e}")
            _docs_cache = []
            _docs_cache_count = 0
        time_cache_sync = time.time() - start_cache_sync
    else:
        _docs_cache_hits += 1
        logger.info("Chroma doc count and sync cache hit (TTL < 10s)")

    # 3. Classify Query Intent & reasoning mode
    query_class = classify_query(normalized_query, _docs_cache)
    is_doc_query = (query_class in ["document", "mixed"])
    reasoning = is_reasoning_query(normalized_query)
    
    original_intent = detected_intent
    intent = detected_intent
    
    if reasoning:
        intent = None
        k_vector = 15
        limit_k = 4
    else:
        k_vector = 8
        limit_k = 2

    # Compile metadata filters for ChromaDB
    compiled_filter = compile_chroma_filter(metadata_filters)

    # 4. Vector Search
    start_vector = time.time()
    vector_results = []

    logger.info(f"Performing global semantic search across the entire Chroma collection with filter: {compiled_filter}")
    try:
        vector_results = vector_store.similarity_search_with_score(
            query,
            k=k_vector,
            filter=compiled_filter
        )
    except Exception as e:
        logger.error(f"Global semantic search failed: {e}")
        vector_results = []

    # Supplemental search for document-targeted queries
    if is_doc_query:
        print(f"\n--- DEBUG: Detected dynamic doc query ({query_class}). Supplementing... ---")
        try:
            doc_filter = {"source": "kb_document"}
            if compiled_filter:
                if "$and" in compiled_filter:
                    doc_filter = {"$and": [{"source": "kb_document"}] + compiled_filter["$and"]}
                else:
                    doc_filter = {"$and": [{"source": "kb_document"}, compiled_filter]}
            
            dynamic_results = vector_store.similarity_search_with_score(
                query,
                k=k_vector,
                filter=doc_filter
            )
            print(f"--- DEBUG: Found {len(dynamic_results)} dynamic chunks in Chroma ---")
            vector_results.extend(dynamic_results)
        except Exception as e:
            print(f"--- DEBUG: Exception in supplemental search: {e} ---")
            logger.error(f"Failed to supplement search with dynamic documents: {e}")
        
    time_vector = time.time() - start_vector
    if debug_store:
        debug_store.vector_search_time_ms = time_vector * 1000.0

    # 5. Query Expansion & Heuristic / Acronym matching
    start_keyword = time.time()
    expanded_terms = get_query_expansions(query_lower)
    
    query_clean = re.sub(r'[^\w\s]', ' ', query_lower)
    query_words = set(query_clean.split())
    
    # Expand words for keyword matching
    expanded_query_words = query_words.copy()
    for term in expanded_terms:
        expanded_query_words.update(term.split())

    meaningful_query_words = set(normalization_result["extracted_keywords"])
    expanded_meaningful_query_words = meaningful_query_words.copy()
    for term in expanded_terms:
        # Filter synonyms expansions to remove stop words
        expanded_meaningful_query_words.update([w for w in term.split() if w not in STOP_WORDS])

    # Exclude common small words and pronouns from being matched as acronyms (e.g. "me" matching ME)
    invalid_acronyms = {
        "me", "an", "is", "it", "at", "in", "to", "by", "on", "or", "of", "no",
        "so", "he", "we", "us", "go", "do", "my", "as", "if"
    }

    keyword_candidates: List[Tuple[Document, float]] = []
    for doc in _docs_cache:
        # Apply Lexical Metadata Filtering (Task 4)
        if metadata_filters and not matches_metadata_filters(doc.metadata, metadata_filters):
            continue
            
        # Filter out expired items immediately
        if doc.metadata.get("status") == "expired":
            continue
            
        expires_at = doc.metadata.get("expires_at")
        if expires_at:
            try:
                from datetime import datetime, timezone
                if isinstance(expires_at, str):
                    exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                else:
                    exp_dt = expires_at
                if exp_dt and exp_dt < datetime.now(timezone.utc):
                    continue
            except Exception as e:
                logger.error(f"Error checking document expiry: {e}")

        orig_name = (
            doc.metadata.get("filename") or
            doc.metadata.get("name") or
            doc.metadata.get("title") or
            doc.metadata.get("event") or
            doc.metadata.get("question") or
            ""
        )
        name_lower = orig_name.lower()
        if not name_lower:
            continue

        boost_base = None

        # Check for acronym match
        acronym = get_acronym(orig_name)
        if acronym and len(acronym) >= 2 and acronym in query_words and acronym not in invalid_acronyms:
            boost_base = 0.20

        # Check for unique/meaningful word matches (including expanded synonym terms)
        name_clean = re.sub(r'[^\w\s]', ' ', name_lower)
        name_words = set(name_clean.split())
        common_words = expanded_meaningful_query_words.intersection(name_words)
        if common_words:
            boost_base = 0.30

        if boost_base is not None:
            keyword_candidates.append((doc, boost_base))
    time_keyword = time.time() - start_keyword

    # 6. Merge Vector and Keyword Candidates
    start_merge = time.time()
    merged_candidates: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for doc, score in vector_results:
        # Ignore expired items
        if doc.metadata.get("status") == "expired":
            continue
        key = (doc.page_content, doc.metadata.get("source", ""))
        merged_candidates[key] = {
            "doc": doc,
            "score": score,
            "method": "vector"
        }

    for doc, score in keyword_candidates:
        key = (doc.page_content, doc.metadata.get("source", ""))
        if key in merged_candidates:
            # Keep the better (lower distance) score
            merged_candidates[key]["score"] = min(
                merged_candidates[key]["score"],
                score
            )
            merged_candidates[key]["method"] = "both"
        else:
            merged_candidates[key] = {
                "doc": doc,
                "score": score,
                "method": "keyword"
            }
    time_merge = time.time() - start_merge

    # 7. Apply Multi-Factor Ranking (Composite Score Calculation)
    start_boosting = time.time()
    facility_keywords = [
        "medical", "healthcare", "doctor", "hospital", "dispensary",
        "pharmacy", "clinic", "treatment", "sick", "ambulance"
    ]
    dept_keywords = [
        "department", "aiml", "cse", "ece", "mechanical", "electrical",
        "civil", "biotechnology", "chemical", "management"
    ]
    club_keywords = [
        "club", "coding", "programming", "hackathon", "robotics",
        "developer", "ieee", "entrepreneurship", "music", "dance",
        "photography", "sports"
    ]
    building_keywords = [
        "building", "library", "auditorium", "hall", "complex", "gate",
        "center", "centre", "house"
    ]

    boosted_results = []
    for key, item in merged_candidates.items():
        doc = item["doc"]
        raw_score = item["score"]
        source = doc.metadata.get("source", "")
        doc_content_lower = doc.page_content.lower()

        # A. Semantic Score (normalize L2 distance: lower distance -> higher similarity)
        semantic_score = max(0.0, 1.0 - (raw_score / 1.5))
        if item["method"] == "keyword":
            semantic_score = 0.50

        # B. Keyword Overlap Score
        chunk_clean = re.sub(r'[^\w\s]', ' ', doc_content_lower)
        chunk_words = set(chunk_clean.split())
        matched_kw_count = len(expanded_meaningful_query_words.intersection(chunk_words))
        keyword_score = matched_kw_count / max(1, len(meaningful_query_words))

        # C. Title/Filename Match Score
        orig_name = (
            doc.metadata.get("filename") or
            doc.metadata.get("name") or
            doc.metadata.get("title") or
            doc.metadata.get("question") or
            ""
        ).lower()
        title_match_score = 0.0
        if orig_name:
            clean_name = re.sub(r"[^\w\s]", " ", orig_name)
            name_words = set(clean_name.split())
            matched_title_kws = expanded_meaningful_query_words.intersection(name_words)
            if matched_title_kws:
                title_match_score = len(matched_title_kws) / max(1, len(name_words))
                title_match_score = min(1.0, title_match_score + 0.2)

        # D. Source Boost & Intent Alignment
        source_boost = 0.0
        intent_boost = 0.0

        if query_class == "document":
            if source == "kb_document":
                source_boost = 0.10
            else:
                source_boost = -0.05
        elif query_class == "campus":
            if source != "kb_document":
                source_boost = 0.10
            else:
                source_boost = -0.05
        elif query_class == "mixed":
            if source == "kb_document":
                source_boost = 0.08
            else:
                source_boost = 0.04

        if any(kw in query_lower for kw in facility_keywords) and source == "facility":
            intent_boost = 0.05
        elif any(kw in query_lower for kw in dept_keywords) and source == "department":
            intent_boost = 0.05
        elif any(kw in query_lower for kw in club_keywords) and source == "club":
            intent_boost = 0.05
        elif any(kw in query_lower for kw in building_keywords) and source == "building":
            intent_boost = 0.05

        # E. Metadata Match Score (NEW)
        metadata_boost = calculate_metadata_score(doc.metadata, query_lower, detected_intent=detected_intent)

        # Compute composite score (higher is better)
        composite_score = (
            (semantic_score * 0.45) +
            (keyword_score * 0.25) +
            (title_match_score * 0.15) +
            source_boost +
            intent_boost +
            metadata_boost
        )

        # Apply zero keyword/title overlap penalty
        matched_kw_count = len(expanded_meaningful_query_words.intersection(chunk_words))
        title_word_match = False
        if orig_name:
            clean_name = re.sub(r"[^\w\s]", " ", orig_name)
            name_words = set(clean_name.split())
            if expanded_meaningful_query_words.intersection(name_words):
                title_word_match = True

        if matched_kw_count == 0 and not title_word_match:
            composite_score -= 0.30

        composite_distance = 1.0 - composite_score

        boosted_results.append({
            "doc": doc,
            "raw_score": raw_score,
            "final_score": composite_distance,
            "boost": source_boost + intent_boost + metadata_boost,
            "source": source,
            "method": item["method"],
            "name": (
                doc.metadata.get("filename") or
                doc.metadata.get("name") or
                doc.metadata.get("title") or
                doc.metadata.get("question") or
                "unknown"
            )
        })
    time_boosting = time.time() - start_boosting

    # Sort results by final score ascending (lower distance is better)
    boosted_results.sort(key=lambda x: x["final_score"])

    # Filter out low-ranking chunks (final score distance > 0.65)
    filtered_results = [r for r in boosted_results if r["final_score"] <= 0.65]
    if filtered_results:
        boosted_results = filtered_results
    else:
        # Fallback to keep at least top 1 candidate if available
        boosted_results = boosted_results[:1]

    # 8. Duplicate Chunk Detection & Merging
    unique_results = []
    seen_contents = {}
    for r in boosted_results:
        content_norm = " ".join(r["doc"].page_content.lower().split())
        if content_norm in seen_contents:
            existing = seen_contents[content_norm]
            # Merge tags and categories
            meta_e = existing["doc"].metadata
            meta_c = r["doc"].metadata
            tags_e = set(meta_e.get("tags", [])) if isinstance(meta_e.get("tags"), list) else set()
            tags_c = set(meta_c.get("tags", [])) if isinstance(meta_c.get("tags"), list) else set()
            meta_e["tags"] = list(tags_e.union(tags_c))
            
            p1 = meta_e.get("priority", 3)
            p2 = meta_c.get("priority", 3)
            meta_e["priority"] = min(p1, p2)
            
            existing["raw_score"] = min(existing["raw_score"], r["raw_score"])
            existing["final_score"] = min(existing["final_score"], r["final_score"])
        else:
            seen_contents[content_norm] = r
            unique_results.append(r)
            
    boosted_results = unique_results

    # 9. Cross-Encoder Re-ranking
    # Rerank the top candidates (up to 8) before slicing to k
    top_candidates = [(item["doc"], item["final_score"]) for item in boosted_results[:8]]
    
    t_ce_start = time.time()
    from app.services.rag.reranker import rerank_documents
    reranked_docs = rerank_documents(normalized_query, top_candidates, k=limit_k)
    if debug_store:
        debug_store.cross_encoder_time_ms = (time.time() - t_ce_start) * 1000.0
    
    # Map back to dict representation for remaining steps
    reranked_results = []
    for doc, final_score, ce_raw_score in reranked_docs:
        # Find original result to preserve metadata log attributes
        match = next((item for item in boosted_results if item["doc"] == doc), None)
        if match:
            match["final_score"] = final_score
            match["ce_raw_score"] = ce_raw_score
            reranked_results.append(match)
        else:
            reranked_results.append({
                "doc": doc,
                "raw_score": 0.5,
                "final_score": final_score,
                "ce_raw_score": ce_raw_score,
                "boost": 0.0,
                "source": doc.metadata.get("source", "rag"),
                "method": "reranked",
                "name": doc.metadata.get("filename") or "unknown"
            })
            
    boosted_results = reranked_results

    # 10. Low-Confidence Query Expansion
    if boosted_results and boosted_results[0]["final_score"] > 0.65:
        logger.info(f"Low confidence ({boosted_results[0]['final_score']:.4f}) detected. Performing expanded query retry.")
        try:
            extra_results = vector_store.similarity_search_with_score(
                " ".join(expanded_query_words),
                k=20,
                filter=compiled_filter
            )
            # Re-run candidate processing for extra results and merge
            extra_merged = []
            for doc, score in extra_results:
                if doc.metadata.get("status") == "expired":
                    continue
                # Simple metadata boost calculation
                m_score = calculate_metadata_score(doc.metadata, query_lower, detected_intent=detected_intent)
                sem_score = max(0.0, 1.0 - (score / 1.5))
                comp_score = (sem_score * 0.5) + m_score
                final_dist = 1.0 - comp_score
                
                # Check duplication
                content_norm = " ".join(doc.page_content.lower().split())
                if content_norm not in seen_contents:
                    item_res = {
                        "doc": doc,
                        "raw_score": score,
                        "final_score": final_dist,
                        "boost": m_score,
                        "source": doc.metadata.get("source", "rag"),
                        "method": "expanded_retry",
                        "name": doc.metadata.get("filename") or "unknown"
                    }
                    seen_contents[content_norm] = item_res
                    extra_merged.append((doc, final_dist))
            
            if extra_merged:
                # Rerank with Cross-Encoder and append
                extra_reranked = rerank_documents(query, extra_merged, k=5)
                for doc, score, ce_raw_score in extra_reranked:
                    match_item = seen_contents[" ".join(doc.page_content.lower().split())]
                    match_item["final_score"] = score
                    match_item["ce_raw_score"] = ce_raw_score
                    boosted_results.append(match_item)
                
                # Re-sort
                boosted_results.sort(key=lambda x: x["final_score"])
        except Exception as retry_exc:
            logger.error(f"Query expansion retry failed: {retry_exc}")

    # Final confidence scoring & fallback tagging
    if boosted_results and boosted_results[0]["final_score"] > 0.68:
        # Mark all retrieved documents as low_confidence
        for item in boosted_results:
            item["doc"].metadata["low_confidence"] = True
            
    print("\n--- DEBUG: Sorted Multi-Factor Boosted Results ---")
    for idx, item in enumerate(boosted_results):
         print(f"    {idx+1}: name={item['name']}, source={item['source']}, raw={item['raw_score']:.4f}, final_distance={item['final_score']:.4f}")

    # Merge overlapping adjacent chunks (Task 6) and cap to 2–3 maximum
    target_limit = 3 if reasoning else 2
    selected_results = merge_retrieved_chunks(boosted_results, limit_k=target_limit)

    time_total = time.time() - start_total

    print("\n========== RETRIEVAL PROFILE ==========")
    print(f"Vector Search:   {time_vector:.4f} sec")
    print(f"Chroma Count:    {time_chroma_count:.4f} sec")
    print(f"Cache Sync:      {time_cache_sync:.4f} sec")
    print(f"Keyword Match:   {time_keyword:.4f} sec")
    print(f"Merge:           {time_merge:.4f} sec")
    print(f"Boosting:        {time_boosting:.4f} sec")
    print(f"Total:           {time_total:.4f} sec")
    print("=======================================\n")

    print(f"\n==================================================")
    print(f"RAG RETRIEVAL DEBUG INFO FOR QUERY: '{query}'")
    print(f"   Query Classification: '{query_class}'")
    print(f"   Detected Intent: '{original_intent}' (Overridden: {intent})")
    print(f"   Retrieval Mode: {'Reasoning' if reasoning else 'Factual'}")
    print(f"==================================================")
    for idx, item in enumerate(selected_results):
        print(
            f"Selected Rank {idx+1}: Final Dist = {item['final_score']:.4f} "
            f"[Raw: {item['raw_score']:.4f}, Boost: {item['boost']:.2f}, Method: {item['method']}]"
        )
        print(f"   Source: '{item['source']}' | Name/Title: '{item['name']}'")
    print(f"==================================================\n")

    # Cache the sources in thread-local storage
    _local_retrieval_data.sources = [item["source"] for item in selected_results]
    # Cache the full documents in thread-local storage for response citation post-processing (NEW)
    _local_retrieval_data.documents = [item["doc"] for item in selected_results]

    # Format output as expected list of tuples: (Document, final_score) with ContextString
    formatted_results = []
    for item in selected_results:
        doc = item["doc"]
        wrapped_doc = Document(
            page_content=ContextString(doc.page_content, item["source"]),
            metadata=doc.metadata
        )
        formatted_results.append((wrapped_doc, item["final_score"]))

    if debug_store:
        category_keywords = {
            "placement": ["placement", "placements", "recruitment", "hiring", "ppo", "job", "career", "interview", "salary", "package", "companies", "placement process", "placement cutoff", "recruitment season"],
            "hostel": ["hostel", "hostels", "accommodation", "room", "residence", "mess", "dormitory", "dorms", "dorm", "hostel fee", "hostel rules"],
            "academic": ["exam", "exams", "semester", "midsem", "endsem", "registration", "credits", "cgpa", "course", "syllabus", "academics", "academic calendar"],
            "club": ["club", "clubs", "society", "societies", "student activity", "technical club", "cultural club", "club recruitment"],
            "library": ["library", "libraries", "books", "reading room", "study hall", "book"],
            "transport": ["transport", "bus", "shuttle", "commute", "cycle", "cycle sharing", "parking", "vehicle"],
            "admission": ["admission", "admissions", "apply", "eligibility", "counselling"],
            "scholarship": ["scholarship", "scholarships", "financial aid", "fee waiver", "grant", "grants", "tuition fee waiver"]
        }
        
        def generate_ranking_explanation(item: Dict[str, Any], query_lower: str) -> str:
            reasons = []
            raw_dist = item.get("raw_score", 1.0)
            if raw_dist < 0.4:
                reasons.append("High semantic similarity")
            elif raw_dist < 0.7:
                reasons.append("Moderate semantic similarity")
            else:
                reasons.append("Low semantic similarity")
                
            doc_metadata = item["doc"].metadata
            category = str(doc_metadata.get("category", "")).lower()
            source = str(doc_metadata.get("source", "")).lower()
            
            cat_match = False
            for cat_name, keywords in category_keywords.items():
                if any(kw in query_lower for kw in keywords):
                    if category == cat_name or source == cat_name:
                        cat_match = True
                        break
            if cat_match:
                reasons.append("Category matches query intent")
            else:
                reasons.append("General category / mismatch")
                
            version = doc_metadata.get("version")
            if version and int(version) > 1:
                reasons.append(f"Recent version (v{version})")
            
            priority = doc_metadata.get("priority", 3)
            if priority == 1:
                reasons.append("High priority document")
                
            boost = item.get("boost", 0.0)
            if boost > 0.3:
                reasons.append("Strong metadata boost")
            elif boost < 0.0:
                reasons.append("Penalized for mismatch")
                
            method = item.get("method", "vector")
            if method == "both":
                reasons.append("Matched both semantic and keyword index")
            elif method == "keyword":
                reasons.append("Acronym/keyword index hit")
                
            return ", ".join(reasons)

        selected_docs = [item["doc"] for item in selected_results]
        candidates_list = []
        for idx, item in enumerate(boosted_results[:10]):  # log top 10 candidates
            doc = item["doc"]
            doc_metadata = doc.metadata
            chunk_id = doc_metadata.get("id") or doc_metadata.get("chunk_index")
            if chunk_id is None:
                chunk_id = f"Chunk {idx}"
            else:
                chunk_id = f"Chunk {chunk_id}"
                
            is_selected = any(doc.page_content in s_doc.page_content for s_doc in selected_docs)
                
            c_info = {
                "rank": idx + 1,
                "doc_id": str(doc_metadata.get("id", "N/A")),
                "title": str(doc_metadata.get("filename") or doc_metadata.get("name") or doc_metadata.get("title") or doc_metadata.get("question") or "Untitled"),
                "source_type": str(doc_metadata.get("source", "rag")),
                "category": str(doc_metadata.get("category", "General")),
                "raw_score": float(item.get("raw_score", 1.0)),
                "ce_score": float(item.get("ce_raw_score", 0.0)),
                "combined_score": float(item.get("final_score", 1.0)),
                # Goal 3 improved diagnostics
                "vector_score": float(item.get("raw_score", 1.0)),
                "cross_encoder_score": float(item.get("ce_raw_score", 0.0)),
                "hybrid_score": float(item.get("final_score", 1.0)),
                "retrieval_rank": idx + 1,
                "final_selected": "Yes" if is_selected else "No",
                "chunk_id": str(chunk_id),
                "version": int(doc_metadata.get("version", 1)),
                "explanation": generate_ranking_explanation(item, query.lower())
            }
            candidates_list.append(c_info)
            
        debug_store.candidates = candidates_list
        debug_store.total_retrieval_latency_ms = time_total * 1000.0

    return formatted_results