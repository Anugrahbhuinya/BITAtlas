# backend/app/navigation/routing/repositories/route_cache.py

import asyncio
from typing import Dict, Tuple, Optional, Any

class RouteCacheRepository:
    def __init__(self):
        self._cache: Dict[Tuple[str, str, str], Any] = {}
        self._lock = asyncio.Lock()

    async def get_route(self, start_id: str, destination_id: str, route_type: str) -> Optional[Any]:
        async with self._lock:
            key = (start_id, destination_id, route_type)
            return self._cache.get(key)

    async def set_route(self, start_id: str, destination_id: str, route_type: str, route: Any) -> None:
        async with self._lock:
            key = (start_id, destination_id, route_type)
            self._cache[key] = route

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()

# Global Singleton instance
_global_route_cache = RouteCacheRepository()

def get_route_cache_repository() -> RouteCacheRepository:
    return _global_route_cache
