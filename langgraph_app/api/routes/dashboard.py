# src/langgraph_app/api/routes/dashboard.py
"""
API routes for dashboard statistics and activity.
User-isolated stats with fail-fast behavior.
"""

import logging
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from datetime import datetime, timedelta

from ...core.generation_engine import generation_engine

logger = logging.getLogger("writerzroom.api.dashboard")

router = APIRouter()

def _extract_user_id(request: Request, x_user_id: Optional[str] = Header(None)) -> str:
    """Extract user ID from request headers with fail-fast validation."""
    user_id = x_user_id or request.headers.get("X-User-ID")
    
    if not user_id:
        logger.error("Dashboard request missing X-User-ID header")
        raise HTTPException(
            status_code=401, 
            detail="ENTERPRISE: X-User-ID header required for user isolation"
        )
    
    return user_id

@router.get("/stats")
async def get_dashboard_stats(
    request: Request,
    x_user_id: Optional[str] = Header(None)
):
    """
    Retrieves user-specific dashboard statistics.
    ENTERPRISE: Strict user isolation - no cross-user data leakage.
    """
    user_id = _extract_user_id(request, x_user_id)
    
    try:
        # Get user-filtered stats from generation engine
        global_stats = generation_engine.get_generation_stats()
        
        # Filter to user's data only
        user_stats = {
            "total_content": 0,
            "drafts": 0,
            "published": 0,
            "views": 0,
            "recent_content": [],
            "recent_activity": []
        }
        
        # TODO: Implement actual user filtering in generation_engine
        # For now, return empty stats to prevent data leakage
        logger.warning(f"Dashboard stats for user {user_id}: user filtering not implemented, returning empty")
        
        return user_stats
        
    except Exception as e:
        logger.error(f"Failed to get dashboard stats for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="ENTERPRISE: Dashboard stats unavailable"
        )

@router.get("/activity")
async def get_activity_feed(
    request: Request,
    x_user_id: Optional[str] = Header(None)
):
    """
    Retrieves user-specific activity feed.
    ENTERPRISE: Strict user isolation.
    """
    user_id = _extract_user_id(request, x_user_id)
    
    # Stub implementation - return empty until implemented
    return {
        "activities": [],
        "userId": user_id,
        "lastUpdated": datetime.utcnow().isoformat()
    }