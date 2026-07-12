# backend/app/navigation/schemas.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.navigation.constants import (
    RoomType,
    BuildingCategory,
    LandmarkCategory,
    FacilityCategory,
    PathType,
    SurfaceType,
    LightingLevel
)

# Shared Sub-schemas
class EntranceSchema(BaseModel):
    name: str = Field(..., min_length=1)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

class AccessibilitySchema(BaseModel):
    wheelchair_accessible: bool = True
    has_elevator: Optional[bool] = False
    has_ramp: Optional[bool] = False

class CoordinatesSchema(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

class NodeSchema(BaseModel):
    id: str = Field(..., description="Reference ID or Coordinate key")
    type: str = Field(..., description="building, room, landmark, facility, coordinate")
    name: str = Field(..., description="Node name or label")

# --- Building Schemas ---
class BuildingCreateSchema(BaseModel):
    building_code: str = Field(..., min_length=1, max_length=15)
    building_name: str = Field(..., min_length=2, max_length=100)
    description: str = Field("")
    category: BuildingCategory = Field(default=BuildingCategory.OTHER)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: str = Field("")
    image: Optional[str] = None
    opening_hours: str = Field("09:00 - 17:00")
    contact: str = Field("")
    departments: List[str] = Field(default_factory=list)
    entrances: List[EntranceSchema] = Field(default_factory=list)
    floors: List[int] = Field(default_factory=list)
    accessibility: AccessibilitySchema = Field(default_factory=AccessibilitySchema)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    osm_id: Optional[str] = None
    osm_type: Optional[str] = None
    geometry: Optional[List[List[float]]] = None
    entrance_geometry: Optional[List[float]] = None

class BuildingUpdateSchema(BaseModel):
    building_code: Optional[str] = Field(None, min_length=1, max_length=15)
    building_name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    category: Optional[BuildingCategory] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    address: Optional[str] = None
    image: Optional[str] = None
    opening_hours: Optional[str] = None
    contact: Optional[str] = None
    departments: Optional[List[str]] = None
    entrances: Optional[List[EntranceSchema]] = None
    floors: Optional[List[int]] = None
    accessibility: Optional[AccessibilitySchema] = None
    metadata: Optional[Dict[str, Any]] = None

class BuildingResponseSchema(BuildingCreateSchema):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )

# --- Room Schemas ---
class RoomCreateSchema(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=25)
    room_name: str = Field(..., min_length=1, max_length=100)
    building_id: str = Field(..., description="Building ObjectId reference string")
    floor: int = Field(..., ge=0, le=20)
    department: Optional[str] = None
    room_type: RoomType = Field(..., description="Classroom, Laboratory, Seminar Hall, etc.")
    capacity: int = Field(..., ge=1, le=1000)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    description: str = Field("")
    facilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RoomUpdateSchema(BaseModel):
    room_number: Optional[str] = Field(None, min_length=1, max_length=25)
    room_name: Optional[str] = Field(None, min_length=1, max_length=100)
    building_id: Optional[str] = None
    floor: Optional[int] = Field(None, ge=0, le=20)
    department: Optional[str] = None
    room_type: Optional[RoomType] = None
    capacity: Optional[int] = Field(None, ge=1, le=1000)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    description: Optional[str] = None
    facilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class RoomResponseSchema(RoomCreateSchema):
    id: str = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True
    )

# --- Landmark Schemas ---
class LandmarkCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    coordinates: Optional[CoordinatesSchema] = None
    description: str = Field("")
    category: LandmarkCategory = Field(default=LandmarkCategory.OTHER)
    image: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    osm_id: Optional[str] = None
    osm_type: Optional[str] = None
    geometry: Optional[List[List[float]]] = None
    entrance_geometry: Optional[List[float]] = None

    @field_validator("coordinates", mode="before")
    @classmethod
    def set_coordinates(cls, v, info):
        # Auto populate coordinates from latitude and longitude if not provided
        if not v:
            data = info.data
            lat = data.get("latitude")
            lng = data.get("longitude")
            if lat is not None and lng is not None:
                return CoordinatesSchema(latitude=lat, longitude=lng)
        return v

class LandmarkUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    coordinates: Optional[CoordinatesSchema] = None
    description: Optional[str] = None
    category: Optional[LandmarkCategory] = None
    image: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class LandmarkResponseSchema(LandmarkCreateSchema):
    id: str = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True
    )

# --- Facility Schemas ---
class FacilityCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    coordinates: Optional[CoordinatesSchema] = None
    category: FacilityCategory = Field(default=FacilityCategory.OTHER)
    timing: str = Field("")
    services: List[str] = Field(default_factory=list)
    accessibility: AccessibilitySchema = Field(default_factory=AccessibilitySchema)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    osm_id: Optional[str] = None
    osm_type: Optional[str] = None
    geometry: Optional[List[List[float]]] = None
    entrance_geometry: Optional[List[float]] = None

    @field_validator("coordinates", mode="before")
    @classmethod
    def set_coordinates(cls, v, info):
        if not v:
            data = info.data
            lat = data.get("latitude")
            lng = data.get("longitude")
            if lat is not None and lng is not None:
                return CoordinatesSchema(latitude=lat, longitude=lng)
        return v

class FacilityUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    coordinates: Optional[CoordinatesSchema] = None
    category: Optional[FacilityCategory] = None
    timing: Optional[str] = None
    services: Optional[List[str]] = None
    accessibility: Optional[AccessibilitySchema] = None
    metadata: Optional[Dict[str, Any]] = None

class FacilityResponseSchema(FacilityCreateSchema):
    id: str = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True
    )

# --- Pathway Schemas ---
class PathwayCreateSchema(BaseModel):
    start_node: NodeSchema
    end_node: NodeSchema
    path_type: PathType = Field(default=PathType.WALKWAY)
    distance: float = Field(..., ge=0.1, description="Distance in meters")
    surface: SurfaceType = Field(default=SurfaceType.CONCRETE)
    accessible: bool = True
    lighting: LightingLevel = Field(default=LightingLevel.MODERATE)
    notes: str = Field("")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PathwayUpdateSchema(BaseModel):
    start_node: Optional[NodeSchema] = None
    end_node: Optional[NodeSchema] = None
    path_type: Optional[PathType] = None
    distance: Optional[float] = Field(None, ge=0.1)
    surface: Optional[SurfaceType] = None
    accessible: Optional[bool] = None
    lighting: Optional[LightingLevel] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PathwayResponseSchema(PathwayCreateSchema):
    id: str = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True
    )

# --- Unified Search Result ---
class NavigationSearchResultSchema(BaseModel):
    id: str = Field(..., alias="_id")
    type: str = Field(..., description="building, room, landmark, facility")
    name: str
    description: str
    latitude: float
    longitude: float
    category: str
    snippet: str = Field("", description="A short details string")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    osm_id: Optional[str] = None
    osm_type: Optional[str] = None
    geometry: Optional[List[List[float]]] = None
    entrance_geometry: Optional[List[float]] = None

    model_config = ConfigDict(
        populate_by_name=True
    )
