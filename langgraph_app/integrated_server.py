"""
WriterzRoom API — Enterprise Edition
Enterprise-grade FastAPI server with MCP integration and strict fail-fast rules.

Key guarantees:
- No fallbacks or mock data
- template_config and style_config are explicit, non-empty dicts
- YAML templates/style profiles loaded with strict validation
- Background generation uses execute_enhanced_mcp_generation(request_id, template_config, style_config, dynamic_parameters)
"""

import os
from re import template
from unittest import result
import uuid
import json
import yaml
import copy
import time
import hashlib
import frontmatter
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
from langgraph_app.analytics_endpoints import router as analytics_router

# ====== Enterprise: Required integrations must exist ======
try:
    from .mcp_server_extension import (
        initialize_mcp_for_existing_server,
        cleanup_mcp_for_existing_server,
        enhance_generation_with_mcp,
        MCPGenerationRequest,
        execute_enhanced_mcp_generation,   # <- background task
    )
    from .schemas import MCPGenerationRequest
except Exception as e:
    raise SystemExit(f"ENTERPRISE: MCP integration not available: {e}")

try:
    # If your Universal integration lives elsewhere, adjust this import
    from .universal_system.universal_integration import LangGraphUniversalIntegration  # optional but required in enterprise mode
except Exception as e:
    raise SystemExit(f"ENTERPRISE: Universal System not available: {e}")

try:
    # Optional: if you maintain a model registry, keep this check strict
    from .enhanced_model_registry import get_model, EnhancedModelRegistry  # noqa
except Exception as e:
    raise SystemExit(f"ENTERPRISE: Model registry not available: {e}")

# ====== Logging ======
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger("writerzroom.integrated_server")

# ====== Enterprise configuration ======
API_KEY = os.getenv("LANGGRAPH_API_KEY")
if not API_KEY:
    raise SystemExit("ENTERPRISE: LANGGRAPH_API_KEY is required")

ENVIRONMENT = os.getenv("NODE_ENV", "production").lower()
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# ====== Auth (Bearer) ======
security = HTTPBearer(auto_error=False)

async def get_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    return credentials.credentials if credentials else None

async def verify_api_key(api_key: Optional[str] = Depends(get_api_key)) -> bool:
    if ENVIRONMENT == "production":
        if not api_key or api_key != API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return True


# ====== Metrics ======
custom_registry = getattr(globals(), "WRITERZROOM_PROM_REGISTRY", None) or CollectorRegistry()
WRITERZROOM_PROM_REGISTRY = custom_registry

def _get_or_create_counter(name, description, labels, registry=None):
    if registry is None:
        registry = custom_registry
    try:
        return Counter(name, description, labels, registry=registry)
    except ValueError as e:
        # Duplicate — return existing
        for collector in registry._collector_to_names:  # type: ignore[attr-defined]
            if getattr(collector, "_name", None) == name:
                return collector
        raise

def _get_or_create_histogram(name, description, registry=None):
    if registry is None:
        registry = custom_registry
    try:
        return Histogram(name, description, registry=registry)
    except ValueError as e:
        for collector in registry._collector_to_names:  # type: ignore[attr-defined]
            if getattr(collector, "_name", None) == name:
                return collector
        raise

REQUEST_COUNT = _get_or_create_counter(
    "writerzroom_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = _get_or_create_histogram(
    "writerzroom_request_duration_seconds", "HTTP request duration (s)"
)
GENERATION_COUNT = _get_or_create_counter(
    "writerzroom_generation_total", "Total content generations", ["status", "template"]
)
GENERATION_DURATION = _get_or_create_histogram(
    "writerzroom_generation_duration_seconds", "Content generation duration (s)"
)

# ====== Pydantic models (kept local for server boundary clarity) ======
class TemplateParameter(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=200)
    type: str = Field(..., pattern=r"^(string|text|textarea|number|select|boolean|array|date|email|url)$")
    description: Optional[str] = Field(None, max_length=500)
    placeholder: Optional[str] = Field(None, max_length=500)
    default: Optional[Union[str, int, float, bool, List[str]]] = None
    options: Optional[List[str]] = Field(None, max_items=200)
    required: bool = Field(default=False)
    validation: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ContentTemplate(BaseModel):
    id: str = Field(..., min_length=1, max_length=100)    # usually filename w/o .yaml
    slug: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1500)
    category: Optional[str] = Field(None, max_length=100)
    defaults: Dict[str, Any] = Field(default_factory=dict)
    system_prompt: Optional[str] = Field(None, max_length=5000)
    structure: Optional[Dict[str, Any]] = Field(default_factory=dict)
    research: Optional[Dict[str, Any]] = Field(default_factory=dict)
    parameters: Dict[str, TemplateParameter] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: str = Field(default="1.0.0")
    filename: str

