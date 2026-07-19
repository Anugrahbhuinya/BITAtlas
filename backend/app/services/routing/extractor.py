import re
from typing import Optional, Dict, Any
from app.services.routing.constants import DESCRIPTIVE_KEYWORDS, STRUCTURED_KEYWORDS

class FacultyQueryExtractor:
    @staticmethod
    def extract_entity(query: str) -> Optional[Dict[str, Any]]:
        """
        Extracts the discussed faculty member entity from the query.
        Uses the typo-tolerant FacultyNameResolver.
        """
        from app.services.faculty.resolver import FacultyNameResolver
        try:
            resolution = FacultyNameResolver.resolve(query)
            if resolution["status"] in ["exact_single", "fuzzy_single_high", "fuzzy_single_medium"]:
                return resolution["candidates"][0]
            elif resolution["status"] in ["exact_multiple", "fuzzy_multiple"]:
                return resolution["candidates"][0]
        except Exception:
            pass
        return None

    @staticmethod
    def extract_attribute(query: str) -> str:
        """
        Determines the attribute being asked in the query (descriptive vs. structured).
        Returns "descriptive", "structured", or "unknown".
        """
        q_lower = query.lower()
        
        # Check descriptive keywords (allowing optional plural 's')
        for kw in DESCRIPTIVE_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"s?\b", q_lower):
                return "descriptive"
        
        # Check structured keywords (allowing optional plural 's')
        for kw in STRUCTURED_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"s?\b", q_lower):
                return "structured"
                
        return "unknown"
