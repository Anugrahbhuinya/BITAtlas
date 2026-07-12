# backend/app/navigation/models.py

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from bson import ObjectId

class BuildingModel:
    def __init__(
        self,
        building_code: str,
        building_name: str,
        description: str,
        category: str,
        latitude: float,
        longitude: float,
        address: str,
        opening_hours: str,
        contact: str,
        departments: List[str],
        entrances: List[Dict[str, Any]],
        floors: List[int],
        accessibility: Dict[str, Any],
        image: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.building_code = building_code
        self.building_name = building_name
        self.description = description
        self.category = category
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.image = image
        self.opening_hours = opening_hours
        self.contact = contact
        self.departments = departments
        self.entrances = entrances
        self.floors = floors
        self.accessibility = accessibility
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "building_code": self.building_code,
            "building_name": self.building_name,
            "description": self.description,
            "category": self.category,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "image": self.image,
            "opening_hours": self.opening_hours,
            "contact": self.contact,
            "departments": self.departments,
            "entrances": self.entrances,
            "floors": self.floors,
            "accessibility": self.accessibility,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class RoomModel:
    def __init__(
        self,
        room_number: str,
        room_name: str,
        building_id: str,
        floor: int,
        room_type: str,
        capacity: int,
        description: str,
        facilities: List[str],
        department: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.room_number = room_number
        self.room_name = room_name
        self.building_id = building_id
        self.floor = floor
        self.department = department
        self.room_type = room_type
        self.capacity = capacity
        self.latitude = latitude
        self.longitude = longitude
        self.description = description
        self.facilities = facilities
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_number": self.room_number,
            "room_name": self.room_name,
            "building_id": self.building_id,
            "floor": self.floor,
            "department": self.department,
            "room_type": self.room_type,
            "capacity": self.capacity,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "description": self.description,
            "facilities": self.facilities,
            "metadata": self.metadata
        }

class LandmarkModel:
    def __init__(
        self,
        name: str,
        latitude: float,
        longitude: float,
        description: str,
        category: str,
        image: Optional[str] = None,
        coordinates: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.description = description
        self.category = category
        self.image = image
        self.coordinates = coordinates or {"latitude": latitude, "longitude": longitude}
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "coordinates": self.coordinates,
            "description": self.description,
            "category": self.category,
            "image": self.image,
            "metadata": self.metadata
        }

class FacilityModel:
    def __init__(
        self,
        name: str,
        latitude: float,
        longitude: float,
        category: str,
        timing: str,
        services: List[str],
        accessibility: Dict[str, Any],
        coordinates: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.category = category
        self.timing = timing
        self.services = services
        self.accessibility = accessibility
        self.coordinates = coordinates or {"latitude": latitude, "longitude": longitude}
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "coordinates": self.coordinates,
            "category": self.category,
            "timing": self.timing,
            "services": self.services,
            "accessibility": self.accessibility,
            "metadata": self.metadata
        }

class PathwayModel:
    def __init__(
        self,
        start_node: Dict[str, Any],
        end_node: Dict[str, Any],
        path_type: str,
        distance: float,
        surface: str,
        accessible: bool,
        lighting: str,
        notes: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.start_node = start_node
        self.end_node = end_node
        self.path_type = path_type
        self.distance = distance
        self.surface = surface
        self.accessible = accessible
        self.lighting = lighting
        self.notes = notes
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_node": self.start_node,
            "end_node": self.end_node,
            "path_type": self.path_type,
            "distance": self.distance,
            "surface": self.surface,
            "accessible": self.accessible,
            "lighting": self.lighting,
            "notes": self.notes,
            "metadata": self.metadata
        }
