"""
WriterzRoom API — Refactored Enterprise Edition
This server uses the new core modules for configuration, state, and graph management,
ensuring a deterministic, asynchronous, and "fail-fast" enterprise architecture.
"""

import uuid
import time
import logging
import yaml
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from pathlib import Path
import os
import json
import frontmatter
from collections import defaultdict
from fastapi import APIRouter
from langgraph_app.core.circuit_breaker import get_circuit_breaker
from langgraph_app.core.provider_pool import get_provider_pool


# In-memory metrics tracking
content_metrics = defaultdict(lambda: {"views": 0, "unique_sessions": set(), "last_viewed": None})
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from .analytics_endpoints import router as analytics_router
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from langgraph_app.database.models import GenerationLog, get_db
# --- Core Refactored Imports ---
from .core.config_manager import ConfigManager, ConfigManagerError
from .graph.workflow import get_compiled_graph
from langgraph_app.core.provider_pool import initialize_provider_pool_from_env

from .core.state import EnrichedContentState
from .core.schemas import Template, StyleProfile
from .core.types import ContentSpec

# --- Existing Integrations ---
from .health_routes import router as health_router
#from .content_routes import register_content_routes

debug_router = APIRouter(prefix="/api/debug", tags=["debug"])


def _normalize_parameters(yaml_obj: Dict[str, Any]) -> Dict[str, Any]:
    """Transform YAML inputs into frontend parameters format"""
    params_data = yaml_obj.get("parameters") or yaml_obj.get("inputs") or {}
    out = {}

    if isinstance(params_data, dict):
        for key, spec in params_data.items():
            if not isinstance(spec, dict):
                spec = {"default": spec}
            
            default_val = spec.get("default")
            inferred_type = "string"
            if isinstance(default_val, bool):
                inferred_type = "boolean"
            elif isinstance(default_val, (int, float)):
                inferred_type = "number"
            elif spec.get("options"):
                inferred_type = "select"
            elif key.endswith("_description") or key.endswith("_text"):
                inferred_type = "textarea"

            out[key] = {
                "name": key,
                "label": spec.get("label", key.replace("_", " ").title()),
                "type": spec.get("type", inferred_type),
                "required": bool(spec.get("required", False)),
                "default": default_val,
                "description": spec.get("description", ""),
                "placeholder": spec.get("placeholder", ""),
                "options": spec.get("options") if spec.get("options") else None,
            }
    return out

# ====== Logging ======
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("writerzroom.server")

# ====== Enterprise Configuration & Auth ======
API_KEY = os.getenv("LANGGRAPH_API_KEY", "your_default_dev_key")
security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme != "Bearer" or credentials.credentials != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

# ====== Pydantic Models for API Layer ======
class GenerateRequest(BaseModel):
    template_id: Optional[str] = Field(None, min_length=1)
    template: Optional[str] = Field(None, min_length=1)
    style_profile_id: Optional[str] = Field(None, min_length=1) 
    style_profile: Optional[str] = Field(None, min_length=1)
    user_input: Dict[str, Any] = Field(default_factory=dict)
    generation_settings: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def get_template(self) -> str:
        return self.template_id or self.template or ""
    
    def get_style(self) -> str:
        return self.style_profile_id or self.style_profile or ""

# ====== Application Lifespan (Startup/Shutdown) ======
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting WriterzRoom API — Refactored Enterprise Mode")
    try:
        data_path = Path(__file__).resolve().parents[2] / "data"
        app.state.config_manager = ConfigManager(base_dir=data_path)
        logger.info("✅ ConfigManager initialized and all configurations validated.")
    except ConfigManagerError as e:
        logger.error(f"❌ CRITICAL: Failed to initialize ConfigManager. {e}")
        # In a real scenario, this would prevent the app from starting.
        # For this example, we'll allow it but log a critical error.
        raise RuntimeError(f"Could not start server: {e}") from e

    app.state.generation_tasks = {}
    yield
    logger.info("Shutting down WriterzRoom API.")

