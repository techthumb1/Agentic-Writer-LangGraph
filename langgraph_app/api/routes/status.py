# src/langgraph_app/api/routes/status.py
"""
API route for checking the status of generation jobs.
"""

import logging
from fastapi import APIRouter, HTTPException, status

# Import the singleton GenerationEngine
from ...core.generation_engine import generation_engine, GenerationStatus

logger = logging.getLogger("writerzroom.api.status")

router = APIRouter()

@router.get("/status/{request_id}", response_model=GenerationStatus)
async def get_generation_status(request_id: str):
    """
    Retrieves the status or result of a content generation job
    from the GenerationEngine.
    """
    
    # Get status directly from the engine's task cache
    task_status = generation_engine.get_generation_status(request_id)
    
    if not task_status:
        logger.warning(f"Status request for unknown ID: {request_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Generation request not found."
        )
    
    logger.debug(f"[{request_id}] Status checked: {task_status.status}")
    return task_status