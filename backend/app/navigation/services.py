# backend/app/navigation/services.py

import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from app.navigation.repositories import (
    BuildingRepository,
    RoomRepository,
    LandmarkRepository,
    FacilityRepository,
    PathwayRepository
)
from app.navigation.models import (
    BuildingModel,
    RoomModel,
    LandmarkModel,
    FacilityModel,
    PathwayModel
)
from app.navigation.schemas import (
    BuildingCreateSchema, BuildingUpdateSchema,
    RoomCreateSchema, RoomUpdateSchema,
    LandmarkCreateSchema, LandmarkUpdateSchema,
    FacilityCreateSchema, FacilityUpdateSchema,
    PathwayCreateSchema, PathwayUpdateSchema
)

class BuildingService:
    def __init__(self, repo: BuildingRepository):
        self.repo = repo

    async def get_building(self, building_id: str) -> Dict[str, Any]:
        building = await self.repo.get_by_id(building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Building with ID {building_id} not found"
            )
        return building

    async def get_building_by_code(self, code: str) -> Dict[str, Any]:
        building = await self.repo.get_by_code(code)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Building with code {code} not found"
            )
        return building

    async def list_buildings(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        items = await self.repo.get_all(skip, limit, search, category)
        total = await self.repo.count(search, category)
        return {
            "buildings": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def create_building(self, schema: BuildingCreateSchema) -> Dict[str, Any]:
        # Check duplicate code
        existing = await self.repo.get_by_code(schema.building_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Building code '{schema.building_code}' already exists"
            )
        
        model = BuildingModel(
            building_code=schema.building_code,
            building_name=schema.building_name,
            description=schema.description,
            category=schema.category.value,
            latitude=schema.latitude,
            longitude=schema.longitude,
            address=schema.address,
            opening_hours=schema.opening_hours,
            contact=schema.contact,
            departments=schema.departments,
            entrances=[e.model_dump() for e in schema.entrances],
            floors=schema.floors,
            accessibility=schema.accessibility.model_dump(),
            image=schema.image,
            metadata=schema.metadata
        )
        return await self.repo.create(model.to_dict())

    async def update_building(self, building_id: str, schema: BuildingUpdateSchema) -> Dict[str, Any]:
        await self.get_building(building_id) # validates existence
        
        update_data = schema.model_dump(exclude_unset=True)
        if "category" in update_data and update_data["category"]:
            update_data["category"] = update_data["category"].value
        if "entrances" in update_data and update_data["entrances"]:
            update_data["entrances"] = [e.model_dump() if hasattr(e, "model_dump") else e for e in update_data["entrances"]]
        if "accessibility" in update_data and update_data["accessibility"]:
            update_data["accessibility"] = update_data["accessibility"].model_dump() if hasattr(update_data["accessibility"], "model_dump") else update_data["accessibility"]
            
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        updated = await self.repo.update(building_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update building details"
            )
        return updated

    async def delete_building(self, building_id: str) -> bool:
        await self.get_building(building_id)
        return await self.repo.delete(building_id)


class RoomService:
    def __init__(self, repo: RoomRepository, building_repo: BuildingRepository):
        self.repo = repo
        self.building_repo = building_repo

    async def get_room(self, room_id: str) -> Dict[str, Any]:
        room = await self.repo.get_by_id(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with ID {room_id} not found"
            )
        return room

    async def list_rooms(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        building_id: Optional[str] = None,
        floor: Optional[int] = None,
        room_type: Optional[str] = None
    ) -> Dict[str, Any]:
        items = await self.repo.get_all(skip, limit, search, building_id, floor, room_type)
        total = await self.repo.count(search, building_id, floor, room_type)
        return {
            "rooms": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def create_room(self, schema: RoomCreateSchema) -> Dict[str, Any]:
        # Validate building exists
        building = await self.building_repo.get_by_id(schema.building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Building ID '{schema.building_id}' does not exist"
            )
        
        # Verify floor exists in building floor list
        if building.get("floors") and schema.floor not in building.get("floors"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Floor {schema.floor} is not valid for building {building.get('building_name')}"
            )
            
        model = RoomModel(
            room_number=schema.room_number,
            room_name=schema.room_name,
            building_id=schema.building_id,
            floor=schema.floor,
            department=schema.department,
            room_type=schema.room_type.value,
            capacity=schema.capacity,
            latitude=schema.latitude or building.get("latitude"),
            longitude=schema.longitude or building.get("longitude"),
            description=schema.description,
            facilities=schema.facilities,
            metadata=schema.metadata
        )
        return await self.repo.create(model.to_dict())

    async def update_room(self, room_id: str, schema: RoomUpdateSchema) -> Dict[str, Any]:
        room = await self.get_room(room_id)
        
        update_data = schema.model_dump(exclude_unset=True)
        if "room_type" in update_data and update_data["room_type"]:
            update_data["room_type"] = update_data["room_type"].value
            
        if "building_id" in update_data and update_data["building_id"]:
            # Validate building exists
            building = await self.building_repo.get_by_id(update_data["building_id"])
            if not building:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Building ID '{update_data['building_id']}' does not exist"
                )
            # Default lat/lng if not updated explicitly
            if "latitude" not in update_data:
                update_data["latitude"] = building.get("latitude")
            if "longitude" not in update_data:
                update_data["longitude"] = building.get("longitude")
                
        updated = await self.repo.update(room_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update room details"
            )
        return updated

    async def delete_room(self, room_id: str) -> bool:
        await self.get_room(room_id)
        return await self.repo.delete(room_id)


class LandmarkService:
    def __init__(self, repo: LandmarkRepository):
        self.repo = repo

    async def get_landmark(self, landmark_id: str) -> Dict[str, Any]:
        landmark = await self.repo.get_by_id(landmark_id)
        if not landmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Landmark with ID {landmark_id} not found"
            )
        return landmark

    async def list_landmarks(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        items = await self.repo.get_all(skip, limit, search, category)
        total = await self.repo.count(search, category)
        return {
            "landmarks": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def create_landmark(self, schema: LandmarkCreateSchema) -> Dict[str, Any]:
        coords = schema.coordinates.model_dump() if schema.coordinates else {"latitude": schema.latitude, "longitude": schema.longitude}
        model = LandmarkModel(
            name=schema.name,
            latitude=schema.latitude,
            longitude=schema.longitude,
            description=schema.description,
            category=schema.category.value,
            image=schema.image,
            coordinates=coords,
            metadata=schema.metadata
        )
        return await self.repo.create(model.to_dict())

    async def update_landmark(self, landmark_id: str, schema: LandmarkUpdateSchema) -> Dict[str, Any]:
        await self.get_landmark(landmark_id)
        
        update_data = schema.model_dump(exclude_unset=True)
        if "category" in update_data and update_data["category"]:
            update_data["category"] = update_data["category"].value
        if "coordinates" in update_data and update_data["coordinates"]:
            update_data["coordinates"] = update_data["coordinates"].model_dump() if hasattr(update_data["coordinates"], "model_dump") else update_data["coordinates"]
            
        updated = await self.repo.update(landmark_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update landmark details"
            )
        return updated

    async def delete_landmark(self, landmark_id: str) -> bool:
        await self.get_landmark(landmark_id)
        return await self.repo.delete(landmark_id)


class FacilityService:
    def __init__(self, repo: FacilityRepository):
        self.repo = repo

    async def get_facility(self, facility_id: str) -> Dict[str, Any]:
        facility = await self.repo.get_by_id(facility_id)
        if not facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Facility with ID {facility_id} not found"
            )
        return facility

    async def list_facilities(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        items = await self.repo.get_all(skip, limit, search, category)
        total = await self.repo.count(search, category)
        return {
            "facilities": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def create_facility(self, schema: FacilityCreateSchema) -> Dict[str, Any]:
        coords = schema.coordinates.model_dump() if schema.coordinates else {"latitude": schema.latitude, "longitude": schema.longitude}
        model = FacilityModel(
            name=schema.name,
            latitude=schema.latitude,
            longitude=schema.longitude,
            category=schema.category.value,
            timing=schema.timing,
            services=schema.services,
            accessibility=schema.accessibility.model_dump(),
            coordinates=coords,
            metadata=schema.metadata
        )
        return await self.repo.create(model.to_dict())

    async def update_facility(self, facility_id: str, schema: FacilityUpdateSchema) -> Dict[str, Any]:
        await self.get_facility(facility_id)
        
        update_data = schema.model_dump(exclude_unset=True)
        if "category" in update_data and update_data["category"]:
            update_data["category"] = update_data["category"].value
        if "coordinates" in update_data and update_data["coordinates"]:
            update_data["coordinates"] = update_data["coordinates"].model_dump() if hasattr(update_data["coordinates"], "model_dump") else update_data["coordinates"]
        if "accessibility" in update_data and update_data["accessibility"]:
            update_data["accessibility"] = update_data["accessibility"].model_dump() if hasattr(update_data["accessibility"], "model_dump") else update_data["accessibility"]
            
        updated = await self.repo.update(facility_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update facility details"
            )
        return updated

    async def delete_facility(self, facility_id: str) -> bool:
        await self.get_facility(facility_id)
        return await self.repo.delete(facility_id)


class PathwayService:
    def __init__(self, repo: PathwayRepository):
        self.repo = repo

    async def get_pathway(self, pathway_id: str) -> Dict[str, Any]:
        pathway = await self.repo.get_by_id(pathway_id)
        if not pathway:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pathway with ID {pathway_id} not found"
            )
        return pathway

    async def list_pathways(
        self,
        skip: int = 0,
        limit: int = 100,
        path_type: Optional[str] = None,
        accessible: Optional[bool] = None
    ) -> Dict[str, Any]:
        items = await self.repo.get_all(skip, limit, path_type, accessible)
        total = await self.repo.count(path_type, accessible)
        return {
            "pathways": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def create_pathway(self, schema: PathwayCreateSchema) -> Dict[str, Any]:
        model = PathwayModel(
            start_node=schema.start_node.model_dump(),
            end_node=schema.end_node.model_dump(),
            path_type=schema.path_type.value,
            distance=schema.distance,
            surface=schema.surface.value,
            accessible=schema.accessible,
            lighting=schema.lighting.value,
            notes=schema.notes,
            metadata=schema.metadata
        )
        return await self.repo.create(model.to_dict())

    async def update_pathway(self, pathway_id: str, schema: PathwayUpdateSchema) -> Dict[str, Any]:
        await self.get_pathway(pathway_id)
        
        update_data = schema.model_dump(exclude_unset=True)
        for key in ["path_type", "surface", "lighting"]:
            if key in update_data and update_data[key]:
                update_data[key] = update_data[key].value
        for key in ["start_node", "end_node"]:
            if key in update_data and update_data[key]:
                update_data[key] = update_data[key].model_dump() if hasattr(update_data[key], "model_dump") else update_data[key]
                
        updated = await self.repo.update(pathway_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update pathway details"
            )
        return updated

    async def delete_pathway(self, pathway_id: str) -> bool:
        await self.get_pathway(pathway_id)
        return await self.repo.delete(pathway_id)


class NavigationSearchService:
    def __init__(
        self,
        building_repo: BuildingRepository,
        room_repo: RoomRepository,
        landmark_repo: LandmarkRepository,
        facility_repo: FacilityRepository
    ):
        self.building_repo = building_repo
        self.room_repo = room_repo
        self.landmark_repo = landmark_repo
        self.facility_repo = facility_repo

    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []
            
        clean_query = query.strip()
        
        # Query collections concurrently
        buildings_task = self.building_repo.get_all(0, limit, search=clean_query)
        rooms_task = self.room_repo.get_all(0, limit, search=clean_query)
        landmarks_task = self.landmark_repo.get_all(0, limit, search=clean_query)
        facilities_task = self.facility_repo.get_all(0, limit, search=clean_query)
        
        buildings, rooms, landmarks, facilities = await asyncio.gather(
            buildings_task, rooms_task, landmarks_task, facilities_task
        )
        
        results: List[Dict[str, Any]] = []
        
        # 1. Format Buildings
        for b in buildings:
            results.append({
                "_id": b["_id"],
                "type": "building",
                "name": b["building_name"],
                "description": b["description"],
                "latitude": b["latitude"],
                "longitude": b["longitude"],
                "category": b["category"],
                "snippet": f"Building code: {b['building_code']} | Category: {b['category']}",
                "osm_id": b.get("osm_id"),
                "osm_type": b.get("osm_type"),
                "geometry": b.get("geometry"),
                "entrance_geometry": b.get("entrance_geometry"),
                "metadata": {
                    "building_code": b["building_code"],
                    "departments": b.get("departments", []),
                    "address": b.get("address", "")
                }
            })
            
        # 2. Format Rooms
        # Since room lists parent building, resolve name if possible
        building_cache = {}
        for r in rooms:
            b_id = r["building_id"]
            if b_id not in building_cache:
                b_doc = await self.building_repo.get_by_id(b_id)
                building_cache[b_id] = b_doc.get("building_name") if b_doc else "Unknown Building"
                
            building_name = building_cache[b_id]
            
            results.append({
                "_id": r["_id"],
                "type": "room",
                "name": f"{r['room_number']} - {r['room_name']}",
                "description": r["description"],
                "latitude": r.get("latitude") or 0.0,
                "longitude": r.get("longitude") or 0.0,
                "category": r["room_type"],
                "snippet": f"Room in {building_name} (Floor {r['floor']})",
                "metadata": {
                    "room_number": r["room_number"],
                    "building_id": r["building_id"],
                    "building_name": building_name,
                    "floor": r["floor"],
                    "capacity": r["capacity"],
                    "facilities": r.get("facilities", [])
                }
            })
            
        # 3. Format Landmarks
        for l in landmarks:
            results.append({
                "_id": l["_id"],
                "type": "landmark",
                "name": l["name"],
                "description": l["description"],
                "latitude": l["latitude"],
                "longitude": l["longitude"],
                "category": l["category"],
                "snippet": f"Campus Landmark | Category: {l['category']}",
                "osm_id": l.get("osm_id"),
                "osm_type": l.get("osm_type"),
                "geometry": l.get("geometry"),
                "entrance_geometry": l.get("entrance_geometry"),
                "metadata": {}
            })
            
        # 4. Format Facilities
        for f in facilities:
            results.append({
                "_id": f["_id"],
                "type": "facility",
                "name": f["name"],
                "description": f.get("timing") or f.get("category"),
                "latitude": f["latitude"],
                "longitude": f["longitude"],
                "category": f["category"],
                "snippet": f"Facility | Services: {', '.join(f.get('services', []))[:60]}",
                "osm_id": f.get("osm_id"),
                "osm_type": f.get("osm_type"),
                "geometry": f.get("geometry"),
                "entrance_geometry": f.get("entrance_geometry"),
                "metadata": {
                    "timing": f.get("timing", ""),
                    "services": f.get("services", []),
                    "accessibility": f.get("accessibility", {})
                }
            })
            
        # Limit total results
        return results[:limit]