# ====== FastAPI App Initialization ======
app = FastAPI(title="WriterzRoom Orchestrator", version="2.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health_router)
app.include_router(analytics_router)
app.include_router(debug_router, tags=["Debug"])  # ← Add this before "return app"
    

@app.get("/api/dashboard/stats")
async def get_dashboard_stats_direct():
    """Direct stats endpoint for frontend - reads from filesystem JSON"""
    from pathlib import Path
    from datetime import datetime
    
    base_dir = Path("generated_content")
    if not base_dir.exists():
        return {
            "total_content": 0,
            "published": 0,
            "drafts": 0,
            "views": 0,
            "recent_content": [],
            "recent_activity": []
        }
    
    content_list = []
    
    # Collect all JSON files
    json_files = list(base_dir.glob("week_*/*.json"))
    
    # Sort by file modification time (most recent first)
    json_files = sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get timestamp from file stat if not in data
            file_mtime = datetime.fromtimestamp(json_file.stat().st_mtime).isoformat()
            
            content_list.append({
                "id": data.get("id", json_file.stem),
                "title": data.get("title", json_file.stem.replace("_", " ").title()),
                "subtitle": data.get("subtitle", ""),
                "status": data.get("status", "completed"),
                "type": data.get("template_id", "article"),
                "updated_at": data.get("timestamp", file_mtime),
                "views": data.get("views", 0)
            })
        except Exception as e:
            logger.error(f"Error reading {json_file}: {e}")
            continue
    
    # Already sorted by file mtime, just take top 5
    recent_content = content_list[:5]
    
    # Stats
    total = len(content_list)
    published = sum(1 for c in content_list if c["status"] in ["published", "completed"])
    drafts = sum(1 for c in content_list if c["status"] == "draft")
    views = sum(c["views"] for c in content_list)
    
    # Recent activity with unique timestamps and descriptions
    recent_activity = [
        {
            "id": c["id"],
            "action": "created",
            "description": f"Created {c['title']}",
            "timestamp": c["updated_at"],
            "actor": "system"
        } for c in recent_content
    ]
    
    return {
        "total_content": total,
        "published": published,
        "drafts": drafts,
        "views": views,
        "recent_content": recent_content,
        "recent_activity": recent_activity
    }
@app.get("/api/dashboard/activity")
async def get_dashboard_activity():
    """Recent activity with proper MD parsing"""
    from pathlib import Path
    import re
    
    base_dir = Path("generated_content")
    activities = []
    
    for week_dir in sorted(base_dir.iterdir(), reverse=True):
        if not week_dir.is_dir() or not week_dir.name.startswith("week_"):
            continue
        
        for file_path in week_dir.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if not match:
                    continue
                
                frontmatter = {}
                for line in match.group(1).strip().split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        frontmatter[key.strip()] = val.strip().strip('"').strip("'")
                
                activities.append({
                    "id": f"activity-{file_path.stem}",
                    "type": "published" if frontmatter.get('status') == 'published' else "created",
                    "description": f"{'Published' if frontmatter.get('status') == 'published' else 'Created'} \"{frontmatter.get('title', 'Untitled')}\"",
                    "timestamp": frontmatter.get('createdAt', datetime.now().isoformat())
                })
            except:
                continue
    
    # Sort and return latest 10
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"activities": activities[:10]}

@app.get("/api/content")
async def list_content():
    """List all generated content with real metadata"""
    from pathlib import Path
    
    base_dir = Path("generated_content")
    if not base_dir.exists():
        return {"content": [], "total_views": 0, "stats": {"total": 0, "published": 0, "drafts": 0}}
    
    content_list = []
    seen_ids = set()
    total_views = 0
    published = 0
    drafts = 0
    
    for week_dir in sorted(base_dir.iterdir(), reverse=True):
        if not week_dir.is_dir() or not week_dir.name.startswith("week_"):
            continue
        
        # Process JSON files
        for file_path in week_dir.glob("*.json"):
            content_id = file_path.stem
            if content_id in seen_ids:
                continue
            seen_ids.add(content_id)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                title = data.get('title', 'Untitled')
                subtitle = data.get('subtitle', '')
                status = data.get('status', 'completed')
                template_type = data.get('template_id', 'article')
                style_profile = data.get('style_profile', '')
                created_at = data.get('timestamp', datetime.now().isoformat())
                views = data.get('views', 0)
                
                total_views += views
                
                if status == "published":
                    published += 1
                else:
                    drafts += 1
                
                content_list.append({
                    "id": content_id,
                    "title": title,
                    "subtitle": subtitle,
                    "status": status,
                    "created_at": created_at,
                    "updated_at": created_at,
                    "template_type": template_type,
                    "style_profile": style_profile,
                    "views": views
                })
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue
    
    return {
        "content": content_list,
        "total_views": total_views,
        "stats": {"total": len(content_list), "published": published, "drafts": drafts}
    }

