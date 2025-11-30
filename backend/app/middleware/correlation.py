"""Request/Response middleware with correlation IDs and structured logging."""
import uuid
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation IDs and structured logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Start timing
        start_time = time.time()
        
        # Log request
        request_log = {
            "correlation_id": correlation_id,
            "method": request.method,
            "path": str(request.url.path),
            "query_params": str(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "event": "request_received"
        }
        logger.info(json.dumps(request_log))
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Log response
            response_log = {
                "correlation_id": correlation_id,
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "response_time_ms": round(process_time * 1000, 2),
                "event": "response_sent"
            }
            logger.info(json.dumps(response_log))
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Response-Time"] = f"{process_time * 1000:.2f}ms"
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            error_log = {
                "correlation_id": correlation_id,
                "method": request.method,
                "path": str(request.url.path),
                "error": str(e),
                "error_type": type(e).__name__,
                "response_time_ms": round(process_time * 1000, 2),
                "event": "request_error"
            }
            logger.error(json.dumps(error_log))
            raise


