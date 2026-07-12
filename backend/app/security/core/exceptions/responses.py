from typing import Any, Dict
from fastapi.responses import JSONResponse
from app.security.config.settings import settings

def create_error_response(
    status_code: int,
    message: str,
    request_id: str = "unknown",
    internal_error: str | None = None
) -> JSONResponse:
    """
    Standardizes error responses across all APIs.
    Hides internal stack traces/exceptions in production.
    """
    # Build a response content dictionary that is fully compatible with:
    # 1. Chat API expectations (type="error", answer=message)
    # 2. General endpoint expectations (detail=message)
    content: Dict[str, Any] = {
        "type": "error",
        "answer": message,
        "detail": message,
        "request_id": request_id
    }
    
    # Expose detailed internal errors ONLY in debug mode/development profile
    if settings.DEBUG and internal_error:
        content["internal_error"] = internal_error
        
    return JSONResponse(
        status_code=status_code,
        content=content
    )
