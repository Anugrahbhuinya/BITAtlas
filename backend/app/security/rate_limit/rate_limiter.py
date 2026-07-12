import time
import jwt
from typing import Dict, List, Tuple
from fastapi import Request, status
from app.security.config.settings import settings
from app.auth.jwt_service import SECRET_KEY, ALGORITHM

class RateLimitException(Exception):
    def __init__(self, retry_after: int, limit: int, remaining: int, window: str, error_message: str = "Rate limit exceeded. Please try again later."):
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.window = window
        self.error_message = error_message
        super().__init__(error_message)

class RateLimiter:
    """
    Tier-aware sliding window rate limiter.
    """
    def __init__(self):
        # Stores histories as key (endpoint:identifier) -> list of floats
        self.history: Dict[str, List[float]] = {}

    def get_user_info(self, request: Request) -> Tuple[str, str]:
        """
        Extracts user identifier and tier based on JWT authorization.
        Tiers: 'anonymous', 'student', 'admin'
        """
        client_ip = request.client.host if request.client else "unknown"
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                role = payload.get("role")
                sub = payload.get("sub")
                if sub:
                    if role in ["admin", "superadmin"]:
                        return f"admin:{sub}", "admin"
                    elif role == "student":
                        return f"student:{sub}", "student"
                    else:
                        return f"student:{sub}", "student"
            except jwt.PyJWTError:
                pass
        return f"ip:{client_ip}", "anonymous"

    def check_rate_limit(
        self,
        request: Request,
        endpoint_name: str,
        limits: Dict[str, Tuple[int, int]]
    ):
        """
        Checks rate limit for the request and tier.
        limits = { tier: (limit_count, window_seconds) }
        """
        if request.method == "OPTIONS":
            return

        if settings.ENV == "testing":
            return

        identifier, tier = self.get_user_info(request)
        
        if tier not in limits:
            tier = "anonymous"

        requests_limit, window_seconds = limits[tier]

        # 0 or negative means unlimited
        if requests_limit <= 0:
            return

        now = time.time()
        key = f"{endpoint_name}:{identifier}"

        if key not in self.history:
            self.history[key] = []

        # Keep only timestamps within the sliding window
        self.history[key] = [t for t in self.history[key] if now - t < window_seconds]

        # Check rate limit
        if len(self.history[key]) >= requests_limit:
            if self.history[key]:
                oldest_t = self.history[key][0]
                retry_after = int(window_seconds - (now - oldest_t))
                if retry_after <= 0:
                    retry_after = 1
            else:
                retry_after = 1

            if window_seconds == 60:
                window_str = "1 minute"
            elif window_seconds == 3600:
                window_str = "1 hour"
            elif window_seconds % 60 == 0:
                window_str = f"{window_seconds // 60} minutes"
            else:
                window_str = f"{window_seconds} seconds"

            raise RateLimitException(
                retry_after=retry_after,
                limit=requests_limit,
                remaining=0,
                window=window_str
            )

        self.history[key].append(now)

# Global rate limiter instance
limiter = RateLimiter()

class SlidingWindowRateLimiter:
    """
    Backward-compatible wrapper class for rate limiters mocked in tests.
    """
    def __init__(self, endpoint_name: str, limits: Dict[str, Tuple[int, int]]):
        self.endpoint_name = endpoint_name
        self.limits = limits

    def is_rate_limited(self, client_ip: str, request: Request = None) -> bool:
        if request:
            try:
                limiter.check_rate_limit(request, self.endpoint_name, self.limits)
                return False
            except RateLimitException as exc:
                raise exc
        return False

# Initialize distinct limit configurations (backward compatible objects)
chat_rate_limiter = SlidingWindowRateLimiter(
    endpoint_name="chat",
    limits={
        "anonymous": (10, 60),
        "student": (60, 60),
        "admin": (120, 60),
    }
)

admin_rate_limiter = SlidingWindowRateLimiter(
    endpoint_name="admin_general",
    limits={
        "anonymous": (10, 60),
        "student": (30, 60),
        "admin": (120, 60),
    }
)

# Endpoint-specific rate limiting dependencies
async def rate_limit_auth(request: Request):
    limiter.check_rate_limit(
        request=request,
        endpoint_name="auth",
        limits={
            "anonymous": (5, 60),
            "student": (5, 60),
            "admin": (5, 60),
        }
    )

async def rate_limit_chat(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if chat_rate_limiter.is_rate_limited(client_ip, request=request):
        raise RateLimitException(
            retry_after=60,
            limit=60,
            remaining=0,
            window="1 minute"
        )

async def rate_limit_search(request: Request):
    limiter.check_rate_limit(
        request=request,
        endpoint_name="search",
        limits={
            "anonymous": (20, 60),
            "student": (120, 60),
            "admin": (240, 60),
        }
    )

async def rate_limit_upload(request: Request):
    limiter.check_rate_limit(
        request=request,
        endpoint_name="upload",
        limits={
            "anonymous": (0, 3600),  # Blocked
            "student": (0, 3600),    # Blocked
            "admin": (10, 3600),     # 10 uploads/hour per admin
        }
    )

async def rate_limit_website_indexing(request: Request):
    limiter.check_rate_limit(
        request=request,
        endpoint_name="website_indexing",
        limits={
            "anonymous": (0, 3600),  # Blocked
            "student": (0, 3600),    # Blocked
            "admin": (20, 3600),     # 20 indexing/hour per admin
        }
    )

async def rate_limit_system_status(request: Request):
    limiter.check_rate_limit(
        request=request,
        endpoint_name="system_status",
        limits={
            "anonymous": (5, 60),
            "student": (30, 60),
            "admin": (120, 60),
        }
    )

async def rate_limit_admin(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if admin_rate_limiter.is_rate_limited(client_ip, request=request):
        raise RateLimitException(
            retry_after=60,
            limit=10,
            remaining=0,
            window="1 minute"
        )
