import logging
from typing import List, Dict, Any
from rapidfuzz import fuzz
from app.services.faculty.normalizer import normalize_name
from app.services.faculty.models import ResolvedFaculty

logger = logging.getLogger("faculty_fuzzy_matcher")

class FacultyFuzzyMatcher:
    def __init__(self, faculty_list: List[Dict[str, Any]]):
        """
        Pre-calculates and caches normalized faculty names.
        """
        self.normalized_faculty = []
        for member in faculty_list:
            if not member or not member.get("name"):
                continue
            norm_name = normalize_name(member["name"])
            self.normalized_faculty.append({
                "faculty": member,
                "normalized_name": norm_name
            })
        logger.info(f"Initialized FacultyFuzzyMatcher with {len(self.normalized_faculty)} normalized faculty entries.")

    def find_matches(self, normalized_query: str) -> List[ResolvedFaculty]:
        """
        Computes WRatio similarity score against all normalized cached names.
        """
        results = []
        for entry in self.normalized_faculty:
            # Calculate token-aware similarity score
            score = fuzz.WRatio(normalized_query, entry["normalized_name"])
            results.append(ResolvedFaculty(
                faculty=entry["faculty"],
                score=score,
                normalized_name=entry["normalized_name"]
            ))
        return results
