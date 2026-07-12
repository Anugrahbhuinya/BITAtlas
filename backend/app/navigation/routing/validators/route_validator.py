# backend/app/navigation/routing/validators/route_validator.py

from typing import Optional, Tuple
from app.navigation.graph.repositories import CampusGraphRepository

class RouteValidator:
    @staticmethod
    async def validate_routing_nodes(
        start_id: str,
        destination_id: str,
        graph_repo: CampusGraphRepository
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates if start and destination nodes exist in the graph repository.
        Returns a tuple of (is_valid, error_message).
        """
        start_node = await graph_repo.get_node(start_id)
        if not start_node:
            return False, f"Start location node ID '{start_id}' does not exist in the campus graph."

        dest_node = await graph_repo.get_node(destination_id)
        if not dest_node:
            return False, f"Destination location node ID '{destination_id}' does not exist in the campus graph."

        if start_id == destination_id:
            return False, "Start location and destination location cannot be the same."

        return True, None
