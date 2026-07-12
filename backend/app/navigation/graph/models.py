# backend/app/navigation/graph/models.py

from enum import Enum
from typing import Dict, Any, Optional

class GraphNodeType(str, Enum):
    BUILDING = "Building"
    ROOM = "Room"
    ENTRANCE = "Entrance"
    LANDMARK = "Landmark"
    FACILITY = "Facility"
    PARKING = "Parking"
    HOSTEL = "Hostel"
    BUS_STOP = "Bus Stop"
    ROAD = "Road"

class GraphEdgeType(str, Enum):
    CONNECTS_TO = "CONNECTS_TO"
    CONTAINS = "CONTAINS"
    ADJACENT_TO = "ADJACENT_TO"
    HAS_ENTRANCE = "HAS_ENTRANCE"
    LOCATED_IN = "LOCATED_IN"
    WALKWAY = "WALKWAY"
    FLOOR_CONNECTION = "FLOOR_CONNECTION"

class CampusNode:
    def __init__(
        self,
        node_id: str,
        node_type: GraphNodeType,
        name: str,
        latitude: float,
        longitude: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = node_id
        self.type = node_type
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value if hasattr(self.type, "value") else self.type,
            "name": self.name,
            "coordinates": {
                "latitude": self.latitude,
                "longitude": self.longitude
            },
            "metadata": self.metadata
        }

class CampusEdge:
    def __init__(
        self,
        source: str,
        destination: str,
        relationship: GraphEdgeType,
        distance: Optional[float] = None,
        accessibility: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.source = source
        self.destination = destination
        self.relationship = relationship
        self.distance = distance
        self.accessibility = accessibility
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "destination": self.destination,
            "relationship": self.relationship.value if hasattr(self.relationship, "value") else self.relationship,
            "distance": self.distance,
            "accessibility": self.accessibility,
            "metadata": self.metadata
        }
