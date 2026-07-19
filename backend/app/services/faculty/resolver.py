import logging
import re
from typing import Dict, Any, List, Optional
from app.services.faculty.constants import THRESHOLD_HIGH, THRESHOLD_MEDIUM, THRESHOLD_LOW, TIE_BREAK_DELTA
from app.services.faculty.normalizer import normalize_name
from app.services.faculty.fuzzy_matcher import FacultyFuzzyMatcher

logger = logging.getLogger("faculty_resolver")

class FacultyNameResolver:
    _matcher: Optional[FacultyFuzzyMatcher] = None

    @classmethod
    def initialize(cls, faculty_list: List[Dict[str, Any]]):
        """
        Initializes the fuzzy matcher with the faculty list.
        """
        cls._matcher = FacultyFuzzyMatcher(faculty_list)

    @classmethod
    def get_matcher(cls) -> FacultyFuzzyMatcher:
        """
        Gets or initializes the singleton fuzzy matcher.
        """
        if cls._matcher is None:
            from app.services.faculty_service import FacultyService
            cls.initialize(FacultyService.get_all())
        return cls._matcher

    @classmethod
    def resolve(cls, query: str, dept_filter: Optional[str] = None, dept_acronym_matched: Optional[str] = None) -> Dict[str, Any]:
        """
        Resolves a user query to one or more faculty candidates.
        Returns a dict with:
        - status: 'exact_single', 'exact_multiple', 'fuzzy_single_high', 'fuzzy_single_medium', 'fuzzy_multiple', 'no_match'
        - candidates: List[Dict[str, Any]]
        - message: Optional clarification message
        """
        clean_query = query.strip()
        if not clean_query:
            return {
                "status": "no_match",
                "candidates": [],
                "message": "I couldn't find any faculty member matching your request."
            }

        # 1. Exact Match / Substring Match Check
        from app.services.faculty_service import FacultyService
        exact_matches = []

        stop_words = {
            "who", "teaches", "teaching", "is", "the", "of", "in", "on", 
            "interested", "working", "faculty", "professor", "prof", "dr", 
            "show", "give", "me", "find", "email", "phone", "number", "contact", 
            "xyz", "abc", "about", "list", "members", "member", "department", 
            "works", "here", "are", "look", "for", "search", "details", "info", 
            "information", "please", "can", "you", "tell", "get", "address", 
            "office", "hours", "website", "designation"
        }
        query_clean_str = re.sub(r"[^\w\s]", " ", query)
        query_words = [w.lower() for w in query_clean_str.split() if w.lower() not in stop_words]
        search_query = " ".join(query_words).strip()

        # Synonym expansion for research interests
        expanded_words = list(query_words)
        for word in query_words:
            if word == "ai":
                expanded_words.extend(["artificial", "intelligence"])
            elif word == "ml":
                expanded_words.extend(["machine", "learning"])
            elif word == "nlp":
                expanded_words.extend(["natural", "language", "processing"])
            elif word == "cv":
                expanded_words.extend(["computer", "vision"])
            elif word == "dl":
                expanded_words.extend(["deep", "learning"])
            elif word == "iot":
                expanded_words.extend(["internet", "of", "things"])

        if dept_filter:
            # Replicate department filter logic
            matching_faculty = FacultyService.search(dept_filter)
            other_words = [
                w for w in expanded_words 
                if w not in dept_filter.lower() 
                and w != dept_acronym_matched 
                and w not in ["computer", "science", "engineering", "electronics", "electrical"]
            ]
            if other_words:
                filtered = []
                for member in matching_faculty:
                    match_found = False
                    for word in other_words:
                        interests_lower = [i.lower() for i in member.get("research_interests", [])]
                        if (word in member.get("name", "").lower() or
                            (member.get("designation") and word in member.get("designation", "").lower()) or
                            any(word in interest for interest in interests_lower)):
                            match_found = True
                            break
                    if match_found:
                        filtered.append(member)
                matching_faculty = filtered
            exact_matches = matching_faculty
        else:
            # Expand acronyms for search
            search_terms = [search_query] if search_query else [query]
            if search_query.lower() == "nlp":
                search_terms.append("natural language processing")
            elif search_query.lower() == "ai":
                search_terms.append("artificial intelligence")
            elif search_query.lower() == "ml":
                search_terms.append("machine learning")
            elif search_query.lower() == "cv":
                search_terms.append("computer vision")
            elif search_query.lower() == "dl":
                search_terms.append("deep learning")
            elif search_query.lower() == "iot":
                search_terms.append("internet of things")
                
            seen_ids = set()
            for term in search_terms:
                results = FacultyService.search(term)
                for r in results:
                    if r["id"] not in seen_ids:
                        exact_matches.append(r)
                        seen_ids.add(r["id"])

        if exact_matches:
            # If it's a department query or research interest query, return all of them
            if dept_filter or not search_query:
                return {
                    "status": "exact_multiple" if len(exact_matches) > 1 else "exact_single",
                    "candidates": exact_matches,
                    "message": None
                }

            # Check if matching results are name-based (meaning the search query matches the name)
            norm_q = normalize_name(query)
            name_matches = []
            for m in exact_matches:
                norm_name = normalize_name(m.get("name", ""))
                if norm_q in norm_name or any(t in norm_name for t in norm_q.split()):
                    name_matches.append(m)

            # If we matched names specifically and there are multiple, prompt for clarification
            if len(name_matches) > 1:
                return {
                    "status": "exact_multiple",
                    "candidates": name_matches,
                    "message": f"I found multiple faculty members matching '{clean_query}'. Which one did you mean?"
                }
            elif len(name_matches) == 1:
                return {
                    "status": "exact_single",
                    "candidates": name_matches,
                    "message": None
                }
            else:
                # If they matched other fields, return all of them
                return {
                    "status": "exact_multiple" if len(exact_matches) > 1 else "exact_single",
                    "candidates": exact_matches,
                    "message": None
                }

        # 2. Fuzzy Match Fallback
        # Use the stop-word-filtered search_query for cleaner name matching
        fuzzy_q = normalize_name(search_query) if search_query else normalize_name(query)
        if not fuzzy_q:
            return {
                "status": "no_match",
                "candidates": [],
                "message": "I couldn't find any faculty member matching your request."
            }

        matcher = cls.get_matcher()
        matches = matcher.find_matches(fuzzy_q)
        if not matches:
            return {
                "status": "no_match",
                "candidates": [],
                "message": "I couldn't find any faculty member matching your request."
            }

        # Sort matches by score descending
        matches.sort(key=lambda x: x.score, reverse=True)
        best_match = matches[0]
        best_score = best_match.score

        logger.info(f"Fuzzy resolution top candidate: '{best_match.faculty.get('name')}' with score: {best_score}")

        # Discard Low Confidence matches immediately (best_score < THRESHOLD_MEDIUM)
        if best_score < THRESHOLD_MEDIUM:
            return {
                "status": "no_match",
                "candidates": [],
                "message": "I couldn't find any faculty member matching your request."
            }

        # Check for ties or candidates within TIE_BREAK_DELTA of the best score
        tied_candidates = []
        for m in matches:
            if abs(m.score - best_score) <= TIE_BREAK_DELTA:
                tied_candidates.append(m.faculty)
            else:
                break

        if len(tied_candidates) > 1:
            return {
                "status": "fuzzy_multiple",
                "candidates": tied_candidates,
                "message": f"I found multiple faculty members matching '{clean_query}'. Which one did you mean?"
            }

        # Single best candidate evaluation
        if best_score >= THRESHOLD_HIGH:
            return {
                "status": "fuzzy_single_high",
                "candidates": [best_match.faculty],
                "message": None
            }
        else:
            # Since it's >= THRESHOLD_MEDIUM and < THRESHOLD_HIGH, it's Medium confidence
            suggested_name = best_match.faculty.get("name", "")
            return {
                "status": "fuzzy_single_medium",
                "candidates": [best_match.faculty],
                "message": f"Did you mean Dr. {suggested_name}?"
            }
