# langgraph_app/agents/mcp_enhanced_agents.py

from ..mcp_integration import mcp_manager  
from ..mcp_server_extension import MCPGenerationRequest
from ..enhanced_model_registry import get_model

try:
    from ..mcp_server_extension import (
        initialize_mcp_for_existing_server,
        cleanup_mcp_for_existing_server,
        enhance_generation_with_mcp,
        MCPGenerationRequest
    )
    from ..mcp_enhanced_graph import execute_mcp_enhanced_generation
    MCP_AVAILABLE = True
    print("✅ MCP modules loaded successfully")
except ImportError as e:
    print(f"❌ CRITICAL: MCP modules not available: {e}")
    print("❌ WriterzRoom requires MCP integration to function")
    print("❌ Please ensure MCP modules are properly installed")
    raise ImportError(f"MCP modules are required for WriterzRoom operation: {e}")

"""
Enterprise-grade FastAPI server for WriterzRoom
Unified MCP-integrated content generation system
"""

import asyncio
import os
import uuid
import yaml
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request, Query, Body
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
import uvicorn

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
import structlog

# MCP Integration - fixed imports
MCP_AVAILABLE = False
try:
    from ..mcp_server_extension import (
        initialize_mcp_for_existing_server,
        cleanup_mcp_for_existing_server,
        enhance_generation_with_mcp,
        MCPGenerationRequest
    )
    from ..mcp_enhanced_graph import execute_mcp_enhanced_generation
    MCP_AVAILABLE = True
    print("✅ MCP modules loaded successfully")
except ImportError as e:
    print(f"⚠️ MCP modules not available: {e}")
   
    mcp_options=None

# Enhanced model registry
try:
    from ..enhanced_model_registry import get_model, EnhancedModelRegistry
    print("✅ Model registry loaded successfully")
except ImportError as e:
    print(f"❌ Model registry not available: {e}")

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Configuration
API_KEY = os.getenv("LANGGRAPH_API_KEY", "prod_api_key_2025_secure_content_gen_v1") 
ENVIRONMENT = os.getenv("NODE_ENV", "development")

# Authentication setup
security = HTTPBearer(auto_error=False)

async def get_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Extract API key from Authorization header"""
    if credentials:
        return credentials.credentials
    return None

async def verify_api_key(api_key: Optional[str] = Depends(get_api_key)):
    """Verify API key - optional in development, required in production"""
    if ENVIRONMENT == "production":
        if not api_key or api_key != API_KEY:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key",
                headers={"WWW-Authenticate": "Bearer"}
            )
    return True

# Prometheus metrics registry
custom_registry = CollectorRegistry()

def get_or_create_counter(name, description, labels, registry=None):
    """Get existing counter or create new one, avoiding duplicates"""
    if registry is None:
        registry = custom_registry
    
    try:
        return Counter(name, description, labels, registry=registry)
    except ValueError as e:
        if "Duplicated timeseries" in str(e):
            for collector in registry._collector_to_names:
                if hasattr(collector, '_name') and collector._name == name:
                    return collector
            return Counter(f"{name}_new", description, labels, registry=registry)
        raise

def get_or_create_histogram(name, description, registry=None):
    """Get existing histogram or create new one, avoiding duplicates"""
    if registry is None:
        registry = custom_registry
    
    try:
        return Histogram(name, description, registry=registry)
    except ValueError as e:
        if "Duplicated timeseries" in str(e):
            for collector in registry._collector_to_names:
                if hasattr(collector, '_name') and collector._name == name:
                    return collector
            return Histogram(f"{name}_new", description, registry=registry)
        raise

# Initialize Prometheus metrics
REQUEST_COUNT = get_or_create_counter(
    'agentic_writer_requests_total', 
    'Total requests', 
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = get_or_create_histogram(
    'agentic_writer_request_duration_seconds', 
    'Request duration'
)
GENERATION_COUNT = get_or_create_counter(
    'content_generation_total', 
    'Total content generations', 
    ['status', 'template']
)
GENERATION_DURATION = get_or_create_histogram(
    'content_generation_duration_seconds', 
    'Content generation duration'
)

# Pydantic models
class TemplateParameter(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=200)
    type: str = Field(..., pattern=r'^(string|text|textarea|number|select|boolean|array|date|email|url)$')
    description: Optional[str] = Field(None, max_length=500)
    placeholder: Optional[str] = Field(None, max_length=500)
    default: Optional[Union[str, int, float, bool, List[str]]] = None
    options: Optional[List[str]] = Field(None, max_items=100)
    required: bool = Field(default=False)
    validation: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ContentTemplate(BaseModel):
    id: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
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
    id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(default="general", max_length=100)
    platform: Optional[str] = Field(None, max_length=100)
    tone: Optional[str] = Field(None, max_length=100)
    voice: Optional[str] = Field(None, max_length=100)
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
    template: str = Field(..., min_length=1, max_length=100)
    style_profile: str = Field(..., min_length=1, max_length=100)
    dynamic_parameters: Dict[str, Any] = Field(default_factory=dict, max_items=50)
    priority: int = Field(default=1, ge=1, le=5)
    timeout_seconds: int = Field(default=300, ge=60, le=1800)
    
    @field_validator('dynamic_parameters')
    @classmethod
    def validate_parameters(cls, v):
        for key, value in v.items():
            if isinstance(value, str) and len(value) > 10000:
                raise ValueError(f"Parameter '{key}' exceeds maximum length")
        return v

class GenerationStatus(BaseModel):
    requestId: str
    status: str = Field(..., pattern=r'^(pending|processing|completed|failed|cancelled)$')
    progress: float = Field(..., ge=0.0, le=1.0)
    current_step: str = Field(default="")
    content: str = Field(default="")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

class PaginationMetadata(BaseModel):
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
    totalPages: int = Field(..., ge=0)
    hasNext: bool
    hasPrev: bool

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    requestId: Optional[str] = None

# File loading utilities
def get_template_paths() -> List[str]:
    """Get ordered list of template directory paths"""
    paths = [
        "data/content_templates",
        "../data/content_templates",
        "frontend/content-templates",
        "../frontend/content-templates",
        "content-templates"
    ]
    existing_paths = [path for path in paths if os.path.exists(path)]
    logger.info(f"📂 Template paths found: {existing_paths}")
    return existing_paths

def get_style_profile_paths() -> List[str]:
    """Get ordered list of style profile directory paths"""
    paths = [
        "data/style_profiles",
        "../data/style_profiles",
        "frontend/style-profiles",
        "../frontend/style-profiles",
        "style_profiles",
        "style-profiles"
    ]
    existing_paths = [path for path in paths if os.path.exists(path)]
    logger.info(f"📂 Style profile paths found: {existing_paths}")
    return existing_paths

def load_yaml_file_safe(file_path: str) -> Dict[str, Any]:
    """Load YAML file with comprehensive error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            if content is None:
                logger.warning(f"Empty YAML file: {file_path}")
                return {}
            if not isinstance(content, dict):
                logger.warning(f"Invalid YAML structure in {file_path}: expected dict, got {type(content)}")
                return {}
            return content
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in {file_path}: {e}")
        return {}
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return {}
    except PermissionError:
        logger.error(f"Permission denied reading file: {file_path}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading YAML {file_path}: {e}")
        return {}

