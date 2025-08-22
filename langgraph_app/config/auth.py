# langgraph_app/config/auth.py
"""
Authentication configuration and utilities
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .settings import settings

logger = logging.getLogger(__name__)

# Security setup
security = HTTPBearer(auto_error=False)

async def get_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Extract API key from request headers."""
    return credentials.credentials if credentials else None

async def verify_api_key(api_key: Optional[str] = Depends(get_api_key)) -> bool:
    """Verify API key for enterprise operation."""
    if settings.ENVIRONMENT == "production":
        if not api_key or api_key not in [settings.API_KEY, settings.FASTAPI_API_KEY]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required for enterprise operation",
                headers={"WWW-Authenticate": "Bearer"},
            )
    elif settings.ENVIRONMENT == "development":
        # More lenient in development but still validate if provided
        if api_key and api_key not in [settings.API_KEY, settings.FASTAPI_API_KEY]:
            logger.warning(f"Invalid API key provided in development mode: {api_key[:10]}...")
            return False
    return True

def get_auth_config() -> dict:
    """Get authentication configuration for the application."""
    return {
        "api_key_configured": bool(settings.API_KEY),
        "fastapi_key_configured": bool(settings.FASTAPI_API_KEY),
        "environment": settings.ENVIRONMENT,
        "production_mode": settings.ENVIRONMENT == "production"
    }