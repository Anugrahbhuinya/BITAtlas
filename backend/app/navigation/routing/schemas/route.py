# backend/app/navigation/routing/schemas/route.py

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.navigation.graph.schemas import NodeSchema, EdgeSchema

class RouteResponseSchema(BaseModel):
    start_node: NodeSchema
    destination_node: NodeSchema
    ordered_path: List[EdgeSchema]
    ordered_nodes: List[NodeSchema]
    geometry: List[List[float]] = Field(default_factory=list, description="High-fidelity route polyline coordinates")
    total_distance: float = Field(..., description="Total route distance in meters")
    estimated_walking_time: float = Field(..., description="Walking duration in seconds")
    total_nodes: int
    navigation_instructions: List[str]
    accessibility_information: bool
    alternative_routes: List[Any] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ETAResponseSchema(BaseModel):
    start_id: str
    destination_id: str
    distance_meters: float
    estimated_seconds: float
    accessible: bool

class ReachableResponseSchema(BaseModel):
    start_id: str
    reachable_node_ids: List[str]
    total_reachable: int

class NearbyResponseSchema(BaseModel):
    center_latitude: float
    center_longitude: float
    radius_meters: float
    nearby_nodes: List[NodeSchema]
