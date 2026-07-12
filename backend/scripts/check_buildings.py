# backend/scripts/check_buildings.py

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core import config

async def check():
    client = AsyncIOMotorClient(config.MONGO_URI)
    db = client[config.MONGO_DB]
    print("=== BUILDINGS ===")
    async for b in db.buildings.find():
        print(f"{b['building_name']}: {b['latitude']}, {b['longitude']}")
    print("\n=== FACILITIES ===")
    async for f in db.facilities.find():
        print(f"{f['name']}: {f['latitude']}, {f['longitude']}")
    print("\n=== LANDMARKS ===")
    async for l in db.landmarks.find():
        print(f"{l['name']}: {l['latitude']}, {l['longitude']}")

if __name__ == "__main__":
    asyncio.run(check())
