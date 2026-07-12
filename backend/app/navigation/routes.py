# backend/app/navigation/routes.py

from fastapi import APIRouter, Depends, status, Query
from typing import List, Dict, Any, Optional

# Security & Middleware
from app.middleware.auth import (
    require_authenticated,
    get_current_admin_user
)

# Schemas
from app.navigation.schemas import (
    BuildingCreateSchema, BuildingUpdateSchema, BuildingResponseSchema,
    RoomCreateSchema, RoomUpdateSchema, RoomResponseSchema,
    LandmarkCreateSchema, LandmarkUpdateSchema, LandmarkResponseSchema,
    FacilityCreateSchema, FacilityUpdateSchema, FacilityResponseSchema,
    PathwayCreateSchema, PathwayUpdateSchema, PathwayResponseSchema,
    NavigationSearchResultSchema
)

# Dependencies
from app.navigation.dependencies import (
    get_building_service,
    get_room_service,
    get_landmark_service,
    get_facility_service,
    get_pathway_service,
    get_nav_search_service
)
from app.navigation.services import (
    BuildingService,
    RoomService,
    LandmarkService,
    FacilityService,
    PathwayService,
    NavigationSearchService
)
from app.navigation.graph.routes import router as graph_router
from app.navigation.routing.routes import router as routing_router

router = APIRouter(prefix="/api/navigation", tags=["navigation"])
router.include_router(graph_router, prefix="/graph", tags=["navigation-graph"])
router.include_router(routing_router, prefix="/route", tags=["navigation-routing"])

# --- BUILDINGS ENDPOINTS ---

@router.get("/buildings", response_model=Dict[str, Any])
async def list_buildings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: BuildingService = Depends(get_building_service)
):
    """Lists/paginates buildings on campus. Read-only for authenticated students and admins."""
    return await service.list_buildings(skip, limit, search, category)

@router.get("/buildings/{building_id}", response_model=BuildingResponseSchema)
async def get_building(
    building_id: str,
    user: Dict[str, Any] = Depends(require_authenticated),
    service: BuildingService = Depends(get_building_service)
):
    """Retrieves detailed info of a single building. Read-only."""
    return await service.get_building(building_id)

@router.get("/buildings/code/{code}", response_model=BuildingResponseSchema)
async def get_building_by_code(
    code: str,
    user: Dict[str, Any] = Depends(require_authenticated),
    service: BuildingService = Depends(get_building_service)
):
    """Retrieves building details by its unique code. Read-only."""
    return await service.get_building_by_code(code)

@router.post("/buildings", response_model=BuildingResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_building(
    payload: BuildingCreateSchema,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: BuildingService = Depends(get_building_service)
):
    """Creates a new building. Admin only."""
    return await service.create_building(payload)

@router.put("/buildings/{building_id}", response_model=BuildingResponseSchema)
async def update_building(
    building_id: str,
    payload: BuildingUpdateSchema,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: BuildingService = Depends(get_building_service)
):
    """Updates building properties. Admin only."""
    return await service.update_building(building_id, payload)

@router.delete("/buildings/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_building(
    building_id: str,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: BuildingService = Depends(get_building_service)
):
    """Deletes a building. Admin only."""
    await service.delete_building(building_id)
    return None


# --- ROOMS ENDPOINTS ---

@router.get("/rooms", response_model=Dict[str, Any])
async def list_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    building_id: Optional[str] = Query(None),
    floor: Optional[int] = Query(None),
    room_type: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: RoomService = Depends(get_room_service)
):
    """Lists/paginates rooms inside buildings. Read-only."""
    return await service.list_rooms(skip, limit, search, building_id, floor, room_type)

@router.get("/rooms/{room_id}", response_model=RoomResponseSchema)
async def get_room(
    room_id: str,
    user: Dict[str, Any] = Depends(require_authenticated),
    service: RoomService = Depends(get_room_service)
):
    """Retrieves details of a single room. Read-only."""
    return await service.get_room(room_id)

@router.post("/rooms", response_model=RoomResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_room(
    payload: RoomCreateSchema,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: RoomService = Depends(get_room_service)
):
    """Creates a new room inside a building. Admin only."""
    return await service.create_room(payload)

@router.put("/rooms/{room_id}", response_model=RoomResponseSchema)
async def update_room(
    room_id: str,
    payload: RoomUpdateSchema,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: RoomService = Depends(get_room_service)
):
    """Updates a room's fields. Admin only."""
    return await service.update_room(room_id, payload)

@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: str,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: RoomService = Depends(get_room_service)
):
    """Deletes a room. Admin only."""
    await service.delete_room(room_id)
    return None


# --- LANDMARKS ENDPOINTS ---