def parse_template_parameters(parameters_data: Any) -> Dict[str, TemplateParameter]:
    """Parse parameters from various formats"""
    processed_parameters = {}
    
    if isinstance(parameters_data, dict):
        for key, param in parameters_data.items():
            if isinstance(param, dict):
                processed_parameters[key] = TemplateParameter(
                    name=key,
                    label=param.get('label', key.replace('_', ' ').title()),
                    type=param.get('type', 'string'),
                    description=param.get('description'),
                    placeholder=param.get('placeholder'),
                    default=param.get('default'),
                    options=param.get('options'),
                    required=param.get('required', False)
                )
            else:
                processed_parameters[key] = TemplateParameter(
                    name=key,
                    label=key.replace('_', ' ').title(),
                    type='string',
                    default=param if param is not None else None,
                    required=False
                )
    
    elif isinstance(parameters_data, list):
        for param in parameters_data:
            if isinstance(param, dict) and 'name' in param:
                param_name = param['name']
                processed_parameters[param_name] = TemplateParameter(
                    name=param_name,
                    label=param.get('label', param_name.replace('_', ' ').title()),
                    type=param.get('type', 'string'),
                    description=param.get('description'),
                    placeholder=param.get('placeholder'),
                    default=param.get('default'),
                    options=param.get('options'),
                    required=param.get('required', False)
                )
            elif isinstance(param, str):
                processed_parameters[param] = TemplateParameter(
                    name=param,
                    label=param.replace('_', ' ').title(),
                    type='string',
                    required=False
                )
            elif isinstance(param, dict):
                for key, value in param.items():
                    processed_parameters[key] = TemplateParameter(
                        name=key,
                        label=key.replace('_', ' ').title(),
                        type='string',
                        default=value if not isinstance(value, dict) else None,
                        required=False
                    )
                    break
    
    return processed_parameters

