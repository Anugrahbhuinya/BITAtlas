# backend/app/navigation/routing/services/routing.py

from typing import List, Dict, Optional, Any
from app.navigation.graph.repositories import CampusGraphRepository
from app.navigation.routing.interfaces.strategy import RoutingStrategy
from app.navigation.routing.algorithms.shortest_path import ShortestPathStrategy
from app.navigation.routing.algorithms.fastest_route import FastestRouteStrategy
from app.navigation.routing.algorithms.accessible_route import AccessibleRouteStrategy
from app.navigation.routing.models.route import Route
from app.navigation.routing.repositories.route_cache import RouteCacheRepository
from app.navigation.routing.validators.route_validator import RouteValidator
from app.navigation.routing.services.eta import ETAService
from app.navigation.routing.services.instruction import InstructionService

class RoutingService:
    def __init__(
        self,
        graph_repo: CampusGraphRepository,
        route_cache: RouteCacheRepository,
        eta_service: ETAService,
        instruction_service: InstructionService
    ):
        self.graph_repo = graph_repo
        self.route_cache = route_cache
        self.eta_service = eta_service
        self.instruction_service = instruction_service

        # Strategy lookup
        self._strategies: Dict[str, RoutingStrategy] = {
            "shortest": ShortestPathStrategy(),
            "fastest": FastestRouteStrategy(),
            "accessible": AccessibleRouteStrategy()
        }

    async def calculate_route(
        self,
        start_id: str,
        destination_id: str,
        route_type: str = "shortest"
    ) -> Optional[Route]:
        # Normalize strategy name
        strategy_name = route_type.lower()
        if strategy_name not in self._strategies:
            strategy_name = "shortest"

        # Validate nodes exist
        is_valid, err_msg = await RouteValidator.validate_routing_nodes(
            start_id, destination_id, self.graph_repo
        )
        if not is_valid:
            raise ValueError(err_msg)

        # Check Cache
        cached_route = await self.route_cache.get_route(start_id, destination_id, strategy_name)
        if cached_route:
            return cached_route

        # Execute strategy
        strategy = self._strategies[strategy_name]
        edges = await strategy.find_route(start_id, destination_id, self.graph_repo)

        if edges is None:
            # Graph might be disconnected or destination is unreachable
            return None

        # Build ordered nodes and coordinate path geometry
        ordered_nodes = []
        start_node = await self.graph_repo.get_node(start_id)
        if start_node:
            ordered_nodes.append(start_node)

        geometry_points: List[Any] = []
        current_node_id = start_id

        for edge in edges:
            dest_node = await self.graph_repo.get_node(edge.destination)
            if dest_node:
                ordered_nodes.append(dest_node)

            # Stitch pathway geometry points
            edge_geom = (edge.metadata or {}).get("geometry", [])
            is_forward = (edge.source == current_node_id)
            
            src_node = await self.graph_repo.get_node(edge.source)
            if src_node and dest_node:
                src_coords = [src_node.latitude, src_node.longitude]
                dest_coords = [dest_node.latitude, dest_node.longitude]
                
                if edge_geom:
                    points = [list(pt) for pt in edge_geom]
                    if not is_forward:
                        points.reverse()
                else:
                    points = [src_coords, dest_coords]
                    
                for pt in points:
                    if not geometry_points or geometry_points[-1] != pt:
                        geometry_points.append(pt)
            
            current_node_id = edge.destination if is_forward else edge.source

        # Metrics
        total_distance = sum(edge.distance for edge in edges if edge.distance is not None)
        eta_seconds = self.eta_service.calculate_eta(edges)
        instructions = self.instruction_service.generate_instructions(ordered_nodes, edges)

        # Check accessibility status
        is_accessible = all(edge.accessibility for edge in edges)

        route = Route(
            start_node=start_node,
            destination_node=ordered_nodes[-1] if ordered_nodes else start_node,
            ordered_path=edges,
            ordered_nodes=ordered_nodes,
            total_distance=total_distance,
            estimated_walking_time=eta_seconds,
            navigation_instructions=instructions,
            accessibility_information=is_accessible,
            metadata={"route_type": strategy_name},
            geometry=geometry_points
        )

        # Get OSM destination details from metadata
        destination_node = route.destination_node
        dest_osm_id = destination_node.metadata.get("osm_id") or "N/A"
        dest_osm_type = destination_node.metadata.get("osm_type") or "N/A"
        dest_osm_ref = f"{dest_osm_type}_{dest_osm_id}" if dest_osm_id != "N/A" else "N/A"

        # Find building entrance node ID if routing to a building
        entrance_node_id = "N/A"
        if edges:
            last_edge = edges[-1]
            if last_edge.destination == destination_id:
                entrance_node_id = last_edge.source

        print(f"\n========== NAVIGATION DEBUG ==========")
        print(f"GPS Permission\nGranted")
        print(f"Current Coordinates\n{start_node.latitude:.6f}, {start_node.longitude:.6f}")
        print(f"Nearest OSM Node\n{start_id}")
        print(f"Destination\n{destination_node.name}")
        print(f"Destination OSM Way\n{dest_osm_ref}")
        print(f"Building Entrance\n{entrance_node_id}")
        print(f"Route Found\nTRUE")
        print(f"Distance\n{int(total_distance)} m")
        print(f"ETA\n{int(eta_seconds / 60.0)} min")
        print(f"GPS Tracking\nACTIVE")
        print(f"=====================================\n")

        # Store in cache
        await self.route_cache.set_route(start_id, destination_id, strategy_name, route)
        return route

    async def get_reachable_nodes(self, start_id: str) -> List[str]:
        """
        Runs Breadth-First Search (BFS) to identify all node IDs reachable from start_id.
        """
        start_node = await self.graph_repo.get_node(start_id)
        if not start_node:
            raise ValueError(f"Start location node ID '{start_id}' does not exist.")

        visited = {start_id}
        queue = [start_id]

        while queue:
            node = queue.pop(0)
            neighbors = await self.graph_repo.get_neighbors(node)
            for neighbor_node, _ in neighbors:
                if neighbor_node.id not in visited:
                    visited.add(neighbor_node.id)
                    queue.append(neighbor_node.id)

        return sorted(list(visited))

    async def get_nearby_nodes(self, lat: float, lng: float, radius_meters: float = 200.0) -> List[Any]:
        """
        Finds all graph nodes within a given radius (in meters) from a coordinate point.
        """
        import math
        nodes = await self.graph_repo.get_nodes()
        nearby = []

        for node in nodes:
            # Haversine formula
            R = 6371000.0
            phi1 = math.radians(lat)
            phi2 = math.radians(node.latitude)
            delta_phi = math.radians(node.latitude - lat)
            delta_lambda = math.radians(node.longitude - lng)

            a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            dist = R * c

            if dist <= radius_meters:
                nearby.append(node)

        return nearby