@router.get("/landmarks", response_model=Dict[str, Any])
async def list_landmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: LandmarkService = Depends(get_landmark_service)
):
    """Lists/paginates campus landmarks. Read-only."""
    return await service.list_landmarks(skip, limit, search, category)

@router.get("/landmarks/{landmark_id}", response_model=LandmarkResponseSchema)
async def get_landmark(
    landmark_id: str,
    user: Dict[str, Any] = Depends(require_authenticated),
    service: LandmarkService = Depends(get_landmark_service)
):
    """Retrieves details of a single landmark. Read-only."""
    return await service.get_landmark(landmark_id)

@router.post("/landmarks", response_model=LandmarkResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_landmark(
    payload: LandmarkCreateSchema,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: LandmarkService = Depends(get_landmark_service)
):
    """Creates a new landmark. Admin only."""
    return await service.create_landmark(payload)

@router.put("/landmarks/{landmark_id}", response_model=LandmarkResponseSchema)
async def update_landmark(
    landmark_id: str,
    payload: LandmarkUpdateSchema,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: LandmarkService = Depends(get_landmark_service)
):
    """Updates landmark details. Admin only."""
    return await service.update_landmark(landmark_id, payload)

@router.delete("/landmarks/{landmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_landmark(
    landmark_id: str,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: LandmarkService = Depends(get_landmark_service)
):
    """Deletes a landmark. Admin only."""
    await service.delete_landmark(landmark_id)
    return None


# --- FACILITIES ENDPOINTS ---

@router.get("/facilities", response_model=Dict[str, Any])
async def list_facilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: FacilityService = Depends(get_facility_service)
):
    """Lists/paginates facilities (Xerox, ATMs, cafes). Read-only."""
    return await service.list_facilities(skip, limit, search, category)

@router.get("/facilities/{facility_id}", response_model=FacilityResponseSchema)
async def get_facility(
    facility_id: str,
    user: Dict[str, Any] = Depends(require_authenticated),
    service: FacilityService = Depends(get_facility_service)
):
    """Retrieves details of a facility. Read-only."""
    return await service.get_facility(facility_id)

@router.post("/facilities", response_model=FacilityResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_facility(
    payload: FacilityCreateSchema,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: FacilityService = Depends(get_facility_service)
):
    """Creates a facility. Admin only."""
    return await service.create_facility(payload)

@router.put("/facilities/{facility_id}", response_model=FacilityResponseSchema)
async def update_facility(
    facility_id: str,
    payload: FacilityUpdateSchema,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: FacilityService = Depends(get_facility_service)
):
    """Updates facility details. Admin only."""
    return await service.update_facility(facility_id, payload)

@router.delete("/facilities/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_facility(
    facility_id: str,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: FacilityService = Depends(get_facility_service)
):
    """Deletes a facility. Admin only."""
    await service.delete_facility(facility_id)
    return None


# --- PATHWAYS ENDPOINTS ---

@router.get("/pathways", response_model=Dict[str, Any])
async def list_pathways(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    path_type: Optional[str] = Query(None),
    accessible: Optional[bool] = Query(None),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: PathwayService = Depends(get_pathway_service)
):
    """Lists/paginates campus pathways. Read-only."""
    return await service.list_pathways(skip, limit, path_type, accessible)

@router.get("/pathways/{pathway_id}", response_model=PathwayResponseSchema)
async def get_pathway(
    pathway_id: str,
    user: Dict[str, Any] = Depends(require_authenticated),
    service: PathwayService = Depends(get_pathway_service)
):
    """Retrieves details of a pathway. Read-only."""
    return await service.get_pathway(pathway_id)

@router.post("/pathways", response_model=PathwayResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_pathway(
    payload: PathwayCreateSchema,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: PathwayService = Depends(get_pathway_service)
):
    """Creates a new pathway segment. Admin only."""
    return await service.create_pathway(payload)

@router.put("/pathways/{pathway_id}", response_model=PathwayResponseSchema)
async def update_pathway(
    pathway_id: str,
    payload: PathwayUpdateSchema,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: PathwayService = Depends(get_pathway_service)
):
    """Updates a pathway's properties. Admin only."""
    return await service.update_pathway(pathway_id, payload)

@router.delete("/pathways/{pathway_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pathway(
    pathway_id: str,
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    service: PathwayService = Depends(get_pathway_service)
):
    """Deletes a pathway segment. Admin only."""
    await service.delete_pathway(pathway_id)
    return None


# --- UNIFIED SEARCH ENDPOINT ---

@router.get("/search", response_model=List[NavigationSearchResultSchema])
async def search_navigation(
    q: str = Query(..., min_length=2, description="Search term for building code, room number, landmark, facility services"),
    limit: int = Query(20, ge=1, le=100),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: NavigationSearchService = Depends(get_nav_search_service)
):
    """Performs unified campus location search. Returns aggregated results matching query."""
    return await service.search(q, limit)
