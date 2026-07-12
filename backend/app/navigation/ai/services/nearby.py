# backend/app/navigation/ai/services/nearby.py

import math
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class NearbyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # Spherical Law of Cosines to get distance in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_lambda = math.radians(lon2 - lon1)
        R = 6371000.0  # meters
        
        val = math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(delta_lambda)
        # Handle floating point inaccuracies
        val = max(-1.0, min(1.0, val))
        return math.acos(val) * R

    async def find_nearby_places(self, lat: float, lon: float, radius: float = 500.0) -> List[Dict[str, Any]]:
        nearby = []
        
        # 1. Fetch buildings
        cursor_b = self.db.buildings.find()
        async for b in cursor_b:
            dist = self.calculate_distance(lat, lon, b["latitude"], b["longitude"])
            if dist <= radius:
                nearby.append({
                    "id": b["_id"] if isinstance(b["_id"], str) else str(b["_id"]),
                    "name": b["building_name"],
                    "category": b["category"],
                    "type": "building",
                    "distance_meters": round(dist, 1),
                    "coordinates": {"latitude": b["latitude"], "longitude": b["longitude"]}
                })

        # 2. Fetch facilities
        cursor_f = self.db.facilities.find()
        async for f in cursor_f:
            dist = self.calculate_distance(lat, lon, f["latitude"], f["longitude"])
            if dist <= radius:
                nearby.append({
                    "id": f["_id"] if isinstance(f["_id"], str) else str(f["_id"]),
                    "name": f["name"],
                    "category": f["category"],
                    "type": "facility",
                    "distance_meters": round(dist, 1),
                    "coordinates": {"latitude": f["latitude"], "longitude": f["longitude"]}
                })

        # 3. Fetch landmarks
        cursor_l = self.db.landmarks.find()
        async for l in cursor_l:
            dist = self.calculate_distance(lat, lon, l["latitude"], l["longitude"])
            if dist <= radius:
                nearby.append({
                    "id": l["_id"] if isinstance(l["_id"], str) else str(l["_id"]),
                    "name": l["name"],
                    "category": l["category"],
                    "type": "landmark",
                    "distance_meters": round(dist, 1),
                    "coordinates": {"latitude": l["latitude"], "longitude": l["longitude"]}
                })

        # Sort by distance
        nearby.sort(key=lambda x: x["distance_meters"])
        return nearby
