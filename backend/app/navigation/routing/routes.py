# backend/app/navigation/routing/routes.py

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.middleware.auth import require_authenticated
from app.navigation.graph.repositories import get_graph_repository
from app.navigation.graph.services import CampusGraphBuilderService

# Routing entities
from app.navigation.routing.repositories.route_cache import get_route_cache_repository
from app.navigation.routing.services.eta import ETAService
from app.navigation.routing.services.instruction import InstructionService
from app.navigation.routing.services.routing import RoutingService
from app.navigation.routing.schemas.route import (
    RouteResponseSchema,
    ETAResponseSchema,
    ReachableResponseSchema,
    NearbyResponseSchema
)

router = APIRouter()

# Dependency Provider for RoutingService
def get_routing_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> RoutingService:
    graph_repo = get_graph_repository()
    # Initialize the graph builder to make sure the graph data is loaded
    builder = CampusGraphBuilderService(db, graph_repo)
    
    route_cache = get_route_cache_repository()
    eta_service = ETAService()
    instruction_service = InstructionService()
    
    return RoutingService(graph_repo, route_cache, eta_service, instruction_service)

@router.get("", response_model=RouteResponseSchema)
async def calculate_route(
    start: str = Query(..., description="Start node ID"),
    destination: str = Query(..., description="Destination node ID"),
    routeType: str = Query("shortest", description="shortest, fastest, accessible"),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: RoutingService = Depends(get_routing_service)
):
    """
    Calculates a route from a start node to a destination node using the specified strategy.
    """
    try:
        route = await service.calculate_route(start, destination, routeType)
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No route found from '{start}' to '{destination}' under strategy '{routeType}'."
            )
        
        # Map domain Route model to RouteResponseSchema format
        return {
            "start_node": route.start_node.to_dict() if hasattr(route.start_node, "to_dict") else route.start_node.__dict__,
            "destination_node": route.destination_node.to_dict() if hasattr(route.destination_node, "to_dict") else route.destination_node.__dict__,
            "ordered_path": [e.to_dict() if hasattr(e, "to_dict") else e.__dict__ for e in route.ordered_path],
            "ordered_nodes": [n.to_dict() if hasattr(n, "to_dict") else n.__dict__ for n in route.ordered_nodes],
            "total_distance": route.total_distance,
            "estimated_walking_time": route.estimated_walking_time,
            "total_nodes": len(route.ordered_nodes),
            "navigation_instructions": route.navigation_instructions,
            "accessibility_information": route.accessibility_information,
            "alternative_routes": route.alternative_routes,
            "metadata": route.metadata
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/eta", response_model=ETAResponseSchema)
async def get_route_eta(
    start: str = Query(..., description="Start node ID"),
    destination: str = Query(..., description="Destination node ID"),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: RoutingService = Depends(get_routing_service)
):
    """
    Calculates distance and estimated walking duration directly.
    """
    try:
        route = await service.calculate_route(start, destination, "shortest")
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unreachable destination."
            )
        return {
            "start_id": start,
            "destination_id": destination,
            "distance_meters": route.total_distance,
            "estimated_seconds": route.estimated_walking_time,
            "accessible": route.accessibility_information
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/instructions", response_model=List[str])
async def get_route_instructions(
    start: str = Query(..., description="Start node ID"),
    destination: str = Query(..., description="Destination node ID"),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: RoutingService = Depends(get_routing_service)
):
    """
    Retrieves human-readable instructions list for the route path.
    """
    try:
        route = await service.calculate_route(start, destination, "shortest")
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unreachable destination."
            )
        return route.navigation_instructions
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/reachable", response_model=ReachableResponseSchema)
async def get_reachable_nodes(
    start: str = Query(..., description="Start node ID"),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: RoutingService = Depends(get_routing_service)
):
    """
    Checks the connectivity subgraph reachable from the selected start node.
    """
    try:
        reachable = await service.get_reachable_nodes(start)
        return {
            "start_id": start,
            "reachable_node_ids": reachable,
            "total_reachable": len(reachable)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/nearby", response_model=NearbyResponseSchema)
async def get_nearby_nodes(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    radius: float = Query(200.0, description="Search radius in meters"),
    user: Dict[str, Any] = Depends(require_authenticated),
    service: RoutingService = Depends(get_routing_service)
):
    """
    Geographical search returning nodes within a specific meters radius circle.
    """
    nodes = await service.get_nearby_nodes(latitude, longitude, radius)
    return {
        "center_latitude": latitude,
        "center_longitude": longitude,
        "radius_meters": radius,
        "nearby_nodes": [n.to_dict() if hasattr(n, "to_dict") else n.__dict__ for n in nodes]
    }
