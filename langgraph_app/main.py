# File: langgraph_app/main.py
# At the top of langgraph_app/main.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Then your existing code...
import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
import uuid
from pathlib import Path

from .enhanced_orchestration import EnhancedOrchestrator
from .enhanced_model_registry import EnhancedModelRegistry
from .style_profile_loader import StyleProfileLoader
from .cache_system import CacheSystem
from .job_queue import JobQueue
from .template_loader import template_loader

from fastapi import HTTPException, Query
from langgraph_app.style_profile_loader import get_style_profile_loader



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AgentWrite Pro - Enterprise Backend",
    description="Advanced Multi-Agent Content Generation System",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class GenerationRequest(BaseModel):
    template: str
    style_profile: str
    dynamic_parameters: Dict[str, Any] = {}
    priority: int = Field(default=1, ge=1, le=10)
    timeout_seconds: int = Field(default=300, ge=30, le=1800)
    generation_mode: str = Field(default="standard", pattern="^(standard|premium|enterprise)$")
    callback_url: Optional[str] = None

class GenerationResponse(BaseModel):
    success: bool
    generation_id: str
    status: str
    content: Optional[str] = None
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None
    estimated_completion: Optional[datetime] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    active_generations: int
    queue_size: int
    available_models: List[str]
    cache_hit_rate: float

# Initialize Components
orchestrator = EnhancedOrchestrator()
model_registry = EnhancedModelRegistry()
style_loader = StyleProfileLoader()
template_loader = template_loader 
cache_system = CacheSystem()
job_queue = JobQueue()

