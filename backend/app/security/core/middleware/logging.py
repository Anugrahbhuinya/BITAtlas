import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response

logger = logging.getLogger("security.request")

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs incoming requests and outgoing response details using structured parameters.
    Saves metadata including Request ID, IP address, Endpoint, Method, Execution Duration and Status Code.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        
        request_id = getattr(request.state, "request_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Log request receipt
        logger.info(
            f"Request Started: {method} {path}",
            extra={
                "request_id": request_id,
                "client_ip": client_ip,
                "method": method,
                "path": path,
                "stage": "started"
            }
        )
        
        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            
            # Log response delivery
            logger.info(
                f"Request Finished: {method} {path} -> {response.status_code} ({duration:.4f}s)",
                extra={
                    "request_id": request_id,
                    "client_ip": client_ip,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_s": duration,
                    "stage": "finished"
                }
            )
            return response
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error(
                f"Request Failed: {method} {path} -> {str(e)}",
                extra={
                    "request_id": request_id,
                    "client_ip": client_ip,
                    "method": method,
                    "path": path,
                    "duration_s": duration,
                    "error": str(e),
                    "stage": "failed"
                },
                exc_info=True
            )
            raise e
