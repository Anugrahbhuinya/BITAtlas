# backend/app/navigation/routing/algorithms/fastest_route.py

import heapq
from typing import List, Optional, Set, Tuple
from app.navigation.graph.models import CampusEdge
from app.navigation.graph.repositories import CampusGraphRepository
from app.navigation.routing.interfaces.strategy import RoutingStrategy

class FastestRouteStrategy(RoutingStrategy):
    async def find_route(
        self,
        start_id: str,
        destination_id: str,
        graph_repo: CampusGraphRepository
    ) -> Optional[List[CampusEdge]]:
        # Priority Queue: (cumulative_time_seconds, current_node_id, list_of_edges)
        pq: List[Tuple[float, str, List[CampusEdge]]] = [(0.0, start_id, [])]
        visited = set()

        while pq:
            time_taken, current_node, path = heapq.heappop(pq)

            if current_node == destination_id:
                return path

            if current_node in visited:
                continue

            visited.add(current_node)

            neighbors = await graph_repo.get_neighbors(current_node)
            for neighbor_node, edge in neighbors:
                if neighbor_node.id in visited:
                    continue

                # Determine walking speed based on edge relationship & surface
                speed = 1.34  # Default standard walking speed (m/s)
                
                rel = edge.relationship.value if hasattr(edge.relationship, 'value') else str(edge.relationship)
                if rel == "FLOOR_CONNECTION":
                    speed = 0.6  # Staircases are slower
                elif rel == "WALKWAY":
                    surface = (edge.metadata or {}).get("surface", "concrete")
                    if surface == "grass":
                        speed = 1.0
                    elif surface == "dirt":
                        speed = 1.1

                edge_distance = edge.distance if edge.distance is not None else 1.0
                travel_time = edge_distance / speed
                
                heapq.heappush(pq, (time_taken + travel_time, neighbor_node.id, path + [edge]))

        return None
