# backend/app/navigation/routing/services/eta.py

from typing import List
from app.navigation.graph.models import CampusEdge

class ETAService:
    def __init__(self, default_speed: float = 1.34):
        self.default_speed = default_speed

    def calculate_eta(self, edges: List[CampusEdge]) -> float:
        """
        Estimates total walking time in seconds for a list of edges.
        Considers type and surface of pathways.
        """
        total_seconds = 0.0
        for edge in edges:
            dist = edge.distance if edge.distance is not None else 1.0

            # Determine speed based on relationship and metadata
            speed = self.default_speed
            rel = edge.relationship.value if hasattr(edge.relationship, 'value') else str(edge.relationship)

            if rel == "FLOOR_CONNECTION":
                speed = 0.6  # Stairs are slower
            elif rel == "WALKWAY":
                surface = (edge.metadata or {}).get("surface", "concrete")
                if surface == "grass":
                    speed = 1.0
                elif surface == "dirt":
                    speed = 1.1

            total_seconds += dist / speed

        return round(total_seconds, 1)
