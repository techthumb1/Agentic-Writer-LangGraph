# File: langgraph_app/integrated_server.py
import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
import json

# Import your existing infrastructure
from .integrated_workflow import integrated_workflow, WorkflowType
from .enhanced_model_registry import ModelRegistry
from .cache_system import CacheSystem
from .job_queue import JobQueue
from .semantic_search import SemanticSearch
from .style_profile_loader import StyleProfileLoader
from .server import *  # Your existing server components
from .enhanced_graph import *  # Your existing enhanced graph
from .enhanced_orchestration import *  # Your existing orchestration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AgentWrite Pro - Integrated AI Backend",
    description="Full-featured AI Content Generation with LangGraph Agents",
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

# Initialize your existing infrastructure
model_registry = ModelRegistry()
cache_system = CacheSystem()
job_queue = JobQueue()
semantic_search = SemanticSearch()
style_profile_loader = StyleProfileLoader()

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.generation_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, generation_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if generation_id:
            if generation_id not in self.generation_connections:
                self.generation_connections[generation_id] = []
            self.generation_connections[generation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, generation_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if generation_id and generation_id in self.generation_connections:
            if websocket in self.generation_connections[generation_id]:
                self.generation_connections[generation_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_generation_update(self, generation_id: str, message: dict):
        if generation_id in self.generation_connections:
            for connection in self.generation_connections[generation_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove dead connections
                    self.generation_connections[generation_id].remove(connection)

manager = ConnectionManager()

# Enhanced Pydantic models
class WorkflowSelection(BaseModel):
    workflow_type: str = Field(default="comprehensive")
    auto_detect: bool = Field(default=True)
    async_processing: bool = Field(default=False)
    priority: int = Field(default=0, ge=0, le=10)

class EnhancedGenerationRequest(BaseModel):
    prompt: Dict[str, Any]  # Your existing prompt structure
    preferences: Dict[str, Any]  # Your existing preferences
    workflow: WorkflowSelection = WorkflowSelection()
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class GenerationStatusResponse(BaseModel):
    generation_id: str
    status: str
    progress: float
    current_step: str
    estimated_completion: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class WorkflowListResponse(BaseModel):
    workflows: List[Dict[str, Any]]

# Dependency for API key validation (using your existing auth)
async def validate_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization.replace("Bearer ", "")
    expected_key = os.getenv("LANGGRAPH_API_KEY")
    
    if not expected_key or api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key

@app.get("/health")
async def enhanced_health_check():
    """Enhanced health check with infrastructure status"""
    try:
        # Check all your systems
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(),
            "version": "2.0.0",
            "services": {
                "model_registry": await model_registry.health_check(),
                "cache_system": await cache_system.health_check(),
                "job_queue": await job_queue.health_check(),
                "semantic_search": await semantic_search.health_check(),
                "style_profile_loader": await style_profile_loader.health_check(),
            },
            "available_models": model_registry.get_available_models(),
            "active_jobs": await job_queue.get_queue_status(),
            "cache_stats": await cache_system.get_stats(),
        }
        
        # Check if any service is unhealthy
        unhealthy_services = [
            service for service, status in health_status["services"].items()
            if status.get("status") != "healthy"
        ]
        
        if unhealthy_services:
            health_status["status"] = "degraded"
            health_status["unhealthy_services"] = unhealthy_services
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/generate/enhanced")
async def enhanced_generate_content(
    request: EnhancedGenerationRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(validate_api_key)
):
    """Enhanced content generation endpoint with your full agent ecosystem"""
    try:
        logger.info(f"Enhanced generation request: {request.workflow.workflow_type}")
        
        # Validate workflow type
        try:
            workflow_type = WorkflowType(request.workflow.workflow_type)
        except ValueError:
            if request.workflow.auto_detect:
                workflow_type = WorkflowType.COMPREHENSIVE
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid workflow type: {request.workflow.workflow_type}"
                )
        
        # Validate model availability
        model = request.preferences.get("model", "gpt-4-turbo")
        if not model_registry.is_model_available(model):
            available_models = model_registry.get_available_models()
            raise HTTPException(
                status_code=400,
                detail=f"Model '{model}' not available. Available: {available_models}"
            )
        
        # Prepare request for integrated workflow
        workflow_request = {
            "prompt": request.prompt,
            "preferences": request.preferences,
            "workflow_type": workflow_type.value,
            "async": request.workflow.async_processing,
            "priority": request.workflow.priority,
            "user_id": request.user_id,
            "session_id": request.session_id,
        }
        
        # Handle async processing
        if request.workflow.async_processing:
            # Generate content asynchronously
            generation_id = f"async_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(request)}"
            
            # Add background task
            background_tasks.add_task(
                process_async_generation,
                generation_id,
                workflow_request
            )
            
            return {
                "generation_id": generation_id,
                "status": "queued",
                "message": "Content generation queued for async processing",
                "estimated_completion": datetime.now().isoformat(),
                "websocket_url": f"/ws/generation/{generation_id}"
            }
        
        # Synchronous processing
        logger.info("Starting synchronous content generation")
        start_time = datetime.now()
        
        result = await integrated_workflow.generate_content(workflow_request)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Generation completed in {total_time:.2f} seconds")
        
        # Enhance result with timing
        if "metadata" in result:
            result["metadata"]["total_processing_time"] = total_time
            result["metadata"]["infrastructure_stats"] = {
                "cache_hits": result["metadata"].get("cache_hits", 0),
                "model_calls": len(result["metadata"].get("agent_steps", [])),
                "workflow_type": workflow_type.value,
            }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Enhanced content generation failed: {str(e)}"
        )

