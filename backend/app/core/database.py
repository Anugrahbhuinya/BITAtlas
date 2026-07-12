from motor.motor_asyncio import AsyncIOMotorClient
from app.core import config

from typing import Any
_client: Any = None
_db: Any = None
_last_loop: Any = None

def get_database():
    global _client, _db, _last_loop
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
        
    if _client is None or _last_loop != loop:
        _client = AsyncIOMotorClient(config.MONGO_URI)
        _db = _client[config.MONGO_DB]
        _last_loop = loop
    return _db