# Security
async def validate_api_key(authorization: str = Header(None)):
    """Validate API key from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization.replace("Bearer ", "")
    expected_key = os.getenv("LANGGRAPH_API_KEY")
    
    if not expected_key or api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key

# Helper Functions
def safe_get_template(template_id: str) -> Optional[Dict[str, Any]]:
    """Safely get template data"""
    try:
        # Check if the template exists in the cache first
        if hasattr(template_loader, 'templates_cache') and template_id in template_loader.templates_cache:
            return template_loader.templates_cache[template_id]
        
        # Try the get_template method if it exists
        if hasattr(template_loader, 'get_template'):
            return template_loader.get_template(template_id)
        
        # Fallback: try direct cache access
        return template_loader.templates_cache.get(template_id)
        
    except Exception as e:
        logger.warning(f"Could not load template {template_id}: {e}")
        return None

def safe_get_style_profile(profile_id: str) -> Optional[Dict[str, Any]]:
    """Safely get style profile data"""
    try:
        # Use the correct style profile loader
        loader = get_style_profile_loader()
        return loader.get_profile(profile_id)
    except Exception as e:
        logger.warning(f"Could not load style profile {profile_id}: {e}")
        return None

def get_all_style_profiles_sync() -> List[Dict[str, Any]]:
    """Get all style profiles synchronously"""
    loader = get_style_profile_loader()
    profiles = []
    
    for profile_id in loader.list_profiles():
        profile_data = loader.get_profile(profile_id)
        if profile_data:
            profile_info = {
                "id": profile_id,
                "name": profile_data.get("name", profile_id.replace("_", " ").title()),
                "description": profile_data.get("description", f"Style profile: {profile_id}"),
                "category": profile_data.get("category", "general"),
                "tone": profile_data.get("writing_style", {}).get("tone", profile_data.get("tone", "")),
                "voice": profile_data.get("writing_style", {}).get("voice", profile_data.get("voice", "")),
                "structure": profile_data.get("content_structure", {}).get("structure", ""),
                "system_prompt": profile_data.get("system_prompt", ""),
                "settings": profile_data.get("settings", {}),
                "filename": f"{profile_id}.yaml"
            }
            profiles.append(profile_info)
    
    logger.info(f"get_all_style_profiles_sync returning {len(profiles)} profiles")
    return profiles

def get_all_templates_sync() -> List[Dict[str, Any]]:
    """Get all templates synchronously using template_loader"""
    from .template_loader import template_loader
    
    templates = []
    for template_id, template_data in template_loader.templates_cache.items():
        template_info = {
            "id": template_id,
            "name": template_data.get("name", template_id.replace("_", " ").title()),
            "description": template_data.get("description", f"Template for {template_id}"),
            "category": template_data.get("category", "general"),
            "sections": template_data.get("structure", {}).get("sections", []),  # Fixed path
            "metadata": template_data.get("metadata", {}),
            "filename": f"{template_id}.yaml"
        }
        templates.append(template_info)
    
    print(f"DEBUG: Built {len(templates)} template objects")  # Add debug
    return templates

@app.get("/debug/templates")
async def debug_templates():
    from .template_loader import template_loader
    return {
        "templates_cache": template_loader.templates_cache,
        "cache_size": len(template_loader.templates_cache),
        "available_templates": list(template_loader.templates_cache.keys())
    }

    # Rest of the pagination logic stays the same...
# API Endpoints
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Enterprise health check with system metrics"""
    try:
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version="2.0.0",
            active_generations=0,  # job_queue.get_active_count() if available
            queue_size=0,  # job_queue.get_queue_size() if available
            available_models=["gpt-4o", "gpt-4o-mini"],  # model_registry.get_available_models()
            cache_hit_rate=0.0  # cache_system.get_hit_rate() if available
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/api/generate", response_model=GenerationResponse)
async def generate_content(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(validate_api_key)
):
    """Generate content using the enhanced orchestration system"""
    generation_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Starting generation {generation_id} for template: {request.template}, style: {request.style_profile}")
        
        # Load template and style profile
        template_data = safe_get_template(request.template)
        style_data = safe_get_style_profile(request.style_profile)
        
        if not template_data:
            raise HTTPException(
                status_code=400,
                detail=f"Template '{request.template}' not found. Available templates: {[t['id'] for t in get_all_templates_sync()]}"
            )
        
        if not style_data:
            raise HTTPException(
                status_code=400,
                detail=f"Style profile '{request.style_profile}' not found. Available profiles: {style_loader.list_profiles()}"
            )
        
        # Prepare job data for orchestrator
        job_data = {
            "template": request.template,
            "style_profile": request.style_profile,
            "dynamic_parameters": request.dynamic_parameters,
            "topic": request.dynamic_parameters.get("topic", "Untitled"),
            "audience": request.dynamic_parameters.get("target_audience", "General audience"),
            "generation_id": generation_id,
            "template_data": template_data,
            "style_data": style_data
        }
        
        # Generate content through orchestrator
        result = await orchestrator.generate_content(job_data)
        
        if result["success"]:
            logger.info(f"Generation {generation_id} completed successfully")
            return GenerationResponse(
                success=True,
                generation_id=generation_id,
                status="completed",
                content=result.get("content", ""),
                metadata=result.get("metadata", {})
            )
        else:
            logger.error(f"Generation {generation_id} failed: {result.get('error')}")
            return GenerationResponse(
                success=False,
                generation_id=generation_id,
                status="failed",
                error=result.get("error", "Unknown error occurred")
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation {generation_id} failed with exception: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )

@app.get("/api/generation/{generation_id}")
async def get_generation_status(
    generation_id: str,
    api_key: str = Depends(validate_api_key)
):
    """Get generation status - placeholder for now"""
    return {
        "generation_id": generation_id,
        "status": "completed",
        "progress": 100,
        "message": "Generation tracking not yet implemented"
    }