# ====== Background Task for Content Generation ======
@debug_router.get("/circuit-breaker-status")
async def get_circuit_breaker_status():
    """
    Get current circuit breaker status for all providers.
    
    Returns:
        Dict with status for anthropic, openai, tavily providers
    
    Example response:
    {
        "anthropic": {
            "provider": "anthropic",
            "state": "closed",
            "failure_count": 0,
            "last_failure": null,
            "can_execute": true
        },
        "openai": {...},
        "tavily": {...}
    }
    """
    cb = get_circuit_breaker()
    
    providers = ["anthropic", "openai", "tavily"]
    
    status = {}
    for provider in providers:
        status[provider] = cb.get_status(provider)
    
    return {
        "circuit_breakers": status,
        "timestamp": datetime.now().isoformat()
    }


@debug_router.get("/provider-pool-status")
async def get_provider_pool_status():
    """
    Get provider pool status showing API key distribution.
    
    Returns:
        Dict with key pool status for all providers
    
    Example response:
    {
        "anthropic": {
            "total_keys": 3,
            "enabled_keys": 3,
            "disabled_keys": 0,
            "keys": [
                {
                    "name": "anthropic_primary",
                    "priority": 10,
                    "enabled": true,
                    "request_count": 1523
                },
                ...
            ]
        },
        ...
    }
    """
    pool = get_provider_pool()
    
    return {
        "provider_pools": pool.get_all_status(),
        "timestamp": datetime.now().isoformat()
    }


@debug_router.post("/circuit-breaker/{provider}/force-close")
async def force_close_circuit(provider: str):
    """
    Manually close a circuit breaker (admin/emergency use).
    
    Args:
        provider: "anthropic", "openai", or "tavily"
    
    Returns:
        Success message
    """
    cb = get_circuit_breaker()
    
    if provider not in ["anthropic", "openai", "tavily"]:
        return {"error": f"Invalid provider: {provider}"}, 400
    
    cb.force_close(provider)
    
    return {
        "message": f"Circuit breaker for {provider} manually closed",
        "new_status": cb.get_status(provider),
        "timestamp": datetime.now().isoformat()
    }


@debug_router.post("/circuit-breaker/{provider}/force-open")
async def force_open_circuit(provider: str):
    """
    Manually open a circuit breaker (admin/maintenance use).
    
    Args:
        provider: "anthropic", "openai", or "tavily"
    
    Returns:
        Success message
    """
    cb = get_circuit_breaker()
    
    if provider not in ["anthropic", "openai", "tavily"]:
        return {"error": f"Invalid provider: {provider}"}, 400
    
    cb.force_open(provider)
    
    return {
        "message": f"Circuit breaker for {provider} manually opened",
        "new_status": cb.get_status(provider),
        "timestamp": datetime.now().isoformat()
    }


@debug_router.get("/system-health")
async def get_system_health():
    """
    Comprehensive system health check including circuit breakers and provider pools.
    
    Returns:
        Overall system health status
    """
    cb = get_circuit_breaker()
    pool = get_provider_pool()
    
    # Check circuit breaker health
    circuit_status = {}
    all_circuits_healthy = True
    
    for provider in ["anthropic", "openai", "tavily"]:
        status = cb.get_status(provider)
        circuit_status[provider] = status
        
        if status["state"] == "open":
            all_circuits_healthy = False
    
    # Check provider pool health
    pool_status = pool.get_all_status()
    all_pools_healthy = True
    
    for provider, status in pool_status.items():
        if status["enabled_keys"] == 0:
            all_pools_healthy = False
    
    # Overall health
    overall_health = "healthy" if (all_circuits_healthy and all_pools_healthy) else "degraded"
    
    if not all_circuits_healthy:
        overall_health = "unhealthy"
    
    return {
        "overall_health": overall_health,
        "circuit_breakers": {
            "healthy": all_circuits_healthy,
            "status": circuit_status
        },
        "provider_pools": {
            "healthy": all_pools_healthy,
            "status": pool_status
        },
        "timestamp": datetime.now().isoformat()
    }