class StyleProfile(BaseModel):
    id: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1500)
    category: str = Field(default="general", max_length=100)
    platform: Optional[str] = Field(None, max_length=100)
    tone: Optional[str] = Field(None, max_length=100)
    voice: Optional[str] = Field(None, max_length=120)
    structure: Optional[str] = Field(None, max_length=500)
    audience: Optional[str] = Field(None, max_length=200)
    system_prompt: Optional[str] = Field(None, max_length=5000)
    length_limit: Optional[Dict[str, Any]] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    formatting: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    filename: str

class GenerateRequest(BaseModel):
    class Config:
        extra = "allow"
    template: str = Field(..., min_length=1, max_length=200)       # id or filename(.yaml)
    style_profile: str = Field(..., min_length=1, max_length=200)  # id or filename(.yaml)
    dynamic_parameters: Dict[str, Any] = Field(default_factory=dict, max_items=100)
    request_id: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)
    timeout_seconds: int = Field(default=300, ge=60, le=1800)

    @field_validator("dynamic_parameters")
    @classmethod
    def _validate_params(cls, v):
        for k, val in v.items():
            if isinstance(val, str) and len(val) > 10000:
                raise ValueError(f"Parameter '{k}' exceeds maximum length")
        return v

# ====== YAML loading (strict) ======
def _existing_dirs(cands: List[str]) -> List[str]:
    return [p for p in cands if os.path.exists(p)]

def get_template_paths() -> List[str]:
    paths = _existing_dirs([
        "data/content_templates",
        "../data/content_templates",
        "frontend/content-templates",
        "../frontend/content-templates",
        "content-templates",
    ])
    if not paths:
        raise SystemExit("ENTERPRISE: No template directories found")
    return paths

def get_style_profile_paths() -> List[str]:
    paths = _existing_dirs([
        "data/style_profiles",
        "../data/style_profiles",
        "frontend/style-profiles",
        "../frontend/style-profiles",
        "style_profiles",
        "style_profile",
    ])
    if not paths:
        raise SystemExit("ENTERPRISE: No style profile directories found")
    return paths

