# backend/app/navigation/routing/models/route.py

from typing import List, Dict, Any, Optional
from app.navigation.graph.models import CampusNode, CampusEdge

class Route:
    def __init__(
        self,
        start_node: CampusNode,
        destination_node: CampusNode,
        ordered_path: List[CampusEdge],
        ordered_nodes: List[CampusNode],
        total_distance: float,
        estimated_walking_time: float,
        navigation_instructions: List[str],
        accessibility_information: bool,
        alternative_routes: Optional[List[Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        geometry: Optional[List[List[float]]] = None
    ):
        self.start_node = start_node
        self.destination_node = destination_node
        self.ordered_path = ordered_path
        self.ordered_nodes = ordered_nodes
        self.total_distance = total_distance
        self.estimated_walking_time = estimated_walking_time
        self.navigation_instructions = navigation_instructions
        self.accessibility_information = accessibility_information
        self.alternative_routes = alternative_routes or []
        self.metadata = metadata or {}
        self.geometry = geometry or []