async def process_async_generation(generation_id: str, request: Dict[str, Any]):
    """Background task for async content generation"""
    try:
        # Send initial status
        await manager.send_generation_update(generation_id, {
            "type": "status_update",
            "generation_id": generation_id,
            "status": "processing",
            "progress": 0,
            "current_step": "initializing"
        })
        
        # Process with progress updates
        result = await integrated_workflow.generate_content(request)
        
        # Send completion
        await manager.send_generation_update(generation_id, {
            "type": "completion",
            "generation_id": generation_id,
            "status": result.get("status", "completed"),
            "progress": 100,
            "result": result
        })
        
    except Exception as e:
        # Send error
        await manager.send_generation_update(generation_id, {
            "type": "error",
            "generation_id": generation_id,
            "status": "error",
            "error": str(e)
        })

@app.get("/generation/status/{generation_id}")
async def get_generation_status(
    generation_id: str,
    api_key: str = Depends(validate_api_key)
) -> GenerationStatusResponse:
    """Get status of async generation"""
    try:
        status = await integrated_workflow.get_workflow_status(generation_id)
        return GenerationStatusResponse(**status)
    except Exception as e:
        logger.error(f"Failed to get generation status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve status")

@app.get("/workflows/available", response_model=WorkflowListResponse)
async def list_available_workflows(api_key: str = Depends(validate_api_key)):
    """List all available workflow types"""
    try:
        workflows = await integrated_workflow.list_available_workflows()
        return WorkflowListResponse(workflows=workflows)
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workflows")

@app.get("/infrastructure/stats")
async def get_infrastructure_stats(api_key: str = Depends(validate_api_key)):
    """Get detailed infrastructure statistics"""
    try:
        return {
            "cache_system": await cache_system.get_detailed_stats(),
            "job_queue": await job_queue.get_detailed_stats(),
            "model_registry": await model_registry.get_usage_stats(),
            "semantic_search": await semantic_search.get_stats(),
            "active_generations": len(manager.generation_connections),
            "total_connections": len(manager.active_connections),
        }
    except Exception as e:
        logger.error(f"Failed to get infrastructure stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")

@app.post("/cache/clear")
async def clear_cache(
    cache_type: str = "all",
    api_key: str = Depends(validate_api_key)
):
    """Clear cache (admin function)"""
    try:
        if cache_type == "all":
            await cache_system.clear_all()
        else:
            await cache_system.clear_by_type(cache_type)
        
        return {"message": f"Cache cleared: {cache_type}"}
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@app.post("/models/reload")
async def reload_models(api_key: str = Depends(validate_api_key)):
    """Reload model registry (admin function)"""
    try:
        await model_registry.reload()
        return {
            "message": "Model registry reloaded",
            "available_models": model_registry.get_available_models()
        }
    except Exception as e:
        logger.error(f"Failed to reload models: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload models")

