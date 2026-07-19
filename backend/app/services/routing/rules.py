from typing import List
from app.services.routing.constants import FACULTY_DIRECTORY, WEBSITE_KNOWLEDGE_BASE

class RoutingRules:
    @staticmethod
    def get_datasource_priority(attribute_type: str) -> List[str]:
        """
        Returns the priority list of datasources based on the requested attribute type.
        """
        if attribute_type == "structured":
            return [FACULTY_DIRECTORY, WEBSITE_KNOWLEDGE_BASE]
        elif attribute_type == "descriptive":
            return [WEBSITE_KNOWLEDGE_BASE, FACULTY_DIRECTORY]
        else:
            # For general or unknown attribute queries (e.g. "who is Dr. X"),
            # default to structured profile card from Faculty Directory first,
            # then fallback to the Website Knowledge Base.
            return [FACULTY_DIRECTORY, WEBSITE_KNOWLEDGE_BASE]
