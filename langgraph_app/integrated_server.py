# langgraph_app/integrated_server_clean.py
"""
Clean, refactored version of integrated_server.py
Uses existing modules and extracted components
"""

import uuid
import logging
from datetime import datetime
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from langgraph_app.agents.mcp_enhanced_agents import GenerateRequest

# Use your existing modules
from .config.settings import settings
from .config.auth import verify_api_key
from .core.content_manager import content_manager
from .monitoring.metrics import custom_registry, REQUEST_COUNT, REQUEST_DURATION
from .schemas import *  # Your existing Pydantic models
from .mcp_server_extension import execute_enhanced_mcp_generation
from .mcp_server_extension import enhanced_mcp_manager
from .enhanced_model_registry import get_model

# Import your existing systems
try:
    from .mcp_server_extension import (
        initialize_mcp_for_existing_server,
        cleanup_mcp_for_existing_server,
        MCPGenerationRequest,
    )
except ImportError as e:
    logging.error(f"MCP modules not available: {e}")
    raise SystemExit("ENTERPRISE FAILURE: MCP modules not available")

try:
    from .universal_system.universal_integration import LangGraphUniversalIntegration
except ImportError as e:
    logging.error(f"Universal System not available: {e}")
    raise SystemExit("ENTERPRISE FAILURE: Universal System not available")

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management - ENTERPRISE: All components must initialize"""
    logger.info("Starting WriterzRoom API - ENTERPRISE MODE")
    
    # Initialize application state
    app.state.generation_tasks = {}
    app.state.mcp_evidence_store = {}
    
    # Initialize model registry
    try:
        llm = get_model("writer")
        logger.info("✅ Model registry initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize model registry: {str(e)}")
        raise SystemExit(f"ENTERPRISE MODE: Model registry initialization failed: {e}")
    
    # Initialize MCP
    try:
        mcp_success = await initialize_mcp_for_existing_server(app)
        if not mcp_success:
            raise SystemExit("ENTERPRISE MODE: MCP initialization returned failure status")
        app.state.mcp_available = True
        logger.info("✅ MCP initialization successful")
    except Exception as e:
        logger.error(f"❌ MCP initialization error: {e}")
        raise SystemExit(f"ENTERPRISE MODE: MCP initialization failed: {e}")
    
    # Initialize Universal system
    try:
        app.state.universal_integration = LangGraphUniversalIntegration()
        logger.info("✅ Universal Integration initialized successfully")
    except Exception as e:
        logger.error(f"❌ Universal Integration initialization error: {e}")
        raise SystemExit(f"ENTERPRISE MODE: Universal Integration initialization failed: {e}")
    
    # Validate that templates and profiles can be loaded
    try:
        templates = content_manager.load_templates()
        profiles = content_manager.load_style_profiles()
        if len(templates) == 0:
            raise SystemExit("ENTERPRISE MODE: No templates loaded - system cannot operate")
        if len(profiles) == 0:
            raise SystemExit("ENTERPRISE MODE: No style profiles loaded - system cannot operate")
        logger.info(f"✅ Loaded {len(templates)} templates and {len(profiles)} style profiles")
    except Exception as e:
        logger.error(f"❌ Template/Profile loading error: {e}")
        raise SystemExit(f"ENTERPRISE MODE: Template/Profile loading failed: {e}")
    
    logger.info("✅ Server initialization complete - All enterprise requirements met")
    
    yield
    
    # Cleanup
    try:
        await cleanup_mcp_for_existing_server(app)
        logger.info("✅ MCP cleanup completed")
    except Exception as e:
        logger.error(f"❌ MCP cleanup error: {e}")
    
    logger.info("🛑 Shutting down WriterzRoom API")

# FastAPI application
app = FastAPI(
    title="WriterzRoom API - Enterprise Edition",
    description="Enterprise-grade AI-powered content generation with unified MCP integration",
    version="2.0.0-enterprise",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Generation-Time"]
)

# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    requestId = str(uuid.uuid4())
    request.state.requestId = requestId
    
    start_time = datetime.now()
    
    response = await call_next(request)
    
    duration = (datetime.now() - start_time).total_seconds()
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(duration)
    
    response.headers["X-Request-ID"] = requestId
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    logger.info(f"Request completed: {request.method} {request.url.path} {response.status_code} {duration:.3f}s [{requestId}]")
    
    return response

# Root endpoint
@app.get("/")
async def root(request: Request):
    """API root endpoint"""
    return {
        "name": "WriterzRoom API - Enterprise Edition",
        "version": "2.0.0-enterprise", 
        "status": "operational",
        "mode": "enterprise",
        "requestId": request.state.requestId
    }

# Health endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(custom_registry), media_type=CONTENT_TYPE_LATEST)

# Template endpoints  
@app.get("/api/templates")
async def list_templates(authenticated: bool = Depends(verify_api_key)):
    """List all available content templates"""
    try:
        templates = content_manager.load_templates()
        return {
            "success": True,
            "data": {
                "items": [template.dict() for template in templates],
                "count": len(templates)
            }
        }
    except Exception as e:
        logger.error(f"Failed to load templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load templates")

@app.get("/api/style-profiles")
async def list_style_profiles(authenticated: bool = Depends(verify_api_key)):
    """List all available style profiles"""
    try:
        profiles = content_manager.load_style_profiles()
        return {
            "success": True,
            "data": {
                "items": [profile.dict() for profile in profiles],
                "count": len(profiles)
            }
        }
    except Exception as e:
        logger.error(f"Failed to load style profiles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load style profiles")

# Generation endpoints - simplified versions using your existing functions
@app.post("/api/generate")
async def generate_content(
    request_data: GenerateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    authenticated: bool = Depends(verify_api_key)
):
    """Generate content using existing MCP integration"""
    requestId = str(uuid.uuid4())
    
    try:
        # Load templates and profiles
        templates = content_manager.load_templates()
        profiles = content_manager.load_style_profiles()
        
        # Find template and profile
        template = next((t for t in templates if t.id == request_data.template.replace('.yaml', '')), None)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {request_data.template}")
        
        profile = next((p for p in profiles if p.id == request_data.style_profile.replace('.yaml', '')), None)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Style profile not found: {request_data.style_profile}")
        
        # Initialize status
        initial_status = {
            "requestId": requestId,
            "status": "pending",
            "progress": 0.0,
            "current_step": "Initializing generation...",
            "content": "",
            "metadata": {
                "template": template.name,
                "style_profile": profile.name,
                "started_at": datetime.now().isoformat(),
                "enterprise_mode": True
            },
            "created_at": datetime.now().isoformat()
        }
        
        # Store in app state
        if not hasattr(app.state, 'generation_tasks'):
            app.state.generation_tasks = {}
        app.state.generation_tasks[requestId] = initial_status
        
        # Use your existing MCP integration
        background_tasks.add_task(
            execute_enhanced_mcp_generation,
            requestId,
            template.dict(),
            profile.dict(),
            app.state,
            {"enable_mcp": True, "dynamic_parameters": request_data.dynamic_parameters}
        )
        
        logger.info(f"Content generation initiated [requestId={requestId}, template={template.name}]")
        
        return {
            "success": True,
            "data": {
                "requestId": requestId,
                "status": "pending",
                "metadata": initial_status["metadata"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start content generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start content generation")

@app.get("/api/generate/{requestId}")
async def get_generation_result(requestId: str, request: Request, authenticated: bool = Depends(verify_api_key)):
    """Get generation status or final result"""
    if not hasattr(app.state, 'generation_tasks') or requestId not in app.state.generation_tasks:
        raise HTTPException(status_code=404, detail="Generation request not found")
    
    status = app.state.generation_tasks[requestId]
    
    return {
        "success": True,
        "data": status
    }

# Legacy compatibility endpoint
@app.get("/status/{requestId}")
async def get_generation_status_legacy(requestId: str, request: Request):
    """Legacy status endpoint for backward compatibility"""
    try:
        if not hasattr(app.state, 'generation_tasks') or requestId not in app.state.generation_tasks:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "Generation request not found",
                    "timestamp": datetime.now().isoformat(),
                    "requestId": requestId
                }
            )
        
        status = app.state.generation_tasks[requestId]
        
        response_data = {
            "success": True,
            "data": status,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "requestId": requestId
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Legacy status check failed [requestId={requestId}, error={str(e)}]")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Status check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "requestId": requestId
            }
        )

# Content management endpoints
@app.get("/api/content")
async def list_content(authenticated: bool = Depends(verify_api_key)):
    """List all content items"""
    try:
        content_items = content_manager.get_content_items()
        
        # Calculate stats
        total_views = sum(item.get('views', 0) for item in content_items)
        published_count = sum(1 for item in content_items if item.get('status') == 'published')
        draft_count = len(content_items) - published_count
        
        return {
            "content": content_items,
            "totalViews": total_views,
            "stats": {
                "total": len(content_items),
                "published": published_count,
                "drafts": draft_count,
                "types": len(set(item['type'] for item in content_items))
            }
        }
        
    except Exception as e:
        logger.error(f"List content error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list content")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(authenticated: bool = Depends(verify_api_key)):
    """Get dashboard statistics"""
    try:
        content_items = content_manager.get_content_items()
        
        # Calculate basic stats
        stats = {
            "total": len(content_items),
            "totalContent": len(content_items),
            "drafts": sum(1 for item in content_items if item.get('status') == 'draft'),
            "published": sum(1 for item in content_items if item.get('status') == 'published'),
            "views": sum(item.get('views', 0) for item in content_items),
            "recentContent": content_items[:5],  # Most recent 5
            "recentActivity": [
                {
                    "id": f"activity-{item['id']}",
                    "type": "created" if item["status"] == "draft" else "published",
                    "description": f"{'Published' if item['status'] == 'published' else 'Created'} \"{item['title']}\"",
                    "timestamp": item["updatedAt"]
                }
                for item in content_items[:5]
            ]
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

# Development/Debug endpoints (only in development)
if settings.ENVIRONMENT == "development":
    @app.get("/debug/enterprise-status")
    async def debug_enterprise_status(request: Request, authenticated: bool = Depends(verify_api_key)):
        """Debug enterprise system status"""
        try:
            mcp_available = getattr(app.state, 'mcp_available', False)
            universal_available = hasattr(app.state, 'universal_integration') and app.state.universal_integration is not None
            
            template_count = len(content_manager.load_templates())
            profile_count = len(content_manager.load_style_profiles())
            
            return {
                "success": True,
                "data": {
                    "enterprise_mode": True,
                    "system_status": {
                        "mcp_integration": {
                            "available": mcp_available,
                            "status": "operational" if mcp_available else "failed"
                        },
                        "universal_system": {
                            "available": universal_available,
                            "status": "operational" if universal_available else "failed"
                        },
                        "template_system": {
                            "templates_loaded": template_count,
                            "status": "operational" if template_count > 0 else "degraded"
                        },
                        "style_system": {
                            "profiles_loaded": profile_count,
                            "status": "operational" if profile_count > 0 else "degraded"
                        }
                    },
                    "environment": {
                        "mode": settings.ENVIRONMENT,
                        "api_key_configured": bool(settings.API_KEY)
                    },
                    "metrics": {
                        "active_generations": len(getattr(app.state, 'generation_tasks', {})),
                        "total_templates": template_count,
                        "total_profiles": profile_count
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Enterprise status check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

if __name__ == "__main__":
    logger.info("Starting WriterzRoom API Server - ENTERPRISE MODE")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Key: {'✅ Configured' if settings.API_KEY else '❌ Missing'}")
    logger.info(f"MCP Integration: ✅ Required (Enterprise)")
    logger.info(f"Universal System: ✅ Required (Enterprise)")
    logger.info(f"Authentication: ✅ Always Required (Enterprise)")
    logger.info("=" * 60)
    logger.info("ENTERPRISE MODE: All systems must be operational")
    logger.info("No fallbacks - Fail fast on missing dependencies")
    
    uvicorn.run(
        "integrated_server_clean:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=(settings.ENVIRONMENT == "development"),
        access_log=True,
        log_level="info"
    )