def load_templates() -> List[ContentTemplate]:
    """Load and validate all content templates"""
    templates = []
    
    for template_dir in get_template_paths():
        if not os.path.exists(template_dir):
            continue
            
        try:
            files = os.listdir(template_dir)
            
            for filename in files:
                if not filename.endswith('.yaml'):
                    continue
                
                file_path = os.path.join(template_dir, filename)
                template_data = load_yaml_file_safe(file_path)
                
                if not template_data:
                    continue
                
                try:
                    template_id = template_data.get('id', filename.replace('.yaml', ''))
                    parameters_data = template_data.get("parameters", {})
                    processed_parameters = parse_template_parameters(parameters_data)
                    
                    template = ContentTemplate(
                        id=template_id,
                        slug=template_data.get('slug', template_id),
                        name=template_data.get("name", template_id.replace('_', ' ').title()),
                        description=template_data.get("description", ""),
                        category=template_data.get("category", "general"),
                        defaults=template_data.get("defaults", {}),
                        system_prompt=template_data.get("system_prompt"),
                        structure=template_data.get("structure", {}),
                        research=template_data.get("research", {}),
                        parameters=processed_parameters,
                        metadata=template_data.get("metadata", {}),
                        version=template_data.get("version", "1.0.0"),
                        filename=filename
                    )
                    templates.append(template)
                    logger.info(f"✅ Loaded template: {template.name} ({template.id})")
                    
                except Exception as e:
                    logger.error(f"Invalid template format in {filename}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error loading templates from {template_dir}: {e}")
            continue
    
    logger.info(f"📊 Total templates loaded: {len(templates)}")
    return templates

def load_style_profiles() -> List[StyleProfile]:
    """Load and validate all style profiles"""
    profiles = []
    
    for profile_dir in get_style_profile_paths():
        if not os.path.exists(profile_dir):
            continue
            
        try:
            files = os.listdir(profile_dir)
            
            for filename in files:
                if not filename.endswith('.yaml'):
                    continue
                
                file_path = os.path.join(profile_dir, filename)
                profile_data = load_yaml_file_safe(file_path)
                
                if not profile_data:
                    continue
                
                try:
                    profile_id = profile_data.get('id', filename.replace('.yaml', ''))
                    
                    profile = StyleProfile(
                        id=profile_id,
                        name=profile_data.get("name", profile_id.replace('_', ' ').title()),
                        description=profile_data.get("description", ""),
                        category=profile_data.get("category", "general"),
                        platform=profile_data.get("platform"),
                        tone=profile_data.get("tone"),
                        voice=profile_data.get("voice"),
                        structure=profile_data.get("structure"),
                        audience=profile_data.get("audience"),
                        system_prompt=profile_data.get("system_prompt"),
                        length_limit=profile_data.get("length_limit", {}),
                        settings=profile_data.get("settings", {}),
                        formatting=profile_data.get("formatting", {}),
                        metadata=profile_data.get("metadata", {}),
                        filename=filename
                    )
                    profiles.append(profile)
                    logger.info(f"✅ Loaded style profile: {profile.name} ({profile.id})")
                    
                except Exception as e:
                    logger.error(f"Invalid style profile format in {filename}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error loading style profiles from {profile_dir}: {e}")
            continue
    
    logger.info(f"📊 Total style profiles loaded: {len(profiles)}")
    return profiles