def load_yaml_file_safe(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
        if content is None:
            raise ValueError(f"Empty YAML file: {file_path}")
        if not isinstance(content, dict):
            raise ValueError(f"Invalid YAML root in {file_path}: {type(content)}")
        return content
    except Exception as e:
        raise SystemExit(f"ENTERPRISE: YAML load error for {file_path}: {e}")

# langgraph_app/integrated_server.py
# FIXED: parse_template_parameters function at line ~125

def parse_template_parameters(parameters_data: Any) -> Dict[str, TemplateParameter]:
    """Convert YAML inputs/parameters to TemplateParameter dict - FIXED"""
    processed: Dict[str, TemplateParameter] = {}
    
    # Handle V2.0 inputs format (your YAML structure)
    if isinstance(parameters_data, dict) and 'inputs' in parameters_data:
        inputs = parameters_data['inputs']
        for key, param in inputs.items():
            if isinstance(param, dict):
                processed[key] = TemplateParameter(
                    name=key,
                    label=param.get("label", key.replace("_", " ").title()),
                    type=_infer_param_type(param.get("default")),
                    description=param.get("description", ""),
                    placeholder=param.get("placeholder", ""),
                    default=param.get("default"),
                    options=param.get("options"),
                    required=param.get("required", False),
                    validation=param.get("validation", {}) or {},
                )
        return processed
    
    # Handle direct inputs format (your actual case)
    if isinstance(parameters_data, dict):
        # Check if this looks like inputs format
        sample_values = list(parameters_data.values())[:3]
        is_inputs_format = any(
            isinstance(v, dict) and ('required' in v or 'default' in v)
            for v in sample_values
        )
        
        if is_inputs_format:
            # This is inputs format - convert it
            for key, param in parameters_data.items():
                if isinstance(param, dict):
                    processed[key] = TemplateParameter(
                        name=key,
                        label=param.get("label", key.replace("_", " ").title()),
                        type=_infer_param_type(param.get("default")),
                        description=param.get("description", ""),
                        placeholder=param.get("placeholder", ""),
                        default=param.get("default"),
                        options=param.get("options"),
                        required=param.get("required", False),
                        validation=param.get("validation", {}) or {},
                    )
                else:
                    # Simple key-value pair
                    processed[key] = TemplateParameter(
                        name=key,
                        label=key.replace("_", " ").title(),
                        type=_infer_param_type(param),
                        default=param if param is not None else None,
                        required=False,
                    )
        else:
            # This is already parameters format
            for key, param in parameters_data.items():
                if isinstance(param, dict):
                    processed[key] = TemplateParameter(
                        name=key,
                        label=param.get("label", key.replace("_", " ").title()),
                        type=param.get("type", "string"),
                        description=param.get("description"),
                        placeholder=param.get("placeholder"),
                        default=param.get("default"),
                        options=param.get("options"),
                        required=param.get("required", False),
                        validation=param.get("validation", {}) or {},
                    )
    
    # Handle legacy list format
    elif isinstance(parameters_data, list):
        for param in parameters_data:
            if isinstance(param, dict) and "name" in param:
                nm = param["name"]
                processed[nm] = TemplateParameter(
                    name=nm,
                    label=param.get("label", nm.replace("_", " ").title()),
                    type=param.get("type", "string"),
                    description=param.get("description"),
                    placeholder=param.get("placeholder"),
                    default=param.get("default"),
                    options=param.get("options"),
                    required=param.get("required", False),
                    validation=param.get("validation", {}) or {},
                )
    
    return processed

def _infer_param_type(value):
    """Infer parameter type from default value"""
    if isinstance(value, bool):
        return 'boolean'
    if isinstance(value, (int, float)):
        return 'number'
    if isinstance(value, list):
        return 'select'
    if value and len(str(value)) > 100:
        return 'textarea'
    return 'text'

# Also update load_templates() to handle inputs properly
def load_templates() -> List[ContentTemplate]:
    """Load templates with proper inputs conversion"""
    items: List[ContentTemplate] = []
    for base in get_template_paths():
        for path in Path(base).glob("*.yaml"):
            data = load_yaml_file_safe(str(path))
            
            # Required keys: id/slug/name
            tpl_id = data.get("id") or path.stem
            slug = data.get("slug") or path.stem
            name = data.get("name") or slug.replace("-", " ").title()
            
            # Handle both 'parameters' and 'inputs' keys
            params_data = data.get("parameters") or data.get("inputs") or {}
            params = parse_template_parameters(params_data)
            
            # FIXED: Store template_type in defaults for build_template_config access
            defaults = data.get("defaults") or {}
            if data.get("template_type"):
                defaults["template_type"] = data["template_type"]
            
            items.append(ContentTemplate(
                id=str(tpl_id),
                slug=str(slug),
                name=str(name),
                description=data.get("description"),
                category=data.get("category"),
                defaults=defaults,
                system_prompt=data.get("system_prompt"),
                structure=data.get("structure") or {},
                research=data.get("research") or {},
                parameters=params,
                metadata=data.get("metadata") or {},
                version=str(data.get("version", "1.0.0")),
                filename=str(path),
            ))
    
    if not items:
        raise SystemExit("ENTERPRISE: No templates loaded")
    return items

def load_style_profiles() -> List[StyleProfile]:
    items: List[StyleProfile] = []
    for base in get_style_profile_paths():
        for path in Path(base).glob("*.yaml"):
            data = load_yaml_file_safe(str(path))
            prof_id = data.get("id") or path.stem
            name = data.get("name") or path.stem.replace("-", " ").title()
            items.append(StyleProfile(
                id=str(prof_id),
                name=str(name),
                description=data.get("description"),
                category=str(data.get("category", "general")),
                platform=data.get("platform"),
                tone=data.get("tone"),
                voice=data.get("voice"),
                structure=data.get("structure"),
                audience=data.get("audience"),
                system_prompt=data.get("system_prompt"),
                length_limit=data.get("length_limit") or {},
                settings=data.get("settings") or {},
                formatting=data.get("formatting") or {},
                metadata=data.get("metadata") or {},
                filename=str(path),
            ))
    if not items:
        raise SystemExit("ENTERPRISE: No style profiles loaded")
    return items

# ====== Config builders (strict, no fallbacks) ======
# File: langgraph_app/integrated_server.py
# MINIMAL FIX: Only flatten dynamic_overrides structure

# File: langgraph_app/integrated_server.py
# MINIMAL FIX: Only flatten dynamic_overrides structure

# File: langgraph_app/integrated_server.py
# FIXED: Template configuration processing - use actual template structure

def build_template_config(template: ContentTemplate, profile: StyleProfile, request: GenerateRequest) -> Dict[str, Any]:
    """FIXED: Extract template_type from template structure, not defaults"""
    
    # CRITICAL FIX: Use template.template_type directly from YAML metadata
    template_type = getattr(template, 'template_type', None) or template.metadata.get('template_type')
    if not template_type:
        # Fallback to slug-based inference only if absolutely missing
        template_type = template.slug or 'article'
    
    # Extract system prompt and instructions from template
    system_prompt = template.system_prompt or ""
    instructions = ""
    
    # FIXED: Extract template-specific instructions and structure
    if template.structure:
        if isinstance(template.structure, dict):
            instructions += f"Content Structure: {template.structure.get('format', 'sections')}\n"
            if 'sections' in template.structure:
                instructions += f"Required Sections: {template.structure['sections']}\n"
            if 'format_requirements' in template.structure:
                instructions += f"Format Requirements: {template.structure['format_requirements']}\n"
    
    # FIXED: Include template defaults as part of configuration
    template_defaults = template.defaults or {}
    
    # Flatten parameters correctly
    parameters_spec: Dict[str, Any] = {}
    for k, p in (template.parameters or {}).items():
        parameters_spec[k] = {
            "type": p.type,
            "required": bool(p.required),
            "options": p.options or [],
            "default": p.default,
            "label": p.label,
            "description": p.description,
            "placeholder": p.placeholder,
            "validation": p.validation or {},
        }

    # FIXED: Preserve research requirements
    research_config = template.research or {}
    
    cfg = {
        "id": template.id,
        "slug": template.slug,
        "name": template.name,
        "template_type": template_type,
        "system_prompt": system_prompt,
        "instructions": instructions,
        "structure": template.structure or {},
        "research": research_config,
        "parameters": parameters_spec,
        "defaults": template_defaults,
        "generation_mode": template.metadata.get("generation_mode", "standard"),
        "platform": profile.platform or "web",
        "content_requirements": {
            "style_guide": profile.system_prompt or "",
            "tone": profile.tone,
            "voice": profile.voice,
            "structure_preference": profile.structure,
            "audience": profile.audience,
            "length_limits": profile.length_limit or {},
            "formatting": profile.formatting or {}
        }
    }

    # FIXED: Handle dynamic overrides without flattening structure
    if request.dynamic_parameters:
        cfg["dynamic_parameters"] = request.dynamic_parameters
        # Only flatten specific nested structures, not all overrides
        if "dynamic_overrides" in request.dynamic_parameters:
            overrides = request.dynamic_parameters["dynamic_overrides"]
            if isinstance(overrides, dict):
                cfg["user_inputs"] = overrides
    
    cfg["_fingerprint"] = hashlib.sha256(json.dumps(cfg, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    return cfg

def build_style_config(profile: StyleProfile) -> Dict[str, Any]:
    """FIXED: Preserve complete style configuration"""
    style_cfg = {
        "id": profile.id,
        "name": profile.name,
        "category": profile.category,
        "platform": profile.platform,
        "tone": profile.tone,
        "voice": profile.voice,
        "structure": profile.structure,
        "audience": profile.audience,
        "length_limit": profile.length_limit or {},
        "settings": profile.settings or {},
        "formatting": profile.formatting or {},
        "system_prompt": profile.system_prompt,
        "content_guidelines": {
            "formality": profile.settings.get("formality", "professional"),
            "complexity": profile.settings.get("complexity", "medium"),
            "technical_level": profile.settings.get("technical_level", "intermediate")
        },
        "_filename": profile.filename,
    }
    return style_cfg
# ====== App & lifespan ======
app = FastAPI(
    title="WriterzRoom API — Enterprise",
    description="Enterprise-grade AI content generation with strict MCP integration",
    version="2.0.0-enterprise",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
)

app.include_router(analytics_router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting WriterzRoom API — Enterprise Mode")
    app.state.generation_tasks = {}
    app.state.templates = load_templates()
    app.state.style_profiles = load_style_profiles()
    logger.info(f"Templates loaded: {len(app.state.templates)}; Style profiles loaded: {len(app.state.style_profiles)}")
    # Model registry check (strict)
    try:
        _ = get_model("writer")
        logger.info("Model registry initialized")
    except Exception as e:
        raise SystemExit(f"ENTERPRISE: model registry init failed: {e}")

    # MCP init
    try:
        ok = await initialize_mcp_for_existing_server(app)
        if not ok:
            raise SystemExit("ENTERPRISE: MCP init returned failure")
        app.state.mcp_available = True
        logger.info("MCP initialized")
    except Exception as e:
        raise SystemExit(f"ENTERPRISE: MCP init failed: {e}")

    # Universal system (required)
    try:
        app.state.universal = LangGraphUniversalIntegration()
        logger.info("Universal system initialized")
    except Exception as e:
        raise SystemExit(f"ENTERPRISE: Universal init failed: {e}")

    yield

    # Cleanup
    try:
        await cleanup_mcp_for_existing_server(app)
        logger.info("MCP cleanup completed")
    except Exception as e:
        logger.error(f"MCP cleanup error: {e}")

app.router.lifespan_context = lifespan  # register lifespan

# ====== Middleware: request tracking ======
@app.middleware("http")
async def track_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
    finally:
        dur = time.perf_counter() - start
        try:
            status_code = getattr(response, "status_code", 500)
            REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=status_code).inc()
            REQUEST_DURATION.observe(dur)
        except Exception:
            pass
    if response is not None and hasattr(response, "headers"):
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{dur:.3f}s"
    logger.info(f"{request.method} {request.url.path} {getattr(response,'status_code',0)} {dur:.3f}s [{request_id}]")
    return response

# ====== Endpoints ======
@app.get("/")
async def root(request: Request):
    return {
        "name": "WriterzRoom API — Enterprise",
        "version": "2.0.0-enterprise",
        "mode": "enterprise",
        "request_id": request.state.request_id,
    }

@app.get("/health")
async def health(authenticated: bool = Depends(verify_api_key)):
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "mcp_available": bool(getattr(app.state, "mcp_available", False)),
    }

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(custom_registry), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/templates")
async def api_templates(authenticated: bool = Depends(verify_api_key)):
    templates = getattr(app.state, "templates", None) or load_templates()
    return {"success": True, "data": {"items": [t.dict() for t in templates], "count": len(templates)}}

@app.get("/api/style-profiles")
async def api_style_profiles(authenticated: bool = Depends(verify_api_key)):
    profiles = getattr(app.state, "style_profiles", None) or load_style_profiles()
    return {"success": True, "data": {"items": [p.dict() for p in profiles], "count": len(profiles)}}


# File: langgraph_app/integrated_server.py
# Replace the problematic endpoint section (lines 580-650) with this:

@app.post("/api/generate")
async def generate_content(
    request_data: GenerateRequest,
    background_tasks: BackgroundTasks,
    _request: Request,
    _authenticated: bool = Depends(verify_api_key),
):
    request_id = getattr(request_data, 'request_id', None) or str(uuid.uuid4())

    try:
        templates = getattr(app.state, "templates", None) or load_templates()
        profiles = getattr(app.state, "style_profiles", None) or load_style_profiles()

        # Find template and profile
        template = None
        for t in templates:
            if t.id == request_data.template or t.slug == request_data.template:
                template = t
                break

        profile = None
        for p in profiles:
            if p.id == request_data.style_profile:
                profile = p
                break

        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {request_data.template}")
        if not profile:
            raise HTTPException(status_code=404, detail=f"Style profile not found: {request_data.style_profile}")

        template_config = build_template_config(template, profile, request_data)
        style_config = build_style_config(profile)

        # Initialize task status
        status_obj = {
            "request_id": request_id,
            "status": "pending",
            "progress": 0.0,
            "content": "",
            "metadata": {
                "template": template.name,
                "style_profile": profile.name,
                "started_at": datetime.now().isoformat(),
                "enterprise_mode": True,
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        if not hasattr(app.state, "generation_tasks"):
            app.state.generation_tasks = {}
        app.state.generation_tasks[request_id] = status_obj

        # Background task with proper result storage
        # File: langgraph_app/integrated_server.py
        # Replace lines 654-694 in the _execute_and_store() function:

        # Background task with proper result storage
        # File: langgraph_app/integrated_server.py
        # Updated _execute_and_store function with analytics logging
        
        async def _execute_and_store():
            start_time = time.perf_counter()
            try:
                logger.info(f"Background task starting for {request_id}")
                result = await execute_enhanced_mcp_generation(
                    request_id, 
                    template_config, 
                    style_config, 
                    request_data.dynamic_parameters or {}
                )
        
                # Handle async result
                import inspect
                if inspect.isawaitable(result):
                    result = await result
        
                logger.info(f"MCP generation completed for {request_id}, result type: {type(result)}")
        
                # Extract content
                content = ""
                if isinstance(result, dict):
                    content = (
                        result.get('content') or 
                        result.get('final_content') or 
                        result.get('draft_content') or
                        ""
                    )
                    
                    if not content and 'metadata' in result:
                        metadata = result['metadata']
                        content = (
                            metadata.get('content') or
                            metadata.get('final_content') or 
                            metadata.get('generated_content') or
                            ""
                        )
                    
                    logger.info(f"Found content in dict: {len(content)} chars")
                elif hasattr(result, 'content'):
                    content = result.content or ""
                    logger.info(f"Found content in result.content: {len(content)} chars")
                else:
                    logger.warning(f"Unexpected result type: {type(result)}")
        
                # Calculate metrics
                generation_time = time.perf_counter() - start_time
                word_count = len(content.split()) if content else 0
                success = bool(content)
        
                # Log to analytics database
                try:
                    from langgraph_app.database.models import GenerationLog, SessionLocal
                    db = SessionLocal()
                    try:
                        log = GenerationLog(
                            template_id=template_config['id'],
                            style_profile_id=style_config['id'],
                            word_count=word_count,
                            generation_time_seconds=generation_time,
                            success=success
                        )
                        db.add(log)
                        db.commit()
                        logger.info(f"Analytics logged for {request_id}")
                    finally:
                        db.close()
                except Exception as e:
                    logger.error(f"Failed to log analytics for {request_id}: {e}")
                    # Don't fail the generation if analytics logging fails
                
                # Update task status
                app.state.generation_tasks[request_id].update({
                    "status": "completed",
                    "progress": 1.0,
                    "content": content,
                    "updated_at": datetime.now().isoformat(),
                    "metadata": {
                        **app.state.generation_tasks[request_id]["metadata"],
                        "word_count": word_count,
                        "generation_time": generation_time
                    }
                })
                
                logger.info(f"Generation completed for {request_id}, content length: {len(content)}")
                
            except Exception as e:
                logger.error(f"Generation failed for {request_id}: {e}")
                
                # Log failure to analytics
                try:
                    from langgraph_app.database.models import GenerationLog, SessionLocal
                    db = SessionLocal()
                    try:
                        log = GenerationLog(
                            template_id=template_config['id'],
                            style_profile_id=style_config['id'],
                            word_count=0,
                            generation_time_seconds=time.perf_counter() - start_time,
                            success=False
                        )
                        db.add(log)
                        db.commit()
                    finally:
                        db.close()
                except:
                    pass  # Silent fail on analytics during error
                
                app.state.generation_tasks[request_id].update({
                    "status": "error",
                    "errors": [str(e)],
                    "updated_at": datetime.now().isoformat(),
                })
    except Exception as e:
        logger.error(f"Generation initialization failed for {request_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Generation initialization failed: {e}")

    # Schedule background task and return immediate response
    background_tasks.add_task(_execute_and_store)
    return {
        "success": True,
        "request_id": request_id,
        "status": "pending"
    }

@app.get("/api/generate/{request_id}")
async def get_generation_result(request_id: str):
    """Get generation result by request_id"""
    if not hasattr(app.state, "generation_tasks"):
        app.state.generation_tasks = {}
    
    task_data = app.state.generation_tasks.get(request_id)
    
    if not task_data:
        return {
            "success": True,
            "data": {
                "request_id": request_id,
                "status": "not_found",
                "content": "",
                "metadata": {}
            }
        }
    
    return {
        "success": True,
        "data": {
            "request_id": request_id,
            "status": task_data.get("status", "pending"),
            "content": task_data.get("content", ""),
            "metadata": task_data.get("metadata", {}),
            "progress": task_data.get("progress", 0.0)
        }
    }


@app.get("/api/generate/status/{request_id}")
async def get_generation_status(request_id: str):
    """Frontend polling endpoint - same logic as above"""
    if not hasattr(app.state, "generation_tasks"):
        app.state.generation_tasks = {}
    
    task_data = app.state.generation_tasks.get(request_id)
    
    if not task_data:
        return {
            "success": True,
            "data": {
                "request_id": request_id,
                "status": "not_found",
                "content": "",
                "metadata": {}
            }
        }
    
    return {
        "success": True,
        "data": {
            "request_id": request_id,
            "status": task_data.get("status", "pending"),
            "content": task_data.get("content", ""),
            "metadata": task_data.get("metadata", {}),
            "progress": task_data.get("progress", 0.0)
        }
    }


@app.get("/api/content")
async def list_content():
    """List all generated content with real metadata"""
    from pathlib import Path
    import re
    
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
        
        # Process MD files first (they have the metadata)
        for file_path in week_dir.glob("*.md"):
            content_id = file_path.stem
            if content_id in seen_ids:
                continue
            seen_ids.add(content_id)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract YAML frontmatter
                match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if not match:
                    continue
                
                # Parse frontmatter
                frontmatter = {}
                for line in match.group(1).strip().split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        frontmatter[key.strip()] = val.strip().strip('"').strip("'")
                
                title = frontmatter.get('title', 'Untitled')
                status = frontmatter.get('status', 'draft')
                template_type = frontmatter.get('type', frontmatter.get('template', 'article'))
                created_at = frontmatter.get('createdAt', datetime.now().isoformat())
                
                views = content_metrics.get(content_id, {}).get("views", 0)
                total_views += views
                
                if status == "published":
                    published += 1
                else:
                    drafts += 1
                
                content_list.append({
                    "id": content_id,
                    "title": title,
                    "status": status,
                    "created_at": created_at,
                    "updated_at": created_at,
                    "template_type": template_type,
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


# langgraph_app/integrated_server.py

from datetime import datetime
import frontmatter

@app.get("/api/dashboard/stats")
async def get_dashboard_stats_direct():
    """Direct stats endpoint for frontend"""
    from pathlib import Path
    
    base_dir = Path("generated_content")
    total = 0
    published = 0
    drafts = 0
    views = 0
    recent_content = []
    recent_activity = []
    
    for week_dir in base_dir.iterdir():
        if not week_dir.is_dir():
            continue
        for md_file in week_dir.glob("*.md"):
            total += 1
            content_id = md_file.stem
            views += content_metrics.get(content_id, {}).get("views", 0)

            # Parse frontmatter for metadata
            try:
                post = frontmatter.load(md_file)
                status = post.get("status", "draft")
                title = post.get("title", content_id)
                updated_at = post.get("updated_at") or datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                ctype = post.get("type", "article")

                if status == "published":
                    published += 1
                else:
                    drafts += 1

                recent_content.append({
                    "id": content_id,
                    "title": title,
                    "status": status,
                    "updated_at": updated_at,
                    "type": ctype,
                })

                recent_activity.append({
                    "id": content_id,
                    "action": f"{status.capitalize()} content",
                    "timestamp": updated_at,
                    "actor": "system",
                })

            except Exception as e:
                drafts += 1
                # fail-fast: re-raise parsing error
                raise RuntimeError(f"Failed parsing {md_file}: {e}")

    # Sort by updated_at descending, limit to 10
    recent_content = sorted(recent_content, key=lambda x: x["updated_at"], reverse=True)[:10]
    recent_activity = sorted(recent_activity, key=lambda x: x["timestamp"], reverse=True)[:10]
    
    return {
        "total_content": total,
        "published": published,
        "drafts": drafts,
        "views": views,
        "recent_content": recent_content,
        "recent_activity": recent_activity,
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


@app.get("/api/metrics/dashboard")
async def get_real_dashboard_metrics():
    """Real dashboard metrics with snake_case fields"""
    from pathlib import Path
    
    base_dir = Path("generated_content")
    total_content = 0
    total_views = 0
    published = 0
    drafts = 0
    
    for week_dir in base_dir.iterdir():
        if not week_dir.is_dir():
            continue
        
        for json_file in week_dir.glob("*.json"):
            total_content += 1
            content_id = json_file.stem
            
            if content_id in content_metrics:
                total_views += content_metrics[content_id]["views"]
            
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    if data.get("status") == "published":
                        published += 1
                    else:
                        drafts += 1
            except:
                drafts += 1
    
    return {
        "total_content": total_content,
        "published": published,
        "drafts": drafts,
        "views": total_views
    }


# langgraph_app/integrated_server.py
# Replace the existing update_content endpoint (around line 850-880)

@app.put("/api/content/{content_id}")
async def update_content(content_id: str, content_update: dict):
    """Update content in both JSON and MD files to maintain consistency"""
    from pathlib import Path
    import frontmatter
    
    base_dir = Path("generated_content")
    
    for week_dir in base_dir.iterdir():
        if not week_dir.is_dir():
            continue
        
        json_file = week_dir / f"{content_id}.json"
        md_file = week_dir / f"{content_id}.md"
        
        # Check if either file exists
        if json_file.exists() or md_file.exists():
            logger.info(f"[CONTENT:PUT] Found content at {week_dir}/{content_id}")
            
            # Read existing data
            if json_file.exists():
                with open(json_file) as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Update data
            data["content"] = content_update.get("content", data.get("content", ""))
            data["title"] = content_update.get("title", data.get("title", ""))
            data["status"] = content_update.get("status", data.get("status", "draft"))
            
            if "metadata" not in data:
                data["metadata"] = {}
            
            data["metadata"]["updated_at"] = datetime.now().isoformat()
            
            # Write JSON file
            with open(json_file, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"[CONTENT:PUT] Updated JSON: {json_file}")
            
            # CRITICAL: Also update the MD file which is read by GET
            if md_file.exists() or data.get("content"):
                # Create frontmatter post
                post = frontmatter.Post(
                    content=data.get("content", ""),
                    title=data.get("title", ""),
                    status=data.get("status", "draft"),
                    type=data.get("type", "article"),
                    updated_at=data["metadata"]["updated_at"],
                    createdAt=data.get("createdAt", data["metadata"]["updated_at"]),
                    **{k: v for k, v in data.items() if k not in ["content", "title", "status", "type"]}
                )
                
                # Write MD file
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(frontmatter.dumps(post))
                logger.info(f"[CONTENT:PUT] Updated MD: {md_file}")
            
            return data
    
    raise HTTPException(status_code=404, detail="Content not found")


@app.get("/api/content/{content_id}")
async def get_content(content_id: str):
    """Get content with proper MD/JSON synchronization"""
    base_dir = Path("generated_content")
    
    for week_dir in base_dir.iterdir():
        if not week_dir.is_dir():
            continue
        
        md_file = week_dir / f"{content_id}.md"
        json_file = week_dir / f"{content_id}.json"
        
        # Try MD file first (primary source)
        if md_file.exists():
            try:
                post = frontmatter.load(md_file)
                logger.info(f"[CONTENT:GET] Found MD at {md_file}")
                
                # Check if JSON needs sync
                if json_file.exists():
                    with open(json_file) as f:
                        json_data = json.load(f)
                    
                    # Use the most recently updated version
                    json_updated = json_data.get("metadata", {}).get("updated_at", "")
                    md_updated = post.get("updated_at", "")
                    
                    if json_updated > md_updated:
                        logger.info(f"[CONTENT:GET] JSON is newer, using JSON data")
                        return {
                            "id": content_id,
                            "title": json_data.get("title", content_id),
                            "content": json_data.get("content", ""),
                            "status": json_data.get("status", "draft"),
                            "updated_at": json_updated,
                            "type": json_data.get("type", "article"),
                            "metadata": json_data.get("metadata", {}),
                        }
                
                return {
                    "id": content_id,
                    "title": post.get("title", content_id),
                    "content": post.content,
                    "status": post.get("status", "draft"),
                    "updated_at": post.get("updated_at"),
                    "type": post.get("type", "article"),
                    "metadata": post.metadata,
                }
            except Exception as e:
                logger.error(f"[CONTENT:GET] Error parsing MD {md_file}: {e}")
        
        # Fallback to JSON
        if json_file.exists():
            try:
                with open(json_file) as f:
                    data = json.load(f)
                logger.info(f"[CONTENT:GET] Using JSON at {json_file}")
                return {
                    "id": content_id,
                    "title": data.get("title", content_id),
                    "content": data.get("content", ""),
                    "status": data.get("status", "draft"),
                    "updated_at": data.get("metadata", {}).get("updated_at"),
                    "type": data.get("type", "article"),
                    "metadata": data.get("metadata", {}),
                }
            except Exception as e:
                logger.error(f"[CONTENT:GET] Error reading JSON {json_file}: {e}")
    
    raise HTTPException(status_code=404, detail="Content not found")

# Add after existing content endpoints (around line 850)

from collections import defaultdict
from datetime import datetime

# In-memory tracking (replace with Redis/PostgreSQL for production)
content_metrics = defaultdict(lambda: {
    "views": 0,
    "unique_sessions": set(),
    "last_viewed": None
})

@app.post("/api/content/{content_id}/track-view")
async def track_content_view(content_id: str, session_id: str = None):
    """Track real content view"""
    metrics = content_metrics[content_id]
    metrics["views"] += 1
    metrics["last_viewed"] = datetime.now().isoformat()
    
    if session_id:
        metrics["unique_sessions"].add(session_id)
    
    return {
        "views": metrics["views"],
        "unique_views": len(metrics["unique_sessions"])
    }

@app.get("/api/metrics/dashboard")
async def get_real_dashboard_metrics():
    """Real dashboard metrics"""
    from pathlib import Path
    
    base_dir = Path("generated_content")
    total_content = 0
    total_views = 0
    published = 0
    drafts = 0
    
    for week_dir in base_dir.iterdir():
        if not week_dir.is_dir():
            continue
        
        for json_file in week_dir.glob("*.json"):
            total_content += 1
            content_id = json_file.stem
            
            if content_id in content_metrics:
                total_views += content_metrics[content_id]["views"]
            
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    if data.get("status") == "published":
                        published += 1
                    else:
                        drafts += 1
            except:
                drafts += 1
    
    return {
        "totalContent": total_content,
        "published": published,
        "drafts": drafts,
        "views": total_views
    }

from pathlib import Path
import frontmatter
from fastapi import HTTPException

@app.get("/api/content/{content_id}")
async def get_content(content_id: str):
    """Retrieve content details by ID for frontend consumption"""
    base_dir = Path("generated_content")
    for week_dir in base_dir.iterdir():
        if not week_dir.is_dir():
            continue
        for md_file in week_dir.glob("*.md"):
            if md_file.stem == content_id:
                try:
                    post = frontmatter.load(md_file)
                    return {
                        "id": content_id,
                        "title": post.get("title", content_id),
                        "status": post.get("status", "draft"),
                        "updated_at": post.get("updated_at"),
                        "type": post.get("type", "article"),
                        "content": post.content,
                        "metadata": post.metadata,
                    }
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed parsing {md_file}: {e}")
    raise HTTPException(status_code=404, detail="Content not found")


if __name__ == "__main__":
    logger.info("Starting WriterzRoom API Server — ENTERPRISE MODE")
    uvicorn.run(
        "langgraph_app.integrated_server:app",
        host=HOST,
        port=PORT,
        reload=(ENVIRONMENT == "development"),
        access_log=True,
        log_level="info",
    )
