# src/langgraph_app/api/routes/generation.py
"""
API route for starting content generation jobs.
"""

import uuid
import logging
from typing import Dict, Any, Optional

from fastapi import (
    APIRouter, 
    BackgroundTasks, 
    Request, 
    HTTPException, 
    status,
    Body
)
from pydantic import BaseModel, Field

# Import the singleton GenerationEngine
from ...core.generation_engine import generation_engine
from ...core.config_manager import ConfigManager

logger = logging.getLogger("writerzroom.api.generation")

router = APIRouter()

class GenerateRequest(BaseModel):
    template_id: str = Field(..., min_length=1, description="The ID of the content template.")
    style_profile_id: str = Field(..., min_length=1, description="The ID of the style profile.")
    user_input: Dict[str, Any] = Field(default_factory=dict, description="User-provided inputs like topic, etc.")
    request_id: Optional[str] = None

@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def start_generation(
    req: GenerateRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Starts a content generation job in the background using the GenerationEngine.
    """
    config_manager: ConfigManager = request.app.state.config_manager
    if not config_manager:
        raise HTTPException(
            status_code=503, 
            detail="Configuration Manager not available."
        )

    request_id = req.request_id or str(uuid.uuid4())

    try:
        # 1. Get validated configs from the ConfigManager
        template_config = config_manager.get_template(req.template_id)
        style_config = config_manager.get_style_profile(req.style_profile_id)
        
        # 2. Merge user_input into the template_config for the engine
        # This provides dynamic parameters
        template_config.update(req.user_input)

        # 3. Add the job to the background tasks
        # We call the GenerationEngine's method, not a local function
        background_tasks.add_task(
            generation_engine.execute_content_generation,
            request_id=request_id,
            template_config=template_config,
            style_config=style_config,
            app_state=request.app.state,
            mcp_options={} # Add any specific MCP options here
        )
        
        logger.info(f"[{request_id}] Generation task added for template '{req.template_id}'")

        return {
            "request_id": request_id,
            "status": "pending",
            "message": "Content generation started.",
            "links": {"status": f"/api/generate/status/{request_id}"},
        }
    except KeyError as e:
        logger.warning(f"Failed to start job: {e}")
        raise HTTPException(status_code=404, detail=f"Configuration not found: {e}")
    except Exception as e:
        logger.error(f"Failed to start generation for request {request_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")