async def run_generation_workflow(request_id: str, initial_state: EnrichedContentState):
    """Invokes the main LangGraph graph to run the content generation pipeline."""
    logger.info(f"[{request_id}] Starting background generation workflow.")
    app.state.generation_tasks[request_id] = {
        "status": "running", 
        "progress": 0.1, 
        "started_at": datetime.now().isoformat()
    }

    content = ""
    title = ""
    subtitle = ""

    try:
        final_state = None
        graph = get_compiled_graph()
        async for output in graph.astream(initial_state, {"recursion_limit": 100}):
            final_state = output

        if not final_state:
            raise RuntimeError("Graph execution finished without a final state.")

        # Extract final state data
        last_node = list(final_state.keys())[-1]
        final_state_data = final_state[last_node]
        
        # Extract content
        if isinstance(final_state_data, dict):
            content = final_state_data.get("final_content") or final_state_data.get("content", "")
        else:
            content = getattr(final_state_data, "final_content", None) or getattr(final_state_data, "content", "")

        # Extract title and subtitle from YAML frontmatter
        if content:
            lines = content.split('\n')
            in_frontmatter = False
            frontmatter_title = ""
            frontmatter_description = ""
            
            for line in lines:
                stripped = line.strip()
                
                if stripped == '---':
                    in_frontmatter = not in_frontmatter
                    if not in_frontmatter:  # End of frontmatter
                        break
                    continue
                
                if in_frontmatter:
                    if stripped.startswith('title:'):
                        frontmatter_title = stripped.replace('title:', '').strip()
                    elif stripped.startswith('description:'):
                        frontmatter_description = stripped.replace('description:', '').strip()
            
            # Build title from template name + topic
            # Use template name as title, frontmatter as subtitle
            template_name = initial_state.template_config.get("name", "Content")
            title = template_name
            
            if frontmatter_title:
                subtitle = frontmatter_title.strip('"').strip("'").split('|')[0].strip()
            elif frontmatter_description:
                subtitle = frontmatter_description.strip('"').strip("'")
            else:
                subtitle = ""
            
            subtitle = subtitle[:200] if subtitle else ""
        # Fallback if no title extracted
        if not title:
            template_name = initial_state.template_config.get("name", "Content")
            title = f"Generated Content | {template_name}"

        # Fallback subtitle from content body
        if not subtitle and content:
            # Skip frontmatter, get first meaningful line
            lines = content.split('\n')
            in_frontmatter = False
            for line in lines:
                stripped = line.strip()
                if stripped == '---':
                    in_frontmatter = not in_frontmatter
                    continue
                if not in_frontmatter and stripped and not stripped.startswith('#'):
                    subtitle = stripped[:150]
                    if len(stripped) > 150:
                        subtitle += "..."
                    break


        # Save to database
        from .database.models import GenerationLog, SessionLocal
        db = SessionLocal()
        try:
            log = GenerationLog(
                template_id=initial_state.template_config.get("id", "unknown"),
                style_profile_id=initial_state.style_config.get("id", "unknown"),
                word_count=len(content.split()),
                generation_time_seconds=0,
                success=True
            )
            db.add(log)
            db.commit()
        except Exception as db_error:
            logger.error(f"Failed to save to database: {db_error}")
            db.rollback()
        finally:
            db.close()

        # Save to filesystem
        from pathlib import Path
        import json
        
        week_num = datetime.now().isocalendar()[1]
        output_dir = Path(f"generated_content/week_{week_num}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        import uuid
        slug = title.lower().replace(" ", "_").replace("/", "_").replace("|", "").replace(":", "")[:50]
        unique_id = str(uuid.uuid4())[:8]
        file_id = f"{slug}_{unique_id}"
        output_file = output_dir / f"{file_id}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "id": file_id,
                "title": title,
                "subtitle": subtitle,
                "content": content,
                "final_content": content,
                "template_id": initial_state.template_config.get("id"),
                "style_profile_id": initial_state.style_config.get("id"),
                "style_profile": initial_state.style_config.get("name"),
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "views": 0,
                "planning_output": {
                    "content_strategy": {"subtitle": subtitle, "preview": subtitle}
                }
            }, f, indent=2)
        
        logger.info(f"[{request_id}] Content saved to {output_file} - Title: {title} | Subtitle: {subtitle}")

        # ✅ NEW: Sync to frontend database
        import requests
        import os
        
        try:
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            api_key = os.getenv("LANGGRAPH_API_KEY")
            
            # Get user_id from dynamic_parameters or environment
            user_id = initial_state.dynamic_parameters.get("user_id") or os.getenv("SERVICE_USER_ID")
            
            if not user_id:
                logger.warning(f"[{request_id}] No user_id for database sync - skipping")
            else:
                sync_response = requests.post(
                    f"{frontend_url}/api/content",
                    headers={
                        "Content-Type": "application/json",
                        "x-writerzroom-key": api_key
                    },
                    json={
                        "userId": user_id,
                        "title": title,
                        "content": content,
                        "contentHtml": "",
                        "status": "completed",
                        "type": initial_state.template_config.get("template_type", "article"),
                        "metadata": {
                            "file_id": file_id,
                            "template_id": initial_state.template_config.get("id"),
                            "style_profile_id": initial_state.style_config.get("id"),
                            "subtitle": subtitle,
                            "request_id": request_id
                        }
                    },
                    timeout=10
                )
                
                if sync_response.status_code == 200:
                    logger.info(f"✓ [{request_id}] Content synced to database")
                else:
                    logger.error(f"✗ [{request_id}] Database sync failed: {sync_response.status_code} - {sync_response.text}")
                    
        except Exception as sync_error:
            logger.error(f"[{request_id}] Database sync exception: {sync_error}")
            # Don't fail generation if sync fails

        app.state.generation_tasks[request_id] = {
            "status": "completed",
            "progress": 1.0,
            "content": content,
            "content_id": file_id,
            "metadata": {
                "completed_at": datetime.now().isoformat(),
                "title": title,
                "subtitle": subtitle,
                "preview": subtitle
            }
        }
        logger.info(f"[{request_id}] Workflow completed successfully.")

    except Exception as e:
        logger.error(f"[{request_id}] Workflow failed: {e}", exc_info=True)
        app.state.generation_tasks[request_id] = {
            "status": "error",
            "progress": 0,
            "error": str(e)
        }