# FIXED: Unified content generation function with proper exception handling
async def execute_content_generation(
    request_id: str,
    template_config: Dict[str, Any],
    style_config: Dict[str, Any],
    app_state,
    mcp_options: Optional[Dict[str, Any]] = None
) -> GenerationStatus:
    """Execute content generation through unified MCP pipeline - FIXED exception handling"""
    start_time = datetime.now()
    
    # FIXED: Initialize result to None before try block
    result = None
    
    try:
        logger.info("Starting MCP-enhanced content generation",
                   requestId=request_id,
                   template=template_config.get("name"),
                   style=style_config.get("name"),
                   mcp_enabled=mcp_options.get('enable_mcp', True) if mcp_options else True)
        
        # Use MCP enhancement if available and enabled
        if MCP_AVAILABLE and getattr(app_state, 'mcp_available', False):
            if mcp_options and mcp_options.get('enable_mcp', True):
                logger.info(f"🚀 Using MCP-enhanced generation for {request_id}")
                result = await enhance_generation_with_mcp(
                    execute_mcp_enhanced_generation,
                    request_id,
                    template_config,
                    style_config,
                    app_state,
                    mcp_options or {}
                )
            else:
                logger.info(f"🔄 Using direct MCP generation for {request_id}")
                result = await execute_mcp_enhanced_generation(
                    request_id=request_id,
                    template_config=template_config,
                    style_config=style_config
                )
        else:
            logger.warning(f"⚠️ MCP not available, falling back to basic generation")
            # Fallback to basic generation if MCP is not available
            result = await execute_mcp_enhanced_generation(
                request_id=request_id,
                template_config=template_config,
                style_config=style_config,
                app_state=app_state,
                mcp_options=mcp_options or {}
            )
        
        # FIXED: Only process result if it was successfully set
        if result:
            logger.info(f"🔍 Generation result type: {type(result)}")
            
            # Extract result data safely
            status_value = result.get("status", "failed")
            progress_value = result.get("progress", 0.0)
            content_value = result.get("content", "")
            metadata_value = result.get("metadata", {})
            errors_value = result.get("errors", [])
            warnings_value = result.get("warnings", [])
            metrics_value = result.get("metrics", {})
            
            logger.info(f"✅ Generation completed: {status_value}, content_length: {len(content_value)}")
            
            # Create status object
            status = GenerationStatus(
                requestId=request_id,
                status=status_value,
                progress=progress_value,
                current_step="Completed" if status_value == "completed" else "Failed",
                content=content_value,
                metadata=metadata_value,
                errors=errors_value,
                warnings=warnings_value,
                metrics=metrics_value,
                created_at=start_time,
                updated_at=datetime.now(),
                completed_at=datetime.now() if status_value in ["completed", "failed"] else None
            )
            
            # Store in app state
            if not hasattr(app_state, 'generation_tasks'):
                app_state.generation_tasks = {}
            app_state.generation_tasks[request_id] = status
            
            # Record metrics
            duration = (datetime.now() - start_time).total_seconds()
            GENERATION_DURATION.observe(duration)
            GENERATION_COUNT.labels(
                status=status_value,
                template=template_config.get("name", "unknown")
            ).inc()
            
            logger.info("Content generation completed successfully",
                       requestId=request_id,
                       status=status_value,
                       duration=duration,
                       mcp_enhanced=mcp_options.get('enable_mcp', True) if mcp_options else True)
            
            return status
        
        # FIXED: Handle case where result is None
        else:
            raise Exception("Generation function returned None")
        
    except Exception as e:
        logger.error("Content generation failed",
                    requestId=request_id,
                    error=str(e),
                    exc_info=True)
        
        error_status = GenerationStatus(
            requestId=request_id,
            status="failed",
            progress=0.0,
            current_step="Failed",
            content="",
            metadata={},
            errors=[f"Generation failed: {str(e)}"],
            warnings=[],
            metrics={},
            created_at=start_time,
            updated_at=datetime.now()
        )
        
        if not hasattr(app_state, 'generation_tasks'):
            app_state.generation_tasks = {}
        app_state.generation_tasks[request_id] = error_status
        
        GENERATION_COUNT.labels(status="failed", template="unknown").inc()
        return error_status

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management with MCP initialization"""
    logger.info("🚀 Starting WriterzRoom API with MCP integration")
    
    # Initialize generation task storage
    app.state.generation_tasks = {}
    
    # Initialize model registry
    try:
        llm = get_model("writer")
        logger.info("✅ Model registry initialized successfully")
    except Exception as e:
        logger.error("❌ Failed to initialize model registry", error=str(e))
    
    # Initialize MCP if available
    if MCP_AVAILABLE:
        try:
            mcp_success = await initialize_mcp_for_existing_server(app)
            app.state.mcp_available = mcp_success if mcp_success else False
            logger.info(f"✅ MCP initialization: {'successful' if app.state.mcp_available else 'failed'}")
        except Exception as e:
            logger.error(f"❌ MCP initialization error: {e}")
            app.state.mcp_available = False
    else:
        app.state.mcp_available = False
    
    logger.info("✅ Server initialization complete")
    
    yield
    
    # Cleanup MCP
    if MCP_AVAILABLE and getattr(app.state, 'mcp_available', False):
        try:
            await cleanup_mcp_for_existing_server(app)
            logger.info("✅ MCP cleanup completed")
        except Exception as e:
            logger.error(f"❌ MCP cleanup error: {e}")
    
    logger.info("🛑 Shutting down WriterzRoom API")

# FastAPI application
app = FastAPI(
    title="WriterzRoom API",
    description="Enterprise-grade AI-powered content generation with unified MCP integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "https://*.vercel.app"],
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
    
    with REQUEST_DURATION.time():
        response = await call_next(request)
    
    duration = (datetime.now() - start_time).total_seconds()
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    response.headers["X-Request-ID"] = requestId
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    logger.info("Request completed",
                requestId=requestId,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration)
    
    return response

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error("HTTP exception",
                 requestId=getattr(request.state, 'requestId', None),
                 status_code=exc.status_code,
                 detail=exc.detail)
    
    response_data = APIResponse(
        success=False,
        error={
            "code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        },
        requestId=getattr(request.state, 'requestId', None)
    ).dict()
    
    response_data["timestamp"] = response_data["timestamp"].isoformat() if isinstance(response_data["timestamp"], datetime) else response_data["timestamp"]
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception",
                 requestId=getattr(request.state, 'requestId', None),
                 error=str(exc),
                 exc_info=True)
    
    response_data = APIResponse(
        success=False,
        error={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        },
        requestId=getattr(request.state, 'requestId', None)
    ).dict()
    
    response_data["timestamp"] = response_data["timestamp"].isoformat() if isinstance(response_data["timestamp"], datetime) else response_data["timestamp"]
    
    return JSONResponse(
        status_code=500,
        content=response_data
    )

# API Endpoints
@app.get("/", response_model=APIResponse)
async def root(request: Request):
    """API root endpoint"""
    return APIResponse(
        success=True,
        data={
            "name": "WriterzRoom API",
            "version": "2.0.0",
            "status": "operational",
            "features": [
                "Unified MCP content generation",
                "Real-time progress tracking",
                "Comprehensive metrics",
                "Template and style management",
                "Production-ready monitoring"
            ],
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "metrics": "/metrics",
                "templates": "/api/templates",
                "styles": "/api/style-profiles",
                "generate": "/api/generate"
            }
        },
        requestId=request.state.requestId
    )

@app.get("/health")
async def health_check(request: Request):
    """Comprehensive health check"""
    try:
        template_count = len(load_templates())
        profile_count = len(load_style_profiles())
        
        template_dirs_exist = any(os.path.exists(path) for path in get_template_paths())
        profile_dirs_exist = any(os.path.exists(path) for path in get_style_profile_paths())
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "mcp_integration": MCP_AVAILABLE,
                "template_directories": template_dirs_exist,
                "style_profile_directories": profile_dirs_exist,
                "api_server": True
            },
            "metrics": {
                "templates_loaded": template_count,
                "profiles_loaded": profile_count,
                "active_generations": len(getattr(app.state, 'generation_tasks', {}))
            },
            "system": {
                "environment": ENVIRONMENT,
                "mcp_enabled": MCP_AVAILABLE
            }
        }
        
        critical_services = [
            health_data["services"]["mcp_integration"],
            health_data["services"]["api_server"]
        ]
        
        all_healthy = all(critical_services)
        
        if not all_healthy:
            health_data["status"] = "unhealthy"
        elif template_count == 0 or profile_count == 0:
            health_data["status"] = "degraded"
        
        return JSONResponse(
            status_code=200 if all_healthy else 503,
            content=health_data
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(custom_registry), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/templates", response_model=APIResponse)
async def list_templates(request: Request, authenticated: bool = Depends(verify_api_key)):
    """List all available content templates"""
    try:
        templates = load_templates()
        
        return APIResponse(
            success=True,
            data={
                "items": [template.dict() for template in templates],
                "count": len(templates)
            },
            requestId=request.state.requestId
        )
        
    except Exception as e:
        logger.error("Failed to load templates", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to load templates")

@app.get("/api/style-profiles", response_model=APIResponse)
async def list_style_profiles(
    request: Request,
    authenticated: bool = Depends(verify_api_key),
    page: int = 1,
    limit: int = 100,
    search: str = "",
    category: str = ""
):
    """List style profiles with pagination and filtering"""
    try:
        profiles = load_style_profiles()
        
        # Apply filters
        if search:
            search_lower = search.lower()
            profiles = [
                p for p in profiles 
                if search_lower in p.name.lower() or 
                   search_lower in (p.description or "").lower()
            ]
        
        if category:
            profiles = [p for p in profiles if p.category.lower() == category.lower()]
        
        # Pagination
        total = len(profiles)
        total_pages = (total + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_profiles = profiles[start_idx:end_idx]
        
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            total=total,
            totalPages=total_pages,
            hasNext=page < total_pages,
            hasPrev=page > 1
        )
        
        return APIResponse(
            success=True,
            data={
                "items": [profile.dict() for profile in paginated_profiles],
                "pagination": pagination.dict()
            },
            requestId=request.state.requestId
        )
        
    except Exception as e:
        logger.error("Failed to load style profiles", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to load style profiles")

@app.post("/api/generate", response_model=APIResponse)
async def generate_content_endpoint(
    request_data: GenerateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    authenticated: bool = Depends(verify_api_key)
):
    """Start content generation through unified MCP pipeline"""
    requestId = str(uuid.uuid4())
    
    try:
        logger.info(f"🔍 Generation request received: {request_data}")
        
        # Load and validate template
        templates = load_templates()
        template = next(
            (t for t in templates if t.id == request_data.template.replace('.yaml', '')),
            None
        )
        
        if not template:
            logger.error(f"Template not found: {request_data.template}")
            logger.error(f"Available templates: {[t.id for t in templates]}")
            raise HTTPException(status_code=404, detail=f"Template not found: {request_data.template}")
        
        # Load and validate style profile
        profiles = load_style_profiles()
        
        # Try multiple ways to find the profile
        profile = None
        search_terms = [
            request_data.style_profile,
            request_data.style_profile.replace('.yaml', ''),
            request_data.style_profile.replace('-', '_'),
            request_data.style_profile.replace('_', '-'),
        ]
        
        for search_term in search_terms:
            profile = next(
                (p for p in profiles if p.id == search_term),
                None
            )
            if profile:
                break
        
        if not profile:
            logger.error(f"Style profile not found: {request_data.style_profile}")
            logger.error(f"Available profiles: {[p.id for p in profiles]}")
            raise HTTPException(
                status_code=404, 
                detail=f"Style profile not found: {request_data.style_profile}. Available: {[p.id for p in profiles]}"
            )
        
        logger.info(f"✅ Found template: {template.name} and profile: {profile.name}")
        
        # Prepare configurations for MCP generation
        template_config = template.dict()
        template_config.update(request_data.dynamic_parameters)
        
        style_config = profile.dict()
        
        # Prepare MCP options
        mcp_options = {
            'enable_mcp': True,  # Always enable MCP by default
            'research_depth': 'moderate',
            'memory_namespace': 'content_generation',
            'timeout_seconds': request_data.timeout_seconds
        }
        
        # Initialize generation status
        initial_status = GenerationStatus(
            requestId=requestId,
            status="pending",
            progress=0.0,
            current_step="Initializing...",
            content="",
            metadata={
                "template": template.name,
                "style_profile": profile.name,
                "started_at": datetime.now().isoformat(),
                "mcp_enabled": mcp_options['enable_mcp']
            },
            errors=[],
            warnings=[],
            metrics={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        if not hasattr(app.state, 'generation_tasks'):
            app.state.generation_tasks = {}
        app.state.generation_tasks[requestId] = initial_status
        
        # Start background generation through MCP pipeline
        background_tasks.add_task(
            execute_content_generation,
            requestId,
            template_config,
            style_config,
            app.state,
            mcp_options
        )
        
        logger.info("Content generation initiated",
                   requestId=requestId,
                   template=template.name,
                   style_profile=profile.name,
                   mcp_enabled=mcp_options['enable_mcp'])
        
        return APIResponse(
            success=True,
            data={
                "requestId": requestId,
                "status": "pending",
                "metadata": initial_status.metadata
            },
            requestId=request.state.requestId
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start generation", 
                    error=str(e), 
                    requestId=requestId)
        raise HTTPException(status_code=500, detail="Failed to start content generation")

@app.get("/api/generate/{requestId}", response_model=APIResponse)
async def get_generation_result(requestId: str, request: Request, authenticated: bool = Depends(verify_api_key)):
    """Get generation status or final result"""
    if not hasattr(app.state, 'generation_tasks') or requestId not in app.state.generation_tasks:
        raise HTTPException(status_code=404, detail="Generation request not found")
    
    status = app.state.generation_tasks[requestId]
    
    return APIResponse(
        success=True,
        data=status.dict(),
        requestId=request.state.requestId
    )

@app.delete("/api/generate/{requestId}")
async def cancel_generation(requestId: str, request: Request, authenticated: bool = Depends(verify_api_key)):
    """Cancel an ongoing generation"""
    if not hasattr(app.state, 'generation_tasks') or requestId not in app.state.generation_tasks:
        raise HTTPException(status_code=404, detail="Generation request not found")
    
    status = app.state.generation_tasks[requestId]
    if status.status in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed generation")
    
    # Update status to cancelled
    status.status = "cancelled"
    status.updated_at = datetime.now()
    app.state.generation_tasks[requestId] = status
    
    logger.info("Generation cancelled", requestId=requestId)
    
    return APIResponse(
        success=True,
        data={"message": "Generation cancelled successfully"},
        requestId=request.state.requestId
    )

@app.get("/status/{requestId}")
async def get_generation_status(requestId: str, request: Request):
    """Get generation status - frontend compatibility endpoint"""
    try:
        logger.info(f"🔍 Status check for request: {requestId}")
        
        if not hasattr(app.state, 'generation_tasks') or requestId not in app.state.generation_tasks:
            logger.warning(f"❌ Request {requestId} not found")
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
        
        logger.info(f"✅ Status found: {status.status}, content_length: {len(status.content)}")
        
        response_data = {
            "success": True,
            "data": {
                "requestId": requestId,
                "status": status.status,
                "progress": status.progress,
                "current_step": status.current_step,
                "content": status.content,
                "metadata": status.metadata,
                "errors": status.errors,
                "warnings": status.warnings,
                "metrics": status.metrics,
                "created_at": status.created_at.isoformat() if status.created_at else None,
                "updated_at": status.updated_at.isoformat() if status.updated_at else None,
                "completed_at": status.completed_at.isoformat() if status.completed_at else None
            },
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "requestId": requestId
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error("Status check failed", requestId=requestId, error=str(e))
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Status check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "requestId": requestId
            }
        )

# MCP Enhanced Generation Endpoint
@app.post("/api/generate-mcp", response_model=APIResponse)
async def generate_content_with_explicit_mcp(
    request_data: MCPGenerationRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    authenticated: bool = Depends(verify_api_key)
):
    """Generate content with explicit MCP enhancement and advanced options"""
    
    # Convert to standard request format
    standard_request = GenerateRequest(
        template=request_data.template,
        style_profile=request_data.style_profile,
        dynamic_parameters=request_data.dynamic_parameters,
        priority=request_data.priority,
        timeout_seconds=request_data.timeout_seconds
    )
    
    requestId = str(uuid.uuid4())
    
    try:
        # Load and validate template and profile (same as regular endpoint)
        templates = load_templates()
        template = next(
            (t for t in templates if t.id == request_data.template.replace('.yaml', '')),
            None
        )
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {request_data.template}")
        
        profiles = load_style_profiles()
        profile = None
        search_terms = [
            request_data.style_profile,
            request_data.style_profile.replace('.yaml', ''),
            request_data.style_profile.replace('-', '_'),
            request_data.style_profile.replace('_', '-'),
        ]
        
        for search_term in search_terms:
            profile = next((p for p in profiles if p.id == search_term), None)
            if profile:
                break
        
        if not profile:
            raise HTTPException(status_code=404, detail=f"Style profile not found: {request_data.style_profile}")
        
        # Prepare configurations with MCP-specific options
        template_config = template.dict()
        template_config.update(request_data.dynamic_parameters)
        
        style_config = profile.dict()
        
        # Enhanced MCP options
        mcp_options = {
            'enable_mcp': request_data.enable_mcp,
            'research_depth': request_data.research_depth,
            'memory_namespace': 'mcp_enhanced_generation',
            'timeout_seconds': request_data.timeout_seconds,
            'priority': request_data.priority,
            'advanced_features': True
        }
        
        # Initialize status
        initial_status = GenerationStatus(
            requestId=requestId,
            status="pending",
            progress=0.0,
            current_step="Initializing MCP generation...",
            content="",
            metadata={
                "template": template.name,
                "style_profile": profile.name,
                "started_at": datetime.now().isoformat(),
                "mcp_enabled": mcp_options['enable_mcp'],
                "research_depth": mcp_options['research_depth'],
                "generation_type": "mcp_enhanced"
            },
            errors=[],
            warnings=[],
            metrics={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        if not hasattr(app.state, 'generation_tasks'):
            app.state.generation_tasks = {}
        app.state.generation_tasks[requestId] = initial_status
        
        # Start MCP-enhanced generation
        background_tasks.add_task(
            execute_content_generation,
            requestId,
            template_config,
            style_config,
            app.state,
            mcp_options
        )
        
        logger.info("MCP-enhanced content generation initiated",
                   requestId=requestId,
                   template=template.name,
                   style_profile=profile.name,
                   mcp_enabled=mcp_options['enable_mcp'],
                   research_depth=mcp_options['research_depth'])
        
        return APIResponse(
            success=True,
            data={
                "requestId": requestId,
                "status": "pending",
                "metadata": initial_status.metadata
            },
            requestId=request.state.requestId
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start MCP generation", 
                    error=str(e), 
                    requestId=requestId)
        raise HTTPException(status_code=500, detail="Failed to start MCP content generation")

@app.get("/api/content")
async def list_content():
    """List all content items"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        content_items = []
        total_views = 0
        published_count = 0
        draft_count = 0
        
        if content_dir.exists():
            for week_dir in content_dir.iterdir():
                if not week_dir.is_dir():
                    continue
                
                for json_file in week_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        content_id = json_file.stem
                        status = metadata.get('status', 'draft')
                        views = metadata.get('views', 0)
                        
                        total_views += views
                        if status == 'published':
                            published_count += 1
                        else:
                            draft_count += 1
                        
                        content_items.append({
                            "id": content_id,
                            "title": metadata.get('title', content_id.replace('_', ' ').title()),
                            "status": status,
                            "type": metadata.get('type', 'article'),
                            "date": metadata.get('createdAt', datetime.now().isoformat()),
                            "createdAt": metadata.get('createdAt', datetime.now().isoformat()),
                            "updatedAt": metadata.get('updatedAt', datetime.now().isoformat()),
                            "views": views,
                            "week": week_dir.name
                        })
                    except Exception as e:
                        logger.warning(f"Error processing {json_file}: {e}")
                        continue
        
        content_items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
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
        return {
            "content": [], 
            "totalViews": 0,
            "stats": {"total": 0, "published": 0, "drafts": 0, "types": 0}
        }

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        stats = {
            "total": 0,
            "totalContent": 0,
            "drafts": 0,
            "published": 0,
            "views": 0,
            "recentContent": [],
            "recentActivity": []
        }
        
        recent_items = []
        cutoff_date = datetime.now() - timedelta(days=30)
        
        if content_dir.exists():
            for week_dir in content_dir.iterdir():
                if not week_dir.is_dir():
                    continue
                    
                for json_file in week_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        stats["total"] += 1
                        stats["totalContent"] += 1
                        stats["views"] += metadata.get('views', 0)
                        
                        status = metadata.get('status', 'draft')
                        if status == 'published':
                            stats["published"] += 1
                        else:
                            stats["drafts"] += 1
                        
                        created_at = metadata.get('createdAt', metadata.get('updatedAt'))
                        if created_at:
                            try:
                                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            except:
                                created_date = datetime.now()
                        else:
                            created_date = datetime.now()
                        
                        if created_date >= cutoff_date:
                            content_id = json_file.stem
                            recent_items.append({
                                "id": content_id,
                                "title": metadata.get('title', content_id.replace('_', ' ').title()),
                                "status": status,
                                "updatedAt": metadata.get('updatedAt', created_at or datetime.now().isoformat()),
                                "type": metadata.get('type', 'article'),
                                "createdAt": created_at or datetime.now().isoformat()
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error processing {json_file}: {e}")
                        continue
        
        recent_items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        stats["recentContent"] = recent_items[:5]
        
        stats["recentActivity"] = [
            {
                "id": f"activity-{item['id']}",
                "type": "created" if item["status"] == "draft" else "published",
                "description": f"{'Published' if item['status'] == 'published' else 'Created'} \"{item['title']}\"",
                "timestamp": item["updatedAt"]
            }
            for item in stats["recentContent"]
        ]
        
        return stats
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return {
            "total": 0,
            "totalContent": 0,
            "drafts": 0,
            "published": 0,
            "views": 0,
            "recentContent": [],
            "recentActivity": []
        }

@app.get("/api/content/{content_id}")
async def get_content(content_id: str):
    """Get specific content item"""
    base_path = Path(__file__).parent.parent
    content_dir = base_path / "generated_content"
    
    for week_dir in content_dir.iterdir():
        if not week_dir.is_dir():
            continue
        
        json_file = week_dir / f"{content_id}.json"
        md_file = week_dir / f"{content_id}.md"
        
        if json_file.exists():
            with open(json_file, 'r') as f:
                metadata = json.load(f)
            
            content = metadata.get('content', '')
            if md_file.exists():
                with open(md_file, 'r') as f:
                    content = f.read()
            
            return {
                "id": content_id,
                "title": metadata.get('title', content_id.replace('_', ' ').title()),
                "content": content,
                "contentHtml": metadata.get('contentHtml'),
                "status": metadata.get('status', 'draft'),
                "type": metadata.get('type', 'article'),
                "createdAt": metadata.get('createdAt'),
                "updatedAt": metadata.get('updatedAt'),
                "views": metadata.get('views', 0),
                "author": metadata.get('author'),
                "metadata": metadata.get('metadata', {}),
                "week": week_dir.name
            }
    
    raise HTTPException(status_code=404, detail="Content not found")

# Debug endpoints
@app.get("/debug/mcp-status")
async def debug_mcp_status(request: Request):
    """Debug MCP integration status"""
    return APIResponse(
        success=True,
        data={
            "mcp_modules_available": MCP_AVAILABLE,
            "mcp_runtime_available": getattr(app.state, 'mcp_available', False),
            "environment": ENVIRONMENT,
            "template_paths": get_template_paths(),
            "style_profile_paths": get_style_profile_paths(),
            "templates_loaded": len(load_templates()),
            "profiles_loaded": len(load_style_profiles()),
            "active_generations": len(getattr(app.state, 'generation_tasks', {})),
            "integration_type": "mcp_enhanced",
            "mcp_features": [
                "Tool discovery",
                "Memory management", 
                "Enhanced research",
                "Agent coordination",
                "Real-time collaboration"
            ] if MCP_AVAILABLE else []
        },
        requestId=request.state.requestId
    )

@app.get("/debug/integration-status")
async def debug_integration_status(request: Request):
    """Debug unified integration status"""
    return APIResponse(
        success=True,
        data={
            "mcp_available": MCP_AVAILABLE,
            "mcp_runtime_status": getattr(app.state, 'mcp_available', False),
            "environment": ENVIRONMENT,
            "template_paths": get_template_paths(),
            "style_profile_paths": get_style_profile_paths(),
            "templates_loaded": len(load_templates()),
            "profiles_loaded": len(load_style_profiles()),
            "active_generations": len(getattr(app.state, 'generation_tasks', {})),
            "integration_type": "mcp_enhanced" if MCP_AVAILABLE else "fallback",
            "agent_coordination": "enabled" if MCP_AVAILABLE else "basic"
        },
        requestId=request.state.requestId
    )

if __name__ == "__main__":
    print("🚀 Starting WriterzRoom API Server")
    print(f"🔧 MCP Integration: {MCP_AVAILABLE}")
    print(f"🔐 Environment: {ENVIRONMENT}")
    print(f"🔑 Auth Required: {'Yes' if ENVIRONMENT == 'production' else 'No (dev mode)'}")
    
    uvicorn.run(
        "integrated_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )