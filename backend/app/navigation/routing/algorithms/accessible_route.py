# backend/app/navigation/routing/algorithms/accessible_route.py

import heapq
from typing import List, Optional, Set, Tuple
from app.navigation.graph.models import CampusEdge
from app.navigation.graph.repositories import CampusGraphRepository
from app.navigation.routing.interfaces.strategy import RoutingStrategy

class AccessibleRouteStrategy(RoutingStrategy):
    async def find_route(
        self,
        start_id: str,
        destination_id: str,
        graph_repo: CampusGraphRepository
    ) -> Optional[List[CampusEdge]]:
        # Priority Queue: (cumulative_distance, current_node_id, list_of_edges)
        pq: List[Tuple[float, str, List[CampusEdge]]] = [(0.0, start_id, [])]
        visited = set()

        while pq:
            dist, current_node, path = heapq.heappop(pq)

            if current_node == destination_id:
                return path

            if current_node in visited:
                continue

            visited.add(current_node)

            neighbors = await graph_repo.get_neighbors(current_node)
            for neighbor_node, edge in neighbors:
                if neighbor_node.id in visited:
                    continue

                # Filter out inaccessible edges
                if not edge.accessibility:
                    continue

                edge_distance = edge.distance if edge.distance is not None else 1.0
                heapq.heappush(pq, (dist + edge_distance, neighbor_node.id, path + [edge]))

        return None