# ====== API Endpoints ======
@app.get("/api/templates/{template_id}")
async def get_template_details(template_id: str):
    """Get full template details including normalized parameters"""
    config_manager: ConfigManager = app.state.config_manager
    if not config_manager:
        raise HTTPException(status_code=503, detail="Configuration Manager not available.")
    
    try:
        template_dict = config_manager.get_template(template_id)
        parameters = _normalize_parameters(template_dict)
        
        return {
            "success": True,
            "data": {
                "id": template_dict.get("id"),
                "name": template_dict.get("name"),
                "slug": template_dict.get("slug"),
                "description": template_dict.get("description"),
                "template_type": template_dict.get("template_type"),
                #"category": template_dict.get("category"),
                #"version": template_dict.get("version", "1.0"),
                "parameters": parameters,
                "metadata": template_dict.get("metadata", {}),
            }
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    except Exception as e:
        logger.error(f"Error retrieving template {template_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/style-profiles/{profile_id}")
async def get_style_profile_details(profile_id: str):
    """Get full style profile details"""
    config_manager: ConfigManager = app.state.config_manager
    if not config_manager:
        raise HTTPException(status_code=503, detail="Configuration Manager not available.")
    
    try:
        profile_dict = config_manager.get_style_profile(profile_id)
        
        return {
            "success": True,
            "data": {
                "id": profile_dict.get("id"),
                "name": profile_dict.get("name"),
                "description": profile_dict.get("description"),
                "tone": profile_dict.get("tone"),
                "voice": profile_dict.get("voice"),
                "audience": profile_dict.get("audience"),
                "platform": profile_dict.get("platform", "web"),
                "category": profile_dict.get("category"),
                "system_prompt": profile_dict.get("system_prompt"),
                "formatting": profile_dict.get("formatting", {}),
            }
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Style profile '{profile_id}' not found")
    
# Add this import near the top with other core imports
from .core.types import ContentSpec 

# Replace the existing generate function with this one:
@app.post("/api/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate(
    req: GenerateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Starts a content generation job in the background."""
    config_manager: ConfigManager = app.state.config_manager
    if not config_manager:
        raise HTTPException(status_code=503, detail="Configuration Manager not available.")

    request_id = req.request_id or str(uuid.uuid4())
    user_id = req.user_id or request.headers.get("X-User-ID", "anonymous")

    try:
        template_dict = config_manager.get_template(req.get_template())
        style_profile_dict = config_manager.get_style_profile(req.get_style())

        topic = req.user_input.get("topic", req.user_input.get("title", "Unknown Topic"))
        subtopics = req.user_input.get("subtopics", [])
        constraints = req.user_input.get("constraints", {})

        content_spec = ContentSpec(
            topic=str(topic),
            subtopics=[str(s) for s in subtopics] if isinstance(subtopics, list) else [],
            constraints=constraints if isinstance(constraints, dict) else {},
            target_audience=style_profile_dict.get('audience', ''),
            platform=style_profile_dict.get('platform', 'web')
        )

        # Merge generation_settings into dynamic_parameters
        dynamic_params = {
            **req.user_input,
            'generation_settings': req.generation_settings or {
                'max_tokens': 8000,
                'temperature': 0.7,
                'quality_mode': 'balanced'
            }
        }

        initial_state = EnrichedContentState(
            template_config=template_dict,       
            style_config=style_profile_dict,     
            dynamic_parameters=dynamic_params,
            content_spec=content_spec,
            current_date=datetime.now().isoformat()  
        )

        background_tasks.add_task(run_generation_workflow, request_id, initial_state)

        return {
            "request_id": request_id,
            "status": "pending",
            "message": "Content generation started.",
            "links": {"status": f"/api/generate/status/{request_id}"},
        }
    except KeyError as e:
        logger.error(f"Configuration key error for request {request_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Configuration not found: {e}")
    except Exception as e:
        logger.error(f"Failed to start generation for request {request_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
@app.get("/api/generate/status/{request_id}")
async def get_generation_status(request_id: str):
    """Retrieves the status or result of a content generation job."""
    task = app.state.generation_tasks.get(request_id)
    if not task:
        raise HTTPException(status_code=404, detail="Generation request not found.")
    
    # DEBUG: Log what we're returning
    content_len = len(task.get("content", "")) if task.get("content") else 0
    logger.info(f"[{request_id}] Status check: status={task.get('status')}, content_len={content_len}")
    
    return {
        "success": True,
        "data": {
            "request_id": request_id,
            "status": task.get("status", "unknown"),
            "progress": task.get("progress", 0),
            "current_agent": task.get("current_agent"),
            "content": task.get("content"),
            "error": task.get("error"),
            "metadata": task.get("metadata", {}),
        }
    }

# --- Templates & Style Profiles: LIST (enterprise format) ---

@app.get("/api/templates")
async def list_templates(page: int = 1, limit: int = 100):
    """Returns paginated list of available templates."""
    config_manager: ConfigManager = app.state.config_manager
    if not config_manager:
        raise HTTPException(status_code=503, detail="Configuration Manager not available.")

    template_ids = config_manager.list_templates()

    start = (page - 1) * limit
    end = start + limit
    paginated_ids = template_ids[start:end]

    items = []
    for tid in paginated_ids:
        t = config_manager.get_template(tid)
        items.append({
            "id": t.get("id"),
            "name": t.get("name", tid),
            "template_type": t.get("template_type"),
            "description": t.get("description") or t.get("metadata", {}).get("strategy", ""),
        })

    return {"success": True, "data": {"items": items, "count": len(template_ids), "page": page, "limit": limit}}

@app.get("/api/dashboard/stats")
async def dashboard_stats():
    return {"success": True, "data": {"total_content": 0, "this_month": 0}}

@app.get("/api/dashboard/activity")
async def dashboard_activity():
    return {"success": True, "data": {"items": []}}

@app.get("/api/content")
async def list_content():
    return {"success": True, "data": {"items": []}}

@app.get("/api/style-profiles")
async def list_style_profiles(page: int = 1, limit: int = 100):
    """Returns paginated list of available style profiles."""
    config_manager: ConfigManager = app.state.config_manager
    if not config_manager:
        raise HTTPException(status_code=503, detail="Configuration Manager not available.")

    profile_ids = config_manager.list_style_profiles()

    start = (page - 1) * limit
    end = start + limit
    paginated_ids = profile_ids[start:end]

    items = []
    for pid in paginated_ids:
        p = config_manager.get_style_profile(pid)
        items.append({
            "id": p.get("id"),
            "name": p.get("name", pid),
            "tone": p.get("tone"),
            "voice": p.get("voice"),
            "audience": p.get("audience"),
            "platform": p.get("platform", "web"),
        })

    return {"success": True, "data": {"items": items, "count": len(profile_ids), "page": page, "limit": limit}}

@app.get("/api/content/{content_id}")
async def get_content_detail(content_id: str):
    """Get single content item by ID"""
    from pathlib import Path
    import json
    
    for week_dir in Path("generated_content").iterdir():
        if not week_dir.is_dir():
            continue
        
        json_file = week_dir / f"{content_id}.json"
        if json_file.exists():
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                return {
                    "id": data.get("id", content_id),
                    "title": data.get("title"),
                    "content": data.get("final_content") or data.get("content"),
                    "contentHtml": data.get("contentHtml"),
                    "status": data.get("status", "draft"),
                    "type": data.get("template_id", "article"),
                    "createdAt": data.get("timestamp"),
                    "updatedAt": data.get("timestamp"),
                    "views": data.get("views", 0),
                    "metadata": {
                        "template": data.get("template_id"),
                        "styleProfile": data.get("style_profile")
                    }
                }
            except Exception as e:
                logger.error(f"Error reading content {content_id}: {e}")
    
    raise HTTPException(status_code=404, detail="Content not found")

@app.post("/api/content/{content_id}/track-view")
async def track_content_view(content_id: str):
    """Track content view and update metrics"""
    from pathlib import Path
    import json
    
    # Update in-memory counter
    content_metrics[content_id]["views"] = content_metrics[content_id].get("views", 0) + 1
    content_metrics[content_id]["last_viewed"] = datetime.now().isoformat()
    
    # Update JSON file
    for week_dir in Path("generated_content").iterdir():
        if not week_dir.is_dir():
            continue
        
        json_file = week_dir / f"{content_id}.json"
        if json_file.exists():
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                data['views'] = content_metrics[content_id]["views"]
                data['last_viewed'] = content_metrics[content_id]["last_viewed"]
                
                with open(json_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return {
                    "success": True,
                    "views": data['views'],
                    "unique_views": len(content_metrics[content_id].get("unique_sessions", set()))
                }
            except Exception as e:
                logger.error(f"Error updating views for {content_id}: {e}")
    
    return {"success": False, "views": 0, "unique_views": 0}

# Add this endpoint to integrated_server.py

@app.post("/api/analyze/content")
async def analyze_content(request: Request):
    """Enterprise content analysis via SEO agent"""
    body = await request.json()
    content = body.get("content", "")
    analysis_types = body.get("analysis_types", [])
    generation_id = body.get("generation_id")
    
    if not content:
        raise HTTPException(status_code=400, detail="Content required")
    
    # Invoke SEO agent for analysis
    try:
        from agents.enhanced_seo_agent_integrated import invoke_seo_agent
        
        analysis_result = await invoke_seo_agent({
            "final_content": content,
            "template_type": body.get("template_type", "article"),
            "style_profile": body.get("style_profile", {}),
            "generation_id": generation_id
        })
        
        return {
            "readability_score": analysis_result.get("readability_score", 50),
            "sentiment_analysis": analysis_result.get("sentiment_analysis", {
                "score": 0,
                "confidence": 50,
                "dominant_emotion": "neutral"
            }),
            "seo_optimization": analysis_result.get("seo_optimization", {
                "score": 50,
                "keyword_density": {},
                "suggestions": []
            }),
            "engagement_prediction": analysis_result.get("engagement_prediction", {
                "score": 50,
                "viral_potential": 25,
                "target_demographics": []
            }),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "generation_id": generation_id
        }
        
    except Exception as e:
        logger.error(f"Content analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/backfill-titles")
async def backfill_titles():
    """Fix existing JSON files with missing titles"""
    from pathlib import Path
    import json
    
    base_dir = Path("generated_content")
    fixed_count = 0
    
    for json_file in base_dir.glob("week_*/*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data.get("title"):
                content = data.get("content", "")
                
                # Extract title from content
                title = ""
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('title:'):
                        title = line.replace('title:', '').strip()
                        break
                    elif line.startswith('# '):
                        title = line.lstrip('# ').strip()
                        break
                
                if not title:
                    title = json_file.stem.replace('_', ' ').title()
                
                data["title"] = title
                
                # Fix subtitle if it has YAML
                if data.get("subtitle", "").startswith("---"):
                    data["subtitle"] = content.replace('#', '').replace('---', '').strip()[:150]
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                fixed_count += 1
                logger.info(f"Fixed {json_file.name}: {title}")
        
        except Exception as e:
            logger.error(f"Error fixing {json_file}: {e}")
    
    return {"fixed": fixed_count, "message": f"Backfilled {fixed_count} files"}

# --- Uvicorn entry for running directly ---
if __name__ == "__main__":
    uvicorn.run("langgraph_app.integrated_server:app", host="0.0.0.0", port=8000, reload=True)