# WebSocket endpoint for real-time generation updates
@app.websocket("/ws/generation/{generation_id}")
async def websocket_generation_endpoint(websocket: WebSocket, generation_id: str):
    await manager.connect(websocket, generation_id)
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            
            # Handle client commands (pause, cancel, etc.)
            try:
                command = json.loads(data)
                if command.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif command.get("type") == "cancel":
                    # Cancel generation if possible
                    await job_queue.cancel_job(generation_id)
                    await websocket.send_text(json.dumps({
                        "type": "cancelled",
                        "generation_id": generation_id
                    }))
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, generation_id)

# Global WebSocket for system updates
@app.websocket("/ws/system")
async def websocket_system_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic system stats
            await asyncio.sleep(30)  # Every 30 seconds
            
            stats = {
                "type": "system_stats",
                "timestamp": datetime.now().isoformat(),
                "queue_size": await job_queue.get_queue_size(),
                "cache_hit_rate": await cache_system.get_hit_rate(),
                "active_generations": len(manager.generation_connections),
            }
            
            await websocket.send_text(json.dumps(stats))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Legacy compatibility endpoints (for your existing frontend)
@app.post("/generate")
async def legacy_generate_content(
    request: Dict[str, Any],
    api_key: str = Depends(validate_api_key)
):
    """Legacy endpoint for backward compatibility"""
    try:
        # Convert legacy request to new format
        enhanced_request = EnhancedGenerationRequest(
            prompt=request.get("prompt", {}),
            preferences=request.get("preferences", {}),
            workflow=WorkflowSelection(
                workflow_type=request.get("workflow", "comprehensive"),
                async_processing=False
            )
        )
        
        # Use the enhanced generation
        return await enhanced_generate_content(enhanced_request, BackgroundTasks(), api_key)
        
    except Exception as e:
        logger.error(f"Legacy generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Template and Style Profile Management (integrating your existing loaders)
@app.get("/templates/list")
async def list_content_templates(api_key: str = Depends(validate_api_key)):
    """List available content templates"""
    try:
        # Use your existing template loading system
        templates = await style_profile_loader.list_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to list templates")

@app.get("/templates/{template_id}")
async def get_template_details(
    template_id: str,
    api_key: str = Depends(validate_api_key)
):
    """Get detailed template information"""
    try:
        template = await style_profile_loader.load_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve template")

@app.post("/templates/validate")
async def validate_template_structure(
    template_data: Dict[str, Any],
    api_key: str = Depends(validate_api_key)
):
    """Validate template structure"""
    try:
        validation_result = await style_profile_loader.validate_template(template_data)
        return validation_result
    except Exception as e:
        logger.error(f"Template validation failed: {e}")
        raise HTTPException(status_code=500, detail="Template validation failed")

@app.get("/style-profiles/list")
async def list_style_profiles(api_key: str = Depends(validate_api_key)):
    """List available style profiles"""
    try:
        profiles = await style_profile_loader.list_profiles()
        return {"profiles": profiles}
    except Exception as e:
        logger.error(f"Failed to list style profiles: {e}")
        raise HTTPException(status_code=500, detail="Failed to list style profiles")

@app.get("/style-profiles/{profile_id}")
async def get_style_profile_details(
    profile_id: str,
    api_key: str = Depends(validate_api_key)
):
    """Get detailed style profile information"""
    try:
        profile = await style_profile_loader.load_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Style profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get style profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve style profile")

# Semantic Search Integration
@app.post("/search/semantic")
async def semantic_search_endpoint(
    query: str,
    content_type: Optional[str] = None,
    limit: int = 10,
    api_key: str = Depends(validate_api_key)
):
    """Semantic search across your content and knowledge base"""
    try:
        results = await semantic_search.search(
            query=query,
            content_type=content_type,
            limit=limit
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(status_code=500, detail="Semantic search failed")

@app.post("/search/similar")
async def find_similar_content(
    content: str,
    threshold: float = 0.7,
    limit: int = 5,
    api_key: str = Depends(validate_api_key)
):
    """Find similar content using semantic similarity"""
    try:
        similar = await semantic_search.find_similar(
            content=content,
            threshold=threshold,
            limit=limit
        )
        return {"similar_content": similar}
    except Exception as e:
        logger.error(f"Similar content search failed: {e}")
        raise HTTPException(status_code=500, detail="Similar content search failed")

# Analytics and Reporting
@app.get("/analytics/generation-stats")
async def get_generation_analytics(
    timeframe: str = "7d",
    api_key: str = Depends(validate_api_key)
):
    """Get generation analytics and statistics"""
    try:
        stats = await job_queue.get_analytics(timeframe)
        return {
            "timeframe": timeframe,
            "stats": stats,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@app.get("/analytics/model-usage")
async def get_model_usage_stats(
    timeframe: str = "7d",
    api_key: str = Depends(validate_api_key)
):
    """Get model usage statistics"""
    try:
        usage_stats = await model_registry.get_usage_analytics(timeframe)
        return {
            "timeframe": timeframe,
            "model_usage": usage_stats,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get model usage stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve model usage")

# Admin endpoints for your infrastructure
@app.post("/admin/restart-service")
async def restart_service(
    service_name: str,
    api_key: str = Depends(validate_api_key)
):
    """Restart a specific service (admin only)"""
    try:
        # Map service names to restart functions
        service_map = {
            "cache": cache_system.restart,
            "job_queue": job_queue.restart,
            "semantic_search": semantic_search.restart,
            "style_loader": style_profile_loader.restart,
        }
        
        if service_name not in service_map:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown service: {service_name}"
            )
        
        await service_map[service_name]()
        
        return {"message": f"Service {service_name} restarted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restart service {service_name}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to restart service: {service_name}"
        )

@app.get("/admin/system-config")
async def get_system_config(api_key: str = Depends(validate_api_key)):
    """Get current system configuration"""
    try:
        config = {
            "model_registry": await model_registry.get_config(),
            "cache_system": await cache_system.get_config(),
            "job_queue": await job_queue.get_config(),
            "semantic_search": await semantic_search.get_config(),
            "style_profile_loader": await style_profile_loader.get_config(),
            "workflow_settings": {
                "available_workflows": [wf.value for wf in WorkflowType],
                "default_workflow": WorkflowType.COMPREHENSIVE.value,
                "max_concurrent_jobs": int(os.getenv("MAX_CONCURRENT_JOBS", "10")),
                "default_timeout": int(os.getenv("DEFAULT_TIMEOUT", "600")),
            }
        }
        return config
    except Exception as e:
        logger.error(f"Failed to get system config: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system config")

# Integration with your existing publishing system
@app.post("/publish/content")
async def publish_generated_content(
    content_id: str,
    publication_config: Dict[str, Any],
    api_key: str = Depends(validate_api_key)
):
    """Publish generated content using your existing publisher"""
    try:
        # Get the content from cache or database
        content = await cache_system.get(f"content:{content_id}")
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Use your existing publisher agent
        publisher = integrated_workflow.publisher
        publication_result = await publisher.publish_content(
            content=content["final_content"],
            config=publication_config,
            metadata=content.get("metadata", {})
        )
        
        return {
            "publication_id": publication_result.get("publication_id"),
            "published_urls": publication_result.get("urls", []),
            "status": "published",
            "published_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Publication failed: {e}")
        raise HTTPException(status_code=500, detail="Content publication failed")

# Batch processing endpoint
@app.post("/batch/generate")
async def batch_generate_content(
    requests: List[EnhancedGenerationRequest],
    background_tasks: BackgroundTasks,
    api_key: str = Depends(validate_api_key)
):
    """Batch content generation"""
    try:
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Add all requests to the job queue
        job_ids = []
        for i, request in enumerate(requests):
            job_id = f"{batch_id}_{i:03d}"
            
            workflow_request = {
                "prompt": request.prompt,
                "preferences": request.preferences,
                "workflow_type": request.workflow.workflow_type,
                "batch_id": batch_id,
                "job_id": job_id,
            }
            
            # Add to job queue with priority
            await job_queue.add_job(
                job_type="content_generation",
                job_data=workflow_request,
                priority=request.workflow.priority,
                job_id=job_id
            )
            
            job_ids.append(job_id)
        
        return {
            "batch_id": batch_id,
            "job_ids": job_ids,
            "total_jobs": len(requests),
            "status": "queued",
            "estimated_completion": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        raise HTTPException(status_code=500, detail="Batch generation failed")

@app.get("/batch/{batch_id}/status")
async def get_batch_status(
    batch_id: str,
    api_key: str = Depends(validate_api_key)
):
    """Get batch processing status"""
    try:
        batch_status = await job_queue.get_batch_status(batch_id)
        return batch_status
    except Exception as e:
        logger.error(f"Failed to get batch status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve batch status")

# Root endpoint with full system information
@app.get("/")
async def enhanced_root():
    """Enhanced root endpoint with complete system information"""
    return {
        "service": "AgentWrite Pro - Integrated AI Backend",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Multi-Agent Content Generation",
            "Real-time Progress Tracking",
            "Semantic Search Integration",
            "Advanced Caching System",
            "Job Queue Management",
            "Style Profile Loading",
            "Batch Processing",
            "WebSocket Support",
            "Legacy API Compatibility"
        ],
        "workflows": [wf.value for wf in WorkflowType],
        "endpoints": {
            "generation": [
                "/generate/enhanced",
                "/generate",
                "/batch/generate"
            ],
            "management": [
                "/templates/list",
                "/style-profiles/list",
                "/generation/status/{id}"
            ],
            "analytics": [
                "/analytics/generation-stats",
                "/analytics/model-usage",
                "/infrastructure/stats"
            ],
            "search": [
                "/search/semantic",
                "/search/similar"
            ],
            "admin": [
                "/admin/restart-service",
                "/admin/system-config",
                "/cache/clear",
                "/models/reload"
            ],
            "realtime": [
                "/ws/generation/{id}",
                "/ws/system"
            ]
        },
        "infrastructure": {
            "agents": [
                "PlannerAgent", "ResearcherAgent", "WriterAgent", 
                "EditorAgent", "SEOAgent", "FormatterAgent",
                "ImageAgent", "CodeAgent", "PublisherAgent"
            ],
            "systems": [
                "ModelRegistry", "CacheSystem", "JobQueue",
                "SemanticSearch", "StyleProfileLoader"
            ]
        }
    }

# Startup event to initialize your systems
@app.on_event("startup")
async def startup_event():
    """Initialize all systems on startup"""
    logger.info("Starting AgentWrite Pro Integrated Backend...")
    
    try:
        # Initialize your existing infrastructure
        await model_registry.initialize()
        await cache_system.initialize()
        await job_queue.initialize()
        await semantic_search.initialize()
        await style_profile_loader.initialize()
        
        # Initialize the integrated workflow
        logger.info("All systems initialized successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise e

# Shutdown event to cleanup
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AgentWrite Pro Integrated Backend...")
    
    try:
        # Cleanup your systems
        await model_registry.cleanup()
        await cache_system.cleanup()
        await job_queue.cleanup()
        await semantic_search.cleanup()
        await style_profile_loader.cleanup()
        
        logger.info("Shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

if __name__ == "__main__":
    # Configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    workers = int(os.getenv("WORKERS", "1"))
    
    logger.info(f"Starting AgentWrite Pro Integrated Backend on {host}:{port}")
    logger.info(f"Debug mode: {debug}, Workers: {workers}")
    
    uvicorn.run(
        "langgraph_app.integrated_server:app",
        host=host,
        port=port,
        reload=debug,
        workers=workers if not debug else 1,
        log_level="info",
        access_log=True
    )