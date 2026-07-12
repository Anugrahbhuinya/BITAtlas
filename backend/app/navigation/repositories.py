# backend/app/navigation/repositories.py

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class BuildingRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.buildings

    async def get_by_id(self, building_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(building_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception:
            return None

    async def get_by_code(self, building_code: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"building_code": building_code})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"building_name": {"$regex": search, "$options": "i"}},
                {"building_code": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"departments": {"$regex": search, "$options": "i"}},
                {"aliases": {"$regex": search, "$options": "i"}}
            ]
        cursor = self.collection.find(query).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def count(self, search: Optional[str] = None, category: Optional[str] = None) -> int:
        query: Dict[str, Any] = {}
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"building_name": {"$regex": search, "$options": "i"}},
                {"building_code": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"departments": {"$regex": search, "$options": "i"}},
                {"aliases": {"$regex": search, "$options": "i"}}
            ]
        return await self.collection.count_documents(query)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data

    async def update(self, building_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            await self.collection.update_one(
                {"_id": ObjectId(building_id)},
                {"$set": data}
            )
            return await self.get_by_id(building_id)
        except Exception:
            return None

    async def delete(self, building_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(building_id)})
            return result.deleted_count > 0
        except Exception:
            return False


class RoomRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.rooms

    async def get_by_id(self, room_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(room_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception:
            return None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        building_id: Optional[str] = None,
        floor: Optional[int] = None,
        room_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if building_id:
            query["building_id"] = building_id
        if floor is not None:
            query["floor"] = floor
        if room_type:
            query["room_type"] = room_type
        if search:
            query["$or"] = [
                {"room_number": {"$regex": search, "$options": "i"}},
                {"room_name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"department": {"$regex": search, "$options": "i"}}
            ]
        cursor = self.collection.find(query).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def count(
        self,
        search: Optional[str] = None,
        building_id: Optional[str] = None,
        floor: Optional[int] = None,
        room_type: Optional[str] = None
    ) -> int:
        query: Dict[str, Any] = {}
        if building_id:
            query["building_id"] = building_id
        if floor is not None:
            query["floor"] = floor
        if room_type:
            query["room_type"] = room_type
        if search:
            query["$or"] = [
                {"room_number": {"$regex": search, "$options": "i"}},
                {"room_name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"department": {"$regex": search, "$options": "i"}}
            ]
        return await self.collection.count_documents(query)

    async def get_by_building(self, building_id: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"building_id": building_id})
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data

    async def update(self, room_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            await self.collection.update_one(
                {"_id": ObjectId(room_id)},
                {"$set": data}
            )
            return await self.get_by_id(room_id)
        except Exception:
            return None

    async def delete(self, room_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(room_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def delete_by_building(self, building_id: str) -> int:
        result = await self.collection.delete_many({"building_id": building_id})
        return result.deleted_count


class LandmarkRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.landmarks

    async def get_by_id(self, landmark_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(landmark_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception:
            return None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        cursor = self.collection.find(query).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def count(self, search: Optional[str] = None, category: Optional[str] = None) -> int:
        query: Dict[str, Any] = {}
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        return await self.collection.count_documents(query)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data

    async def update(self, landmark_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            await self.collection.update_one(
                {"_id": ObjectId(landmark_id)},
                {"$set": data}
            )
            return await self.get_by_id(landmark_id)
        except Exception:
            return None

    async def delete(self, landmark_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(landmark_id)})
            return result.deleted_count > 0
        except Exception:
            return False


class FacilityRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.facilities

    async def get_by_id(self, facility_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(facility_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception:
            return None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"timing": {"$regex": search, "$options": "i"}},
                {"services": {"$regex": search, "$options": "i"}}
            ]
        cursor = self.collection.find(query).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def count(self, search: Optional[str] = None, category: Optional[str] = None) -> int:
        query: Dict[str, Any] = {}
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"timing": {"$regex": search, "$options": "i"}},
                {"services": {"$regex": search, "$options": "i"}}
            ]
        return await self.collection.count_documents(query)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data

    async def update(self, facility_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            await self.collection.update_one(
                {"_id": ObjectId(facility_id)},
                {"$set": data}
            )
            return await self.get_by_id(facility_id)
        except Exception:
            return None

    async def delete(self, facility_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(facility_id)})
            return result.deleted_count > 0
        except Exception:
            return False


class PathwayRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.pathways

    async def get_by_id(self, pathway_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(pathway_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception:
            return None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        path_type: Optional[str] = None,
        accessible: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if path_type:
            query["path_type"] = path_type
        if accessible is not None:
            query["accessible"] = accessible
        cursor = self.collection.find(query).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def count(self, path_type: Optional[str] = None, accessible: Optional[bool] = None) -> int:
        query: Dict[str, Any] = {}
        if path_type:
            query["path_type"] = path_type
        if accessible is not None:
            query["accessible"] = accessible
        return await self.collection.count_documents(query)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data

    async def update(self, pathway_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            await self.collection.update_one(
                {"_id": ObjectId(pathway_id)},
                {"$set": data}
            )
            return await self.get_by_id(pathway_id)
        except Exception:
            return None

    async def delete(self, pathway_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(pathway_id)})
            return result.deleted_count > 0
        except Exception:
            return False
