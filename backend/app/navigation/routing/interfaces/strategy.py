# backend/app/navigation/routing/interfaces/strategy.py

from abc import ABC, abstractmethod
from typing import List, Optional
from app.navigation.graph.models import CampusEdge
from app.navigation.graph.repositories import CampusGraphRepository

class RoutingStrategy(ABC):
    @abstractmethod
    async def find_route(
        self,
        start_id: str,
        destination_id: str,
        graph_repo: CampusGraphRepository
    ) -> Optional[List[CampusEdge]]:
        """
        Finds a path from start to destination node using the graph repository.
        Returns an ordered list of CampusEdge representing the route path,
        or None if no path exists.
        """
        pass