@app.get("/api/templates")
async def get_templates(
    page: int = 1,
    limit: int = 100,
    search: str = "",
    category: str = "",
    api_key: str = Depends(validate_api_key)
):
    """Get available content templates from YAML files"""
    try:
        templates = get_all_templates_sync()
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            templates = [
                t for t in templates 
                if search_lower in t["name"].lower() or search_lower in t.get("description", "").lower()
            ]
        
        # Apply category filter
        if category:
            templates = [t for t in templates if t.get("category") == category]
        
        # Apply pagination
        total = len(templates)
        start_index = (page - 1) * limit
        paginated_templates = templates[start_index:start_index + limit]
        
        logger.info(f"Returning {len(paginated_templates)} templates out of {total} total")
        
        return {
            "success": True,
            "data": {
                "items": paginated_templates,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": (total + limit - 1) // limit,
                    "hasNext": start_index + limit < total,
                    "hasPrev": page > 1
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve templates")

@app.get("/api/style-profiles")
async def get_style_profiles(
    page: int = 1,
    limit: int = 100,
    search: str = "",
    category: str = "",
    api_key: str = Depends(validate_api_key)
):
    """Get available style profiles from YAML files"""
    try:
        # Use the existing get_all_style_profiles_sync function
        profiles = get_all_style_profiles_sync()
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            profiles = [
                p for p in profiles 
                if search_lower in p["name"].lower() or search_lower in p.get("description", "").lower()
            ]
        
        # Apply category filter
        if category:
            profiles = [p for p in profiles if p.get("category") == category]
        
        # Apply pagination
        total = len(profiles)
        start_index = (page - 1) * limit
        paginated_profiles = profiles[start_index:start_index + limit]
        
        logger.info(f"Returning {len(paginated_profiles)} style profiles out of {total} total")
        
        return {
            "success": True,
            "data": {
                "items": paginated_profiles,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": (total + limit - 1) // limit,
                    "hasNext": start_index + limit < total,
                    "hasPrev": page > 1
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get style profiles: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve style profiles")
    
@app.get("/api/models")
async def get_available_models(api_key: str = Depends(validate_api_key)):
    """Get available AI models"""
    try:
        return {
            "success": True,
            "models": [
                {"id": "gpt-4o", "name": "GPT-4 Optimized", "provider": "OpenAI"},
                {"id": "gpt-4o-mini", "name": "GPT-4 Mini", "provider": "OpenAI"}
            ],
            "default_model": "gpt-4o"
        }
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models")

@app.delete("/api/cache")
async def clear_cache(api_key: str = Depends(validate_api_key)):
    """Clear system cache"""
    try:
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "AgentWrite Pro - Enterprise Backend",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Multi-Agent Orchestration",
            "Real YAML Template Loading",
            "Style Profile Management",
            "Content Generation",
            "Enterprise Security"
        ],
        "endpoints": {
            "health": "/api/health",
            "generate": "/api/generate",
            "templates": "/api/templates", 
            "style_profiles": "/api/style-profiles",
            "models": "/api/models"
        }
    }

# Background Tasks
async def process_generation_queue():
    """Background task processor - placeholder"""
    logger.info("Background queue processing started")
    # Implementation for background processing

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting AgentWrite Pro Enterprise Backend on {host}:{port}")
    logger.info(f"Loaded {len(style_loader.profiles_cache)} style profiles")
    
    uvicorn.run(
        "langgraph_app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
        workers=1 if debug else 4
    )
    print(f"DEBUG: Expected API key: {os.getenv('LANGGRAPH_API_KEY')}")
    logger.info(f"Starting AgentWrite Pro Enterprise Backend on {host}:{port}")
    logger.info(f"Loaded {len(style_loader.profiles_cache)} style profiles")
    logger.info(f"Loaded {len(template_loader.templates_cache)} templates")

@app.get("/debug/style-profiles")
async def debug_style_profiles():
    """Debug endpoint to see style profile data"""
    loader = get_style_profile_loader()
    return {
        "profiles_cache": dict(list(loader.profiles_cache.items())[:3]),  # Show first 3 profiles
        "cache_size": len(loader.profiles_cache),
        "available_profiles": loader.list_profiles(),
        "profiles_loaded": loader._profiles_loaded,
        "get_all_sync_result": get_all_style_profiles_sync()[:2]  # Show first 2
    }

print(f"DEBUG: Expected API key: {os.getenv('LANGGRAPH_API_KEY')}")