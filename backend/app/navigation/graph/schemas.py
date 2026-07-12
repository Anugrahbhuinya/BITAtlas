# backend/app/navigation/graph/schemas.py

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CoordinatesSchema(BaseModel):
    latitude: float
    longitude: float

class NodeSchema(BaseModel):
    id: str
    type: str = Field(..., description="Building, Room, Entrance, Landmark, etc.")
    name: str
    coordinates: CoordinatesSchema
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EdgeSchema(BaseModel):
    source: str = Field(..., description="Source node ID")
    destination: str = Field(..., description="Destination node ID")
    relationship: str = Field(..., description="CONNECTS_TO, CONTAINS, etc.")
    distance: Optional[float] = None
    accessibility: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class NeighborSchema(BaseModel):
    node: NodeSchema
    edge: EdgeSchema

class GraphSummarySchema(BaseModel):
    total_nodes: int
    total_edges: int
    node_type_counts: Dict[str, int]
    edge_relationship_counts: Dict[str, int]
    is_valid: bool

class GraphValidationErrorSchema(BaseModel):
    type: str = Field(..., description="orphan, circle, duplicate_edge, duplicate_node, invalid_reference")
    message: str
    severity: str = Field(..., description="ERROR, WARNING")
    details: Dict[str, Any] = Field(default_factory=dict)

class GraphValidationReportSchema(BaseModel):
    is_valid: bool
    errors: List[GraphValidationErrorSchema]
    total_errors: int
    total_warnings: int
