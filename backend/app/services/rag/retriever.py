import logging
import re
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


def retrieve_with_scores(
    query: str,
    k: int = 5
) -> List[Tuple[Document, float]]:
    global _docs_cache, _docs_cache_count

    vector_store = get_vector_store()

    # 1. Detect Intent before retrieval
    intent = detect_intent(query)

    # 2. Vector Search (with high recall and optional metadata filter)
    k_vector = max(20, k * 2)
    vector_results = []

    if intent:
        logger.info(f"Detected intent: '{intent}'. Performing filtered search.")
        try:
            vector_results = vector_store.similarity_search_with_score(
                query,
                k=k_vector,
                filter={"source": intent}
            )
        except Exception as e:
            logger.error(f"Filtered search failed: {e}")
            vector_results = []

        # Fallback: if no results found in filtered search, run global search
        if not vector_results:
            logger.info("Filtered search returned no results. Falling back to global search.")
            vector_results = vector_store.similarity_search_with_score(
                query,
                k=k_vector
            )
    else:
        logger.info("No specific intent detected. Performing global search.")
        vector_results = vector_store.similarity_search_with_score(
            query,
            k=k_vector
        )

    # 3. Synchronize all documents cache from Chroma for keyword matching
    try:
        current_count = vector_store._collection.count()
        if not _docs_cache or current_count != _docs_cache_count:
            all_chroma = vector_store.get()
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

    # 4. Heuristic / Acronym matching
    query_lower = query.lower()
    query_clean = re.sub(r'[^\w\s]', ' ', query_lower)
    query_words = set(query_clean.split())

    # Meaningful words to look for (exclude search templates and stop words)
    stop_words = {
        "department", "club", "building", "facility", "hostel", "where", "is",
        "of", "and", "in", "to", "for", "the", "a", "an", "which", "offers",
        "about", "tell", "me", "show", "get", "what", "are", "available"
    }
    meaningful_query_words = query_words - stop_words

    # Exclude common small words and pronouns from being matched as acronyms (e.g. "me" matching ME)
    invalid_acronyms = {
        "me", "an", "is", "it", "at", "in", "to", "by", "on", "or", "of", "no",
        "so", "he", "we", "us", "go", "do", "my", "as", "if"
    }

    keyword_candidates: List[Tuple[Document, float]] = []
    for doc in _docs_cache:
        # If intent is detected, only consider documents of the intended source!
        doc_source = doc.metadata.get("source", "")
        if intent and doc_source != intent:
            continue

        orig_name = (
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
        if acronym and acronym in query_words and acronym not in invalid_acronyms:
            # Acronym match: Set a high similarity score (low distance)
            boost_base = 0.20

        # Check for unique/meaningful word matches
        name_clean = re.sub(r'[^\w\s]', ' ', name_lower)
        name_words = set(name_clean.split())
        common_words = meaningful_query_words.intersection(name_words)
        if common_words:
            # Word overlap match: Set a high similarity score (low distance)
            boost_base = 0.30

        if boost_base is not None:
            keyword_candidates.append((doc, boost_base))

    # 5. Merge Vector and Keyword Candidates
    # Deduplicate based on (page_content, source)
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

    # 6. Apply Source-Aware Boosting (Metadata-driven preference)
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
        score = item["score"]
        source = doc.metadata.get("source", "")

        # Determine source boost based on query contents
        source_boost = 0.0
        if any(kw in query_lower for kw in facility_keywords) and source == "facility":
            source_boost = 0.15
        elif any(kw in query_lower for kw in dept_keywords) and source == "department":
            source_boost = 0.15
        elif any(kw in query_lower for kw in club_keywords) and source == "club":
            source_boost = 0.15
        elif any(kw in query_lower for kw in building_keywords) and source == "building":
            source_boost = 0.15

        final_score = score - source_boost

        boosted_results.append({
            "doc": doc,
            "raw_score": score,
            "final_score": final_score,
            "boost": source_boost,
            "source": source,
            "method": item["method"],
            "name": (
                doc.metadata.get("name") or
                doc.metadata.get("title") or
                doc.metadata.get("question")
            )
        })

    # Sort results by final score ascending (lower distance is better)
    boosted_results.sort(key=lambda x: x["final_score"])

    # 7. Debug / Print Retrieved Documents and Scores
    print(f"\n==================================================")
    print(f"RAG RETRIEVAL DEBUG INFO FOR QUERY: '{query}'")
    print(f"   Detected Intent Filter: '{intent}'")
    print(f"==================================================")
    for idx, item in enumerate(boosted_results[:10]):
        print(
            f"Rank {idx+1}: Final Score = {item['final_score']:.4f} "
            f"[Raw: {item['raw_score']:.4f}, Boost: {item['boost']:.2f}, Method: {item['method']}]"
        )
        print(f"   Source: '{item['source']}' | Name/Title: '{item['name']}'")
    print(f"==================================================\n")

    # Format output as expected list of tuples: (Document, final_score)
    return [(item["doc"], item["final_score"]) for item in boosted_results[:k]]