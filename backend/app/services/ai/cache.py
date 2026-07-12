import time
import threading
import logging
from app.core.config import CACHE_TTL

logger = logging.getLogger("response_cache")

class ResponseCache:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        
    def _normalize_key(self, key: str) -> str:
        if not key:
            return ""
        return " ".join(key.lower().strip().split())
        
    def get(self, key: str) -> dict | None:
        norm_key = self._normalize_key(key)
        if not norm_key:
            return None
            
        with self._lock:
            if norm_key in self._cache:
                val, expiry = self._cache[norm_key]
                if time.time() < expiry:
                    logger.info(f"Response cache HIT for query: '{key}'")
                    return val
                else:
                    logger.info(f"Response cache EXPIRED for query: '{key}'")
                    del self._cache[norm_key]
        return None
        
    def set(self, key: str, val: dict):
        norm_key = self._normalize_key(key)
        if not norm_key:
            return
            
        expiry = time.time() + CACHE_TTL
        with self._lock:
            self._cache[norm_key] = (val, expiry)
            logger.info(f"Cached response for query: '{key}' (expires in {CACHE_TTL}s)")
            
    def clear(self):
        with self._lock:
            self._cache.clear()
            logger.info("Response cache cleared successfully.")

# Singleton Instance
_cache_instance = ResponseCache()

def get_cached_response(query: str) -> dict | None:
    return _cache_instance.get(query)

def set_cached_response(query: str, response: dict):
    return _cache_instance.set(query, response)

def clear_response_cache():
    return _cache_instance.clear()
