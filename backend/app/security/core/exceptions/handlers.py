import logging
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.security.core.exceptions.responses import create_error_response

logger = logging.getLogger("security.exceptions")

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catches all unhandled python exceptions, logs them with request correlation, and sanitizes response details.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Unhandled Exception on {request.url.path}: {str(exc)}",
        extra={"request_id": request_id},
        exc_info=True
    )
    
    # Sanitize 500 errors to prevent stack trace leaks
    return create_error_response(
        status_code=500,
        message="An internal server error occurred. Please try again later.",
        request_id=request_id,
        internal_error=str(exc)
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handles FastAPI HTTPExceptions, ensuring standard response schema.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"HTTPException on {request.url.path}: {exc.status_code} - {exc.detail}",
        extra={"request_id": request_id}
    )
    status_code = exc.status_code
    if status_code == 403 and exc.detail == "Not authenticated":
        status_code = 401
    return create_error_response(
        status_code=status_code,
        message=exc.detail,
        request_id=request_id
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handles request parameters/payload validation errors, preserving custom frontend-facing missing fields formats.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    errors = exc.errors()
    
    # Custom registration/login field checks
    missing_fields = []
    for err in errors:
        if err.get("type") in ["value_error.missing", "missing"]:
            loc = err.get("loc", [])
            if len(loc) > 1:
                missing_fields.append(str(loc[1]))
                
    if missing_fields:
        message = f"Missing required field(s): {', '.join(missing_fields)}"
    else:
        # Pull primary message
        message = f"Validation Error: {errors[0].get('msg', 'Invalid request parameters')}"
        
    logger.warning(
        f"Validation Error on {request.url.path}: {message}",
        extra={"request_id": request_id}
    )
    
    return create_error_response(
        status_code=400,
        message=message,
        request_id=request_id,
        internal_error=str(errors)
    )

from app.security.rate_limit.rate_limiter import RateLimitException

async def rate_limit_exception_handler(request: Request, exc: RateLimitException) -> JSONResponse:
    """
    Handles tier-aware RateLimitExceptions, returning standardized flat JSON body and headers.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"RateLimitException on {request.url.path}: limit={exc.limit}, retry_after={exc.retry_after}",
        extra={"request_id": request_id}
    )
    content = {
        "error": exc.error_message,
        "detail": exc.error_message,  # Ensure compatibility with existing test asserts
        "retry_after": exc.retry_after,
        "limit": exc.limit,
        "remaining": exc.remaining,
        "window": exc.window
    }
    headers = {
        "Retry-After": str(exc.retry_after),
        "X-RateLimit-Limit": str(exc.limit),
        "X-RateLimit-Remaining": str(exc.remaining),
        "X-RateLimit-Reset": str(exc.retry_after)
    }
    return JSONResponse(
        status_code=429,
        content=content,
        headers=headers
    )

