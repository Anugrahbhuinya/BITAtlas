import logging
import re
import time
import threading
import os
from typing import List, Tuple, Dict, Any
from langchain_core.documents import Document
from app.services.rag.vector_store import get_vector_store

logger = logging.getLogger("rag_retriever")

# Global cache for documents to optimize keyword/acronym matching speed
_docs_cache: List[Document] = []
_docs_cache_count: int = 0


def detect_intent(query: str) -> str:
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
    def __new__(cls, content: str, source: str):
        instance = super().__new__(cls, content)
        instance.source = source
        return instance


# Thread-local storage to cache the sources from the last retrieve_with_scores run
_local_retrieval_data = threading.local()


def get_last_retrieval_sources() -> List[str]:
    """Retrieve the cached sources of the last retrieve_with_scores execution."""
    return getattr(_local_retrieval_data, "sources", [])


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
                sig_words = {w for w in filename_words if len(w) > 2 and w not in ["pdf", "docx", "doc", "txt"]}
                if sig_words and any(re.search(r"\b" + re.escape(w) + r"\b", query_lower) for w in sig_words):
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


def retrieve_with_scores(
    query: str,
    k: int = 5
) -> List[Tuple[Document, float]]:
    global _docs_cache, _docs_cache_count

    start_total = time.time()
    vector_store = get_vector_store()

    query_lower = query.lower()
    
    # 1. Synchronize all documents cache from Chroma for keyword matching and classification
    # Set limit=10000 to prevent pagination limits from truncating newly indexed files
    start_chroma_count = time.time()
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
    except Exception as e:
        logger.error(f"Error fetching documents from ChromaDB: {e}")
        _docs_cache = []
        _docs_cache_count = 0
    time_cache_sync = time.time() - start_cache_sync

    # 2. Classify Query Intent
    query_class = classify_query(query, _docs_cache)
    is_doc_query = (query_class in ["document", "mixed"])
    
    # 3. Detect Intent & reasoning mode
    intent = detect_intent(query)
    reasoning = is_reasoning_query(query)
    
    original_intent = intent
    if reasoning:
        intent = None
        k_vector = 20
        limit_k = 7
    else:
        k_vector = 10
        limit_k = 3

    # 4. Vector Search (with high recall across the entire collection)
    start_vector = time.time()
    vector_results = []

    logger.info("Performing global semantic search across the entire Chroma collection.")
    try:
        vector_results = vector_store.similarity_search_with_score(
            query,
            k=k_vector
        )
    except Exception as e:
        logger.error(f"Global semantic search failed: {e}")
        vector_results = []

    # Supplemental search for document-targeted queries to guarantee recall of dynamic document chunks
    if is_doc_query:
        print(f"\n--- DEBUG: Detected dynamic doc query ({query_class}). Supplementing... ---")
        try:
            dynamic_results = vector_store.similarity_search_with_score(
                query,
                k=k_vector,
                filter={"source": "kb_document"}
            )
            print(f"--- DEBUG: Found {len(dynamic_results)} dynamic chunks in Chroma ---")
            vector_results.extend(dynamic_results)
        except Exception as e:
            print(f"--- DEBUG: Exception in supplemental search: {e} ---")
            logger.error(f"Failed to supplement search with dynamic documents: {e}")
        
    time_vector = time.time() - start_vector

    # 5. Heuristic / Acronym matching
    start_keyword = time.time()
    query_clean = re.sub(r'[^\w\s]', ' ', query_lower)
    query_words = set(query_clean.split())

    # Meaningful words to look for (exclude search templates and stop words)
    stop_words = {
        "department", "club", "building", "facility", "hostel", "where", "is",
        "of", "and", "in", "to", "for", "the", "a", "an", "which", "offers",
        "about", "tell", "me", "show", "get", "what", "are", "available",
        "student", "students", "bit", "mesra"
    }
    meaningful_query_words = query_words - stop_words

    # Exclude common small words and pronouns from being matched as acronyms (e.g. "me" matching ME)
    invalid_acronyms = {
        "me", "an", "is", "it", "at", "in", "to", "by", "on", "or", "of", "no",
        "so", "he", "we", "us", "go", "do", "my", "as", "if"
    }

    keyword_candidates: List[Tuple[Document, float]] = []
    for doc in _docs_cache:
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

        # Check for acronym match (e.g. query contains "aiml", acronym of name is "aiml")
        acronym = get_acronym(orig_name)
        if acronym and len(acronym) >= 2 and acronym in query_words and acronym not in invalid_acronyms:
            boost_base = 0.20

        # Check for unique/meaningful word matches
        name_clean = re.sub(r'[^\w\s]', ' ', name_lower)
        name_words = set(name_clean.split())
        common_words = meaningful_query_words.intersection(name_words)
        if common_words:
            boost_base = 0.30

        if boost_base is not None:
            keyword_candidates.append((doc, boost_base))
    time_keyword = time.time() - start_keyword

    # 6. Merge Vector and Keyword Candidates
    start_merge = time.time()
    merged_candidates: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for doc, score in vector_results:
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
        # raw_score is L2 distance, typically in [0.0, 1.5]
        semantic_score = max(0.0, 1.0 - (raw_score / 1.5))
        if item["method"] == "keyword":
            # Keyword candidates don't have vector search distances, set base similarity
            semantic_score = 0.50

        # B. Keyword Overlap Score
        chunk_clean = re.sub(r'[^\w\s]', ' ', doc_content_lower)
        chunk_words = set(chunk_clean.split())
        matched_kw_count = len(meaningful_query_words.intersection(chunk_words))
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
            matched_title_kws = meaningful_query_words.intersection(name_words)
            if matched_title_kws:
                title_match_score = len(matched_title_kws) / max(1, len(name_words))
                # Extra boost if it matches specific filename keywords from query
                title_match_score = min(1.0, title_match_score + 0.2)

        # D. Source Boost & Intent Alignment
        source_boost = 0.0
        intent_boost = 0.0

        # Apply classification-aware boosts
        if query_class == "document":
            if source == "kb_document":
                source_boost = 0.50
            else:
                source_boost = -0.20  # Penalty for non-docs
        elif query_class == "campus":
            if source != "kb_document":
                source_boost = 0.30
            else:
                source_boost = -0.20  # Penalty for documents
        elif query_class == "mixed":
            # Both are relevant, slight preference for documents
            if source == "kb_document":
                source_boost = 0.30
            else:
                source_boost = 0.15

        # Query content intent matching
        if any(kw in query_lower for kw in facility_keywords) and source == "facility":
            intent_boost = 0.15
        elif any(kw in query_lower for kw in dept_keywords) and source == "department":
            intent_boost = 0.15
        elif any(kw in query_lower for kw in club_keywords) and source == "club":
            intent_boost = 0.15
        elif any(kw in query_lower for kw in building_keywords) and source == "building":
            intent_boost = 0.15

        # Compute multi-factor composite score (higher is better)
        composite_score = (
            (semantic_score * 0.45) +
            (keyword_score * 0.20) +
            (title_match_score * 0.15) +
            source_boost +
            intent_boost
        )

        # Convert back to composite_distance (lower is better) for backward compatibility
        composite_distance = 1.0 - composite_score

        boosted_results.append({
            "doc": doc,
            "raw_score": raw_score,
            "final_score": composite_distance,
            "boost": source_boost + intent_boost,
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

    # Sort results by final score ascending (lower distance/composite_distance is better)
    boosted_results.sort(key=lambda x: x["final_score"])

    print("\n--- DEBUG: Sorted Multi-Factor Boosted Results ---")
    for idx, item in enumerate(boosted_results):
         print(f"    {idx+1}: name={item['name']}, source={item['source']}, raw={item['raw_score']:.4f}, final_distance={item['final_score']:.4f}")

    # Source Diversity / Top K context builder preferences
    selected_results = []
    source_counts = {}
    
    # Context builder prioritization:
    # If this is a document query, prioritize kb_document chunks
    if query_class == "document":
        doc_chunks = [item for item in boosted_results if item["source"] == "kb_document"]
        other_chunks = [item for item in boosted_results if item["source"] != "kb_document"]
        # Arrange to place dynamic document chunks at the absolute top of the ranking
        boosted_results = doc_chunks + other_chunks
    
    for item in boosted_results:
        source = item.get("source", "unknown")
        # For reasoning queries, enforce source diversity limits
        if reasoning:
            count = source_counts.get(source, 0)
            if count >= 4:
                continue
            source_counts[source] = count + 1
        
        selected_results.append(item)
        if len(selected_results) >= limit_k:
            break

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

    # Format output as expected list of tuples: (Document, final_score) with ContextString
    formatted_results = []
    for item in selected_results:
        doc = item["doc"]
        wrapped_doc = Document(
            page_content=ContextString(doc.page_content, item["source"]),
            metadata=doc.metadata
        )
        formatted_results.append((wrapped_doc, item["final_score"]))
    return formatted_results