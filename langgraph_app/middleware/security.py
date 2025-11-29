# langgraph_app/middleware/security.py
"""
Security middleware for WriterzRoom API
- Rate limiting
- CORS configuration
- Request validation
- Security headers
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import os
from typing import Callable

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def configure_cors(app: FastAPI) -> None:
    """Configure CORS for production"""
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
    )
    logger.info(f"CORS configured for origins: {allowed_origins}")

def configure_security_headers(app: FastAPI) -> None:
    """Add security headers middleware"""
    
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

def configure_rate_limiting(app: FastAPI) -> None:
    """Configure rate limiting"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Apply rate limits to generation endpoints
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Only rate limit generation endpoints
        if request.url.path.startswith("/api/generate"):
            rate_limit = os.getenv("RATE_LIMIT_PER_MINUTE", "10")
            # Rate limit is handled by @limiter decorator on routes
            pass
        
        return await call_next(request)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Generate request ID
        request_id = f"{int(time.time() * 1000)}-{get_remote_address(request)}"
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": get_remote_address(request)
            }
        )
        
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2)
            }
        )
        
        # Add request ID to response
        response.headers["X-Request-ID"] = request_id
        
        return response

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize user inputs"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Check request size
        max_size = 10 * 1024 * 1024  # 10MB
        
        if request.headers.get("content-length"):
            content_length = int(request.headers["content-length"])
            if content_length > max_size:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Request body too large"}
                )
        
        # Validate content type for POST/PUT
        if request.method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if not any(ct in content_type for ct in ["application/json", "multipart/form-data"]):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={"detail": "Unsupported content type"}
                )
        
        return await call_next(request)

def setup_security_middleware(app: FastAPI) -> None:
    """Setup all security middleware"""
    
    # Add in order (last added = first executed)
    app.add_middleware(InputValidationMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    configure_cors(app)
    configure_security_headers(app)
    
    if os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true":
        configure_rate_limiting(app)
        logger.info("Rate limiting enabled")
    
    logger.info("Security middleware configured")