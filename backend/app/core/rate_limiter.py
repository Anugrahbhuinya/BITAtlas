import time
from typing import Dict, List
from fastapi import Request, HTTPException, status

class SimpleRateLimiter:
    """
    A simple memory-based sliding window rate limiter.
    """
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.history: Dict[str, List[float]] = {}

    def check_rate_limit(self, client_ip: str):
        now = time.time()
        
        if client_ip not in self.history:
            self.history[client_ip] = []
            
        # Keep only timestamps within the current window
        self.history[client_ip] = [
            t for t in self.history[client_ip] 
            if now - t < self.window_seconds
        ]
        
        if len(self.history[client_ip]) >= self.requests_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
            
        self.history[client_ip].append(now)

# Limit file uploads to 10 files per minute per IP address
upload_rate_limiter = SimpleRateLimiter(requests_limit=10, window_seconds=60)
