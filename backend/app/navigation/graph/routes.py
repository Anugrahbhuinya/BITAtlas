# backend/app/navigation/graph/routes.py

from fastapi import APIRouter, Depends, status, Query, HTTPException
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

# Core Database and Auth
from app.core.database import get_database
from app.middleware.auth import (
    require_authenticated,
    get_current_admin_user
)

# Models and Repo
from app.navigation.graph.repositories import get_graph_repository
from app.navigation.graph.services import CampusGraphBuilderService, CampusGraphService
from app.navigation.graph.utils import CampusGraphValidator

# Schemas
from app.navigation.graph.schemas import (
    NodeSchema,
    EdgeSchema,
    NeighborSchema,
    GraphSummarySchema,
    GraphValidationReportSchema
)

router = APIRouter()

# Dependency Providers
def get_graph_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> CampusGraphService:
    repo = get_graph_repository()
    builder = CampusGraphBuilderService(db, repo)
    return CampusGraphService(repo, builder)

def get_graph_validator() -> CampusGraphValidator:
    repo = get_graph_repository()
    return CampusGraphValidator(repo)

@router.get("", response_model=GraphSummarySchema)
async def get_graph_summary(
    user: Dict[str, Any] = Depends(require_authenticated),
    service: CampusGraphService = Depends(get_graph_service),
    validator: CampusGraphValidator = Depends(get_graph_validator)
):
    """Retrieves high-level summary and counts of the campus graph nodes and relationships."""
    summary = await service.get_graph_summary()
    report = await validator.validate_graph()
    summary["is_valid"] = report["is_valid"]
    return summary

@router.get("/nodes", response_model=List[NodeSchema])
async def list_graph_nodes(
    type: Optional[str] = Query(None, description="Filter by node type: Building, Room, Entrance, Landmark, Facility, Parking, Hostel, Bus Stop"),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: CampusGraphService = Depends(get_graph_service)
):
    """Lists all nodes in the campus graph, with optional type filters."""
    nodes = await service.list_nodes(node_type=type)
    return [n.to_dict() for n in nodes]

@router.get("/edges", response_model=List[EdgeSchema])
async def list_graph_edges(
    user: Dict[str, Any] = Depends(require_authenticated),
    service: CampusGraphService = Depends(get_graph_service)
):
    """Lists all edge relationships in the campus graph."""
    edges = await service.list_edges()
    return [e.to_dict() for e in edges]

@router.get("/node/{id}", response_model=NodeSchema)
async def get_graph_node(
    id: str,
    user: Dict[str, Any] = Depends(require_authenticated),
    service: CampusGraphService = Depends(get_graph_service)
):
    """Retrieves a single node in the graph by its unique ID."""
    node = await service.get_node_by_id(id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph node with ID {id} not found"
        )
    return node.to_dict()

@router.get("/neighbors/{id}", response_model=List[NeighborSchema])
async def get_node_neighbors(
    id: str,
    user: Dict[str, Any] = Depends(require_authenticated),
    service: CampusGraphService = Depends(get_graph_service)
):
    """Retrieves all neighboring nodes connected to the specified node by outgoing edges."""
    neighbors = await service.get_neighbors(id)
    return [{"node": n.to_dict(), "edge": e.to_dict()} for n, e in neighbors]

@router.get("/building/{id}/rooms", response_model=List[NodeSchema])
async def get_building_rooms_graph(
    id: str,
    user: Dict[str, Any] = Depends(require_authenticated),
    service: CampusGraphService = Depends(get_graph_service)
):
    """Retrieves all Room nodes contained inside the specified Building in the graph."""
    rooms = await service.get_rooms_in_building(id)
    return [r.to_dict() for r in rooms]

@router.get("/building/{id}/facilities", response_model=List[NodeSchema])
async def get_building_facilities_graph(
    id: str,
    radius: float = Query(200.0, ge=10.0, le=2000.0, description="Search radius in meters"),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: CampusGraphService = Depends(get_graph_service)
):
    """Retrieves all Facility nodes within a given radius (meters) of the specified Building node."""
    facilities = await service.get_facilities_near_building(id, radius)
    return [f.to_dict() for f in facilities]

@router.get("/validate", response_model=GraphValidationReportSchema)
async def validate_campus_graph(
    user: Dict[str, Any] = Depends(require_authenticated),
    service: CampusGraphService = Depends(get_graph_service),
    validator: CampusGraphValidator = Depends(get_graph_validator)
):
    """Performs validation checks on the graph (circular containments, orphans, reference errors)."""
    await service._ensure_loaded()
    return await validator.validate_graph()

@router.post("/rebuild", response_model=GraphSummarySchema)
async def rebuild_campus_graph(
    admin: Dict[str, Any] = Depends(get_current_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: get_graph_repository = Depends(get_graph_repository),
    service: CampusGraphService = Depends(get_graph_service),
    validator: CampusGraphValidator = Depends(get_graph_validator)
):
    """Triggers graph builder reconstruction. Pulls all current database documents and regenerates graph indices."""
    builder = CampusGraphBuilderService(db, repo)
    await builder.build_graph()
    
    summary = await service.get_graph_summary()
    report = await validator.validate_graph()
    summary["is_valid"] = report["is_valid"]
    return summary
