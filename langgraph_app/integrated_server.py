"""
Enterprise-grade FastAPI server for WriterzRoom
Integrates with LangGraph enhanced content generation system
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
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request


from fastapi import status  # Import status separately to fix the issue
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
import uvicorn

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
import structlog

# MCP Integration - with graceful fallback
MCP_AVAILABLE = False
try:
    from .mcp_server_extension import (
        initialize_mcp_for_existing_server,
        cleanup_mcp_for_existing_server,
        enhance_generation_with_mcp,
        MCPGenerationRequest
    )
    MCP_AVAILABLE = True
    print("✅ MCP modules loaded successfully")
except ImportError:
    print("⚠️ MCP modules not available, continuing without MCP")

# Import your enhanced graph system
LANGGRAPH_AVAILABLE = False
try:
    from .enhanced_graph import (
        EnhancedContentGraph, 
        AgentState, 
        ProcessingStatus,
        MetricsCollector
    )
    # Import the enhanced model registry
    from .enhanced_model_registry import get_model, EnhancedModelRegistry
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph modules loaded successfully")
except ImportError as e:
    print(f"❌ LangGraph modules not available: {e}")
    print("❌ This server requires LangGraph modules to function properly")
    raise ImportError("LangGraph modules are required for this server to function")

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
                status_code=401,  # Use the actual status code number
                detail="Invalid or missing API key",
                headers={"WWW-Authenticate": "Bearer"}
            )
    # In development, auth is optional
    return True

# Create a custom registry for this application to avoid conflicts
custom_registry = CollectorRegistry()

# Prometheus metrics with error handling for duplicates
def get_or_create_counter(name, description, labels, registry=None):
    """Get existing counter or create new one, avoiding duplicates"""
    if registry is None:
        registry = custom_registry
    
    try:
        # Try to create the counter
        return Counter(name, description, labels, registry=registry)
    except ValueError as e:
        if "Duplicated timeseries" in str(e):
            # If it already exists, find and return it
            for collector in registry._collector_to_names:
                if hasattr(collector, '_name') and collector._name == name:
                    return collector
            # If we can't find it, create with a slightly different name
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
            # If it already exists, find and return it
            for collector in registry._collector_to_names:
                if hasattr(collector, '_name') and collector._name == name:
                    return collector
            # If we can't find it, create with a slightly different name
            return Histogram(f"{name}_new", description, registry=registry)
        raise

# Initialize Prometheus metrics safely
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

# Models and utils
class EnterpriseGenerationRequest(BaseModel):
    prompt: Dict[str, Any]
    preferences: Dict[str, Any]
    workflow: str
    generation_mode: str = Field(default="enterprise", pattern="^(standard|premium|enterprise)$")

class GenerationResponse(BaseModel):
    success: bool = True
    generation_id: str
    status: str = "queued"
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    estimated_completion: Optional[str] = None

# Custom JSON encoder for datetime serialization
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Advanced file loading with caching and validation
def get_template_paths() -> List[str]:
    """Get ordered list of template directory paths"""
    paths = [
        "data/content_templates",          # Relative to current directory
        "../data/content_templates",       # One level up (if running from langgraph_app)
        "frontend/content-templates",      # Frontend directory
        "../frontend/content-templates",   # Frontend one level up
        "content-templates"                # Generic fallback
    ]
    existing_paths = [path for path in paths if os.path.exists(path)]
    logger.info(f"📂 Template paths checked: {paths}")
    logger.info(f"📂 Template paths found: {existing_paths}")
    return existing_paths

def get_style_profile_paths() -> List[str]:
    """Get ordered list of style profile directory paths"""
    paths = [
        "data/style_profiles",            # Relative to current directory  
        "../data/style_profiles",         # One level up (if running from langgraph_app)
        "frontend/style-profiles",        # Frontend directory
        "../frontend/style-profiles",     # Frontend one level up
        "style_profiles",                 # Generic fallback
        "style-profiles"                  # Alternative naming
    ]
    existing_paths = [path for path in paths if os.path.exists(path)]
    logger.info(f"📂 Style profile paths checked: {paths}")
    logger.info(f"📂 Style profile paths found: {existing_paths}")
    return existing_paths

def load_yaml_file_safe(file_path: str) -> Dict[str, Any]:
    """Load YAML file with comprehensive error handling - FIXED VERSION"""
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

    # Pydantic models with comprehensive validation
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
    
    # Enhanced fields for unified structure
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
    
    # Enhanced fields for unified structure
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
        # Validate parameter values
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

def parse_template_parameters(parameters_data: Any) -> Dict[str, TemplateParameter]:
    """Parse parameters from various formats (dict, list, or mixed) - FIXED VERSION"""
    processed_parameters = {}
    
    if isinstance(parameters_data, dict):
        # Handle dict format: {param_name: {config...}}
        for key, param in parameters_data.items():
            if isinstance(param, dict):
                # Full parameter specification
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
                # Simple parameter (just name and value)
                processed_parameters[key] = TemplateParameter(
                    name=key,
                    label=key.replace('_', ' ').title(),
                    type='string',
                    default=param if param is not None else None,
                    required=False
                )
    
    elif isinstance(parameters_data, list):
        # Handle list format: [{name: ..., type: ...}, ...] or [param_name1, param_name2, ...]
        for param in parameters_data:
            if isinstance(param, dict) and 'name' in param:
                # Full parameter dict with name field
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
                # Simple string parameter
                processed_parameters[param] = TemplateParameter(
                    name=param,
                    label=param.replace('_', ' ').title(),
                    type='string',
                    required=False
                )
            elif isinstance(param, dict):
                # Dict without explicit 'name' field - use first key as name
                for key, value in param.items():
                    processed_parameters[key] = TemplateParameter(
                        name=key,
                        label=key.replace('_', ' ').title(),
                        type='string',
                        default=value if not isinstance(value, dict) else None,
                        required=False
                    )
                    break  # Only process first key-value pair
    
    else:
        # Handle other types or empty
        logger.warning(f"Unexpected parameters format: {type(parameters_data)}")
    
    return processed_parameters

def load_templates() -> List[ContentTemplate]:
    """Load and validate all content templates with dynamic structure handling"""
    templates = []
    
    for template_dir in get_template_paths():
        logger.info(f"📁 Checking template directory: {template_dir}")
        
        if not os.path.exists(template_dir):
            logger.warning(f"Template directory does not exist: {template_dir}")
            continue
            
        try:
            files = os.listdir(template_dir)
            logger.info(f"Files found in {template_dir}: {files}")
            
            for filename in files:
                if not filename.endswith('.yaml'):
                    logger.debug(f"Skipping non-YAML file: {filename}")
                    continue
                
                file_path = os.path.join(template_dir, filename)
                logger.info(f"📄 Loading template: {file_path}")
                template_data = load_yaml_file_safe(file_path)
                
                if not template_data:
                    logger.warning(f"Empty or invalid YAML in: {file_path}")
                    continue
                
                try:
                    # Get the template ID from filename or data
                    template_id = template_data.get('id', filename.replace('.yaml', ''))
                    
                    # Parse parameters dynamically
                    parameters_data = template_data.get("parameters", {})
                    logger.info(f"Processing parameters for {filename}: type={type(parameters_data)}, value={parameters_data}")
                    
                    processed_parameters = parse_template_parameters(parameters_data)
                    
                    # Create template with enhanced structure
                    template = ContentTemplate(
                        id=template_id,
                        slug=template_data.get('slug', template_id),
                        name=template_data.get("name", template_id.replace('_', ' ').title()),
                        description=template_data.get("description", ""),
                        category=template_data.get("category", "general"),
                        
                        # Enhanced fields
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
                    logger.info(f"✅ Successfully loaded template: {template.name} (ID: {template.id}) with {len(processed_parameters)} parameters")
                    
                except Exception as e:
                    logger.error("Invalid template format", 
                                filename=filename, 
                                error=str(e),
                                template_data_keys=list(template_data.keys()) if isinstance(template_data, dict) else "Not a dict")
                    continue
        
        except Exception as e:
            logger.error("Error loading templates from directory", 
                        directory=template_dir, 
                        error=str(e))
            continue
    
    logger.info(f"📊 Total templates loaded: {len(templates)}")
    for template in templates:
        logger.info(f"  - {template.id}: {template.name}")
    
    return templates

def load_style_profiles() -> List[StyleProfile]:
    """Load and validate all style profiles with enhanced structure"""
    profiles = []
    
    for profile_dir in get_style_profile_paths():
        logger.info(f"📁 Checking style profile directory: {profile_dir}")
        
        if not os.path.exists(profile_dir):
            logger.warning(f"Style profile directory does not exist: {profile_dir}")
            continue
            
        try:
            files = os.listdir(profile_dir)
            logger.info(f"Files found in {profile_dir}: {files}")
            
            for filename in files:
                if not filename.endswith('.yaml'):
                    logger.debug(f"Skipping non-YAML file: {filename}")
                    continue
                
                file_path = os.path.join(profile_dir, filename)
                logger.info(f"📄 Loading style profile: {file_path}")
                profile_data = load_yaml_file_safe(file_path)
                
                if not profile_data:
                    logger.warning(f"Empty or invalid YAML in: {file_path}")
                    continue
                
                try:
                    # Get the profile ID from filename or data
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
                        
                        # Enhanced fields
                        system_prompt=profile_data.get("system_prompt"),
                        length_limit=profile_data.get("length_limit", {}),
                        settings=profile_data.get("settings", {}),
                        formatting=profile_data.get("formatting", {}),
                        
                        metadata=profile_data.get("metadata", {}),
                        filename=filename
                    )
                    profiles.append(profile)
                    logger.info(f"✅ Successfully loaded style profile: {profile.name} (ID: {profile.id})")
                    
                except Exception as e:
                    logger.error("Invalid style profile format", 
                                filename=filename, 
                                error=str(e),
                                profile_data_type=type(profile_data).__name__)
                    continue
        
        except Exception as e:
            logger.error("Error loading style profiles from directory", 
                        directory=profile_dir, 
                        error=str(e))
            continue
    
    logger.info(f"📊 Total style profiles loaded: {len(profiles)}")
    return profiles

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("🚀 Starting Agentic Writer API")
    
    # Initialize content graph
    try:
        from .enhanced_model_registry import get_model
        llm = get_model("writer")
        app.state.content_graph = EnhancedContentGraph(llm)
        app.state.generation_tasks = {}
        app.state.metrics_collector = MetricsCollector()
        logger.info("✅ Content graph initialized successfully")
    except Exception as e:
        logger.error("❌ Failed to initialize content graph", error=str(e))
        # Create a mock LLM for development
        class MockLLM:
            async def ainvoke(self, prompt):
                return "Mock response"
        
        app.state.content_graph = EnhancedContentGraph(MockLLM())
        app.state.generation_tasks = {}
        app.state.metrics_collector = MetricsCollector()
        logger.warning("⚠️ Using mock LLM for development")
    
    # Rest of MCP initialization stays the same...
    if MCP_AVAILABLE:
        try:
            mcp_success = await initialize_mcp_for_existing_server(app)
            app.state.mcp_available = mcp_success if mcp_success else False
        except Exception as e:
            logger.error(f"❌ MCP initialization error: {e}")
            app.state.mcp_available = False
    else:
        app.state.mcp_available = False
    
    yield
    
    # Cleanup
    if MCP_AVAILABLE and getattr(app.state, 'mcp_available', False):
        try:
            await cleanup_mcp_for_existing_server(app)
        except Exception as e:
            logger.error(f"❌ MCP cleanup error: {e}")
    
    logger.info("🛑 Shutting down Agentic Writer API")
# FastAPI application with advanced configuration
app = FastAPI(
    title="WriterzRoom API",
    description="Enterprise-grade AI-powered content generation using LangGraph",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Background task for content generation
async def generate_content_task(
    requestId: str,
    template_config: Dict[str, Any],
    style_config: Dict[str, Any],
    app_state,
    mcp_options: Optional[Dict[str, Any]] = None
):
    """Execute content generation with full monitoring - ENHANCED WITH MCP"""
# CRITICAL FIX: Extract original_generation function in integrated_server.py
# Replace the nested function with this standalone function

async def original_generation(request_id, template_config, style_config, app_state):
    """FIXED: Handle LangGraph AddableValuesDict results properly"""
    start_time = datetime.now()
    
    try:
        logger.info("Starting content generation",
                   requestId=request_id,
                   template=template_config.get("name"),
                   style=style_config.get("name"))
        
        # Use your enhanced graph
        result = await app_state.content_graph.generate_content(
            request_id=request_id,
            template_config=template_config,
            style_config=style_config
        )
        
        # CRITICAL FIX: LangGraph returns AddableValuesDict, extract values safely
        logger.info(f"🔍 Result type: {type(result)}")
        
        try:
            # Extract all values from the LangGraph result dict
            status_value = result.get("status", "failed")
            progress_value = result.get("progress", 0.0)
            content_value = result.get("content", "")
            metadata_value = result.get("metadata", {})
            errors_value = result.get("errors", [])
            warnings_value = result.get("warnings", [])
            metrics_value = result.get("metrics", {})
            started_at_value = result.get("started_at")
            completed_at_value = result.get("completed_at")
            
            logger.info(f"✅ Extracted status: {status_value}, content_length: {len(content_value)}")
            
        except Exception as extract_error:
            logger.error(f"❌ Failed to extract from result: {extract_error}")
            # Use fallback values
            status_value = "failed"
            progress_value = 0.0
            content_value = ""
            metadata_value = {}
            errors_value = [f"Result extraction failed: {str(extract_error)}"]
            warnings_value = []
            metrics_value = {}
            started_at_value = None
            completed_at_value = None
        
        # Convert to API format
        status = GenerationStatus(
            requestId=request_id,
            status=status_value,
            progress=progress_value,
            current_step="Completed" if status_value == "completed" else "Failed" if status_value == "failed" else "Processing",
            content=content_value,
            metadata=metadata_value,
            errors=errors_value,
            warnings=warnings_value,
            metrics=metrics_value,
            created_at=datetime.fromisoformat(started_at_value) if started_at_value and isinstance(started_at_value, str) else start_time,
            updated_at=datetime.now(),
            completed_at=datetime.fromisoformat(completed_at_value) if completed_at_value and isinstance(completed_at_value, str) else None
        )
        
        app_state.generation_tasks[request_id] = status
        
        # Record metrics
        duration = (datetime.now() - start_time).total_seconds()
        GENERATION_DURATION.observe(duration)
        GENERATION_COUNT.labels(
            status=status_value,
            template=template_config.get("name", "unknown")
        ).inc()
        
        logger.info("Content generation completed",
                   requestId=request_id,
                   status=status_value,
                   duration=duration,
                   word_count=metrics_value.get("word_count", 0))
        
        return status
        
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
        
        app_state.generation_tasks[request_id] = error_status
        GENERATION_COUNT.labels(status="failed", template="unknown").inc()
        return error_status
    
async def generate_content_task(
    requestId: str,
    template_config: Dict[str, Any],
    style_config: Dict[str, Any],
    app_state,
    mcp_options: Optional[Dict[str, Any]] = None
):
    """Execute content generation with full monitoring - FIXED"""
    
    # Use MCP enhancement if available
    if MCP_AVAILABLE and mcp_options and mcp_options.get('enable_mcp', False) and getattr(app_state, 'mcp_available', False):
        logger.info(f"🚀 Using MCP-enhanced generation for {requestId}")
        return await enhance_generation_with_mcp(
            original_generation,
            requestId,
            template_config,
            style_config,
            app_state,
            mcp_options
        )
    else:
        logger.info(f"🔄 Using standard generation for {requestId}")
        return await original_generation(requestId, template_config, style_config, app_state)
# Advanced middleware stack
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

# Advanced exception handling
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
    
    # Convert datetime objects to strings
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
    
    # Convert datetime objects to strings
    response_data["timestamp"] = response_data["timestamp"].isoformat() if isinstance(response_data["timestamp"], datetime) else response_data["timestamp"]
    
    return JSONResponse(
        status_code=500,
        content=response_data
    )

# API Endpoints
# Replace the existing get_dashboard_stats function in integrated_server.py with this fixed version
# Add these missing endpoints to your integrated_server.py

# File: langgraph_app/integrated_server.py
# Update your /api/content endpoint to match what the frontend expects:

@app.get("/api/content")
async def list_content():
    """List all content items for content page"""
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
                        
                        # Count stats
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
        
        # Sort by creation date, newest first
        content_items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        # Return structure that matches frontend expectations
        return {
            "content": content_items,
            "totalViews": total_views,
            "stats": {
                "total": len(content_items),      # Frontend expects stats.total
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
            "stats": {
                "total": 0,
                "published": 0,
                "drafts": 0,
                "types": 0
            }
        }
    
@app.get("/api/dashboard/activity")
async def get_dashboard_activity():
    """Get recent activity for dashboard"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        activities = []
        
        if content_dir.exists():
            for week_dir in content_dir.iterdir():
                if not week_dir.is_dir():
                    continue
                
                for json_file in week_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        content_id = json_file.stem
                        title = metadata.get('title', content_id.replace('_', ' ').title())
                        status = metadata.get('status', 'draft')
                        timestamp = metadata.get('updatedAt', metadata.get('createdAt', datetime.now().isoformat()))
                        
                        activities.append({
                            "id": f"activity-{content_id}",
                            "type": "published" if status == "published" else "created",
                            "description": f"{'Published' if status == 'published' else 'Created'} \"{title}\"",
                            "timestamp": timestamp
                        })
                    except Exception as e:
                        logger.warning(f"Error processing activity {json_file}: {e}")
                        continue
        
        # Sort by timestamp, newest first, and limit to 10
        activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {"activities": activities[:10]}
        
    except Exception as e:
        logger.error(f"Dashboard activity error: {e}")
        return {"activities": []}


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics with correct structure"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        stats = {
            "total": 0,           # Frontend expects 'total', not 'totalContent'
            "totalContent": 0,    # Keep both for compatibility
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
                        
                        # Update stats
                        stats["totalContent"] += 1
                        stats["views"] += metadata.get('views', 0)
                        
                        # Determine status
                        status = metadata.get('status', 'draft')
                        if status == 'published':
                            stats["published"] += 1
                        else:
                            stats["drafts"] += 1
                        
                        # Parse creation date
                        created_at = metadata.get('createdAt', metadata.get('updatedAt'))
                        if created_at:
                            try:
                                if isinstance(created_at, str):
                                    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                else:
                                    created_date = datetime.now()
                            except:
                                created_date = datetime.now()
                        else:
                            created_date = datetime.now()
                        
                        # Add to recent items if within cutoff
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
        
        # Sort recent items by creation date and take top 5
        recent_items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        stats["recentContent"] = recent_items[:5]
        
        # Generate recent activity from recent content
        stats["recentActivity"] = [
            {
                "id": f"activity-{item['id']}",
                "type": "created" if item["status"] == "draft" else "published",
                "description": f"{'Published' if item['status'] == 'published' else 'Created'} \"{item['title']}\"",
                "timestamp": item["updatedAt"]
            }
            for item in stats["recentContent"]
        ]
        
        # Ensure arrays are properly formatted
        if not isinstance(stats["recentContent"], list):
            stats["recentContent"] = []
        if not isinstance(stats["recentActivity"], list):
            stats["recentActivity"] = []
            
        logger.info(f"Dashboard stats generated: {stats['totalContent']} total, {len(stats['recentContent'])} recent")
        
        return stats
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        # Return safe fallback with proper structure
        return {
            "totalContent": 0,
            "drafts": 0,
            "published": 0,
            "views": 0,
            "recentContent": [],  # Always return empty array, never null/undefined
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

@app.put("/api/content/{content_id}")
async def update_content(content_id: str, data: dict):
    """Update content item"""
    base_path = Path(__file__).parent.parent
    content_dir = base_path / "generated_content"
    
    for week_dir in content_dir.iterdir():
        if not week_dir.is_dir():
            continue
        
        json_file = week_dir / f"{content_id}.json"
        if json_file.exists():
            with open(json_file, 'r') as f:
                metadata = json.load(f)
            
            metadata.update(data)
            metadata['updatedAt'] = datetime.now().isoformat()
            
            with open(json_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            if 'content' in data:
                md_file = week_dir / f"{content_id}.md"
                with open(md_file, 'w') as f:
                    f.write(data['content'])
            
            return {"success": True, "message": "Content updated"}
    
    raise HTTPException(status_code=404, detail="Content not found")

@app.delete("/api/content/{content_id}")
async def delete_content(content_id: str):
    """Delete content item"""
    base_path = Path(__file__).parent.parent
    content_dir = base_path / "generated_content"
    
    for week_dir in content_dir.iterdir():
        if not week_dir.is_dir():
            continue
        
        json_file = week_dir / f"{content_id}.json"
        md_file = week_dir / f"{content_id}.md"
        
        if json_file.exists():
            json_file.unlink()
            if md_file.exists():
                md_file.unlink()
            return {"success": True, "message": "Content deleted"}
    
    raise HTTPException(status_code=404, detail="Content not found")

@app.get("/", response_model=APIResponse)
async def root(request: Request):
    """API root endpoint with system information"""
    return APIResponse(
        success=True,
        data={
            "name": "Agentic Writer API",
            "version": "2.0.0",
            "status": "operational",
            "features": [
                "Enhanced LangGraph content generation",
                "Real-time progress tracking",
                "Comprehensive metrics",
                "Template and style management",
                "Production-ready monitoring",
                "MCP integration" if MCP_AVAILABLE else "Standard generation"
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
        
        # Check if template/profile directories exist (more lenient check)
        template_dirs_exist = any(os.path.exists(path) for path in get_template_paths())
        profile_dirs_exist = any(os.path.exists(path) for path in get_style_profile_paths())
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "content_graph": hasattr(app.state, 'content_graph'),
                "template_directories": template_dirs_exist,
                "style_profile_directories": profile_dirs_exist,
                "api_server": True,
                "mcp_available": getattr(app.state, 'mcp_available', False)
            },
            "metrics": {
                "templates_loaded": template_count,
                "profiles_loaded": profile_count,
                "active_generations": len(getattr(app.state, 'generation_tasks', {})),
                "template_directories_found": len(get_template_paths()),
                "style_directories_found": len(get_style_profile_paths())
            },
            "paths": {
                "template_paths": get_template_paths(),
                "style_profile_paths": get_style_profile_paths()
            },
            "system": {
                "python_version": "3.12+",
                "fastapi_version": "0.104+",
                "langgraph_enabled": LANGGRAPH_AVAILABLE,
                "mcp_enabled": MCP_AVAILABLE,
                "environment": ENVIRONMENT
            }
        }
        
        # For now, consider the service healthy if core services are running
        critical_services = [
            health_data["services"]["content_graph"],
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
        logger.error("Health check failed", error=str(e), exc_info=True)
        
        error_health = {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "services": {
                "content_graph": False,
                "template_directories": False,
                "style_profile_directories": False,
                "api_server": True,
                "mcp_available": False
            }
        }
        
        return JSONResponse(
            status_code=503,
            content=error_health
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

# MCP Enhanced Generation Endpoint (if available)
if MCP_AVAILABLE:
    @app.post("/api/generate-mcp", response_model=APIResponse)
    async def generate_content_with_mcp(
        request_data: MCPGenerationRequest,
        background_tasks: BackgroundTasks,
        request: Request,
        authenticated: bool = Depends(verify_api_key)
    ):
        """Generate content with explicit MCP enhancement"""
        
        # Convert to your existing GenerateRequest format
        standard_request = GenerateRequest(
            template=request_data.template,
            style_profile=request_data.style_profile,
            dynamic_parameters=request_data.dynamic_parameters,
            priority=request_data.priority,
            timeout_seconds=request_data.timeout_seconds
        )
        
        # Call your existing endpoint with MCP enabled
        return await generate_content_endpoint(
            standard_request,
            background_tasks,
            request,
            authenticated,
            enable_mcp=request_data.enable_mcp,
            research_depth=request_data.research_depth
        )

@app.post("/api/generate", response_model=APIResponse)
async def generate_content_endpoint(
    request_data: GenerateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    authenticated: bool = Depends(verify_api_key),
    enable_mcp: bool = False,
    research_depth: str = "moderate"
):
    logger.info(f"🔍 RECEIVED REQUEST DATA: {request_data}")
    logger.info(f"🔍 REQUEST BODY TYPE: {type(request_data)}")
    
    """Start content generation with enhanced monitoring"""
    requestId = str(uuid.uuid4())
    
    try:
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
        
        # Load and validate style profile - IMPROVED LOGIC
        profiles = load_style_profiles()
        
        # Try multiple ways to find the profile
        profile = None
        search_terms = [
            request_data.style_profile,                    # exact match
            request_data.style_profile.replace('.yaml', ''), # without extension
            request_data.style_profile.replace('-', '_'),    # dash to underscore
            request_data.style_profile.replace('_', '-'),    # underscore to dash
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
            logger.error(f"Search terms tried: {search_terms}")
            raise HTTPException(
                status_code=404, 
                detail=f"Style profile not found: {request_data.style_profile}. Available profiles: {[p.id for p in profiles]}"
            )
        
        logger.info(f"✅ Found style profile: {profile.id} ({profile.name})")
        
        # Prepare configurations
        template_config = template.dict()
        template_config.update(request_data.dynamic_parameters)
        
        style_config = profile.dict()
        
        # Prepare MCP options
        mcp_options = {
            'enable_mcp': enable_mcp and getattr(app.state, 'mcp_available', False),
            'research_depth': research_depth,
            'memory_namespace': 'content_generation'
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
        
        # Start background generation
        background_tasks.add_task(
            generate_content_task,
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
    if requestId not in app.state.generation_tasks:
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
    if requestId not in app.state.generation_tasks:
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

# Status endpoint for frontend compatibility
@app.get("/status/{requestId}")
async def get_generation_status(requestId: str, request: Request):
    """Get generation status - this is the endpoint your frontend is calling"""
    try:
        print(f"🔍 Backend status check for request: {requestId}")
        
        # Check if generation task exists
        if not hasattr(app.state, 'generation_tasks') or requestId not in app.state.generation_tasks:
            print(f"❌ Request {requestId} not found in generation tasks")
            print(f"🔍 Available tasks: {list(getattr(app.state, 'generation_tasks', {}).keys())}")
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "Generation request not found",
                    "timestamp": datetime.now().isoformat(),
                    "requestId": requestId
                }
            )
        
        # Get the generation status
        status = app.state.generation_tasks[requestId]
        
        print(f"✅ Found status for {requestId}: {status.status}")
        print(f"📝 Content length: {len(status.content)} characters")
        print(f"🔍 Status object type: {type(status)}")
        
        # Format response to match frontend expectations
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
        
        print(f"🔍 Returning status: {status.status}, content_present: {bool(status.content)}")
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"❌ Error in status endpoint: {str(e)}")
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
# Debug endpoints
@app.get("/debug/profiles")
async def debug_profiles(request: Request):
    """Debug endpoint to check style profile loading"""
    try:
        profiles = load_style_profiles()
        template_paths = get_template_paths()
        style_paths = get_style_profile_paths()
        
        return APIResponse(
            success=True,
            data={
                "current_working_directory": os.getcwd(),
                "template_paths_checked": [
                    {"path": path, "exists": os.path.exists(path)} 
                    for path in ["data/content_templates", "../data/content_templates", "frontend/content-templates", "../frontend/content-templates"]
                ],
                "style_paths_checked": [
                    {"path": path, "exists": os.path.exists(path)} 
                    for path in ["data/style_profiles", "../data/style_profiles", "frontend/style-profiles", "../frontend/style-profiles", "style_profiles", "style-profiles"]
                ],
                "template_paths_found": template_paths,
                "style_paths_found": style_paths,
                "profiles_loaded": [{"id": p.id, "name": p.name, "filename": p.filename} for p in profiles],
                "profile_count": len(profiles),
                "mcp_available": getattr(app.state, 'mcp_available', False),
                "environment": ENVIRONMENT
            },
            requestId=request.state.requestId
        )
    except Exception as e:
        logger.error("Debug profiles failed", error=str(e))
        return APIResponse(
            success=False,
            error={"message": str(e)},
            requestId=request.state.requestId
        )

@app.get("/debug/template-parsing")
async def debug_template_parsing(request: Request):
    """Debug how templates are being parsed"""
    try:
        debug_info = {
            "template_directories": get_template_paths(),
            "parsing_results": []
        }
        
        for template_dir in get_template_paths():
            if os.path.exists(template_dir):
                for filename in os.listdir(template_dir):
                    if filename.endswith('.yaml'):
                        file_path = os.path.join(template_dir, filename)
                        try:
                            template_data = load_yaml_file_safe(file_path)
                            parameters_data = template_data.get("parameters", {})
                            
                            # Test the parameter parsing
                            try:
                                processed_params = parse_template_parameters(parameters_data)
                                param_status = "success"
                                param_count = len(processed_params)
                                param_error = None
                            except Exception as e:
                                param_status = "failed"
                                param_count = 0
                                param_error = str(e)
                            
                            debug_info["parsing_results"].append({
                                "filename": filename,
                                "template_id": template_data.get('id', 'not_specified'),
                                "parameters_type": type(parameters_data).__name__,
                                "parameters_raw_count": len(parameters_data) if hasattr(parameters_data, '__len__') else 0,
                                "parameter_parsing_status": param_status,
                                "parameters_processed_count": param_count,
                                "parameter_error": param_error,
                                "first_few_keys": list(template_data.keys())[:5],
                                "parameters_sample": str(parameters_data)[:200] + "..." if len(str(parameters_data)) > 200 else str(parameters_data)
                            })
                            
                        except Exception as e:
                            debug_info["parsing_results"].append({
                                "filename": filename,
                                "status": "file_load_failed",
                                "error": str(e)
                            })
        
        return APIResponse(
            success=True,
            data=debug_info,
            requestId=request.state.requestId
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            error={"message": str(e)},
            requestId=request.state.requestId
        )

@app.get("/debug/file-structures")
async def debug_file_structures(request: Request):
    """Debug endpoint to show how files are being parsed"""
    try:
        debug_info = {
            "templates": [],
            "style_profiles": [],
            "parsing_results": {
                "templates_loaded": 0,
                "profiles_loaded": 0,
                "templates_failed": 0,
                "profiles_failed": 0
            }
        }
        
        # Debug templates
        for template_dir in get_template_paths():
            if os.path.exists(template_dir):
                for filename in os.listdir(template_dir):
                    if filename.endswith('.yaml'):
                        file_path = os.path.join(template_dir, filename)
                        try:
                            template_data = load_yaml_file_safe(file_path)
                            parameters_data = template_data.get("parameters", {})
                            
                            debug_info["templates"].append({
                                "filename": filename,
                                "id": template_data.get('id', 'not_specified'),
                                "name": template_data.get('name', 'not_specified'),
                                "parameters_type": type(parameters_data).__name__,
                                "parameters_count": len(parameters_data) if hasattr(parameters_data, '__len__') else 0,
                                "has_system_prompt": bool(template_data.get('system_prompt')),
                                "has_structure": bool(template_data.get('structure')),
                                "status": "parsed_successfully"
                            })
                            debug_info["parsing_results"]["templates_loaded"] += 1
                            
                        except Exception as e:
                            debug_info["templates"].append({
                                "filename": filename,
                                "status": "parse_failed",
                                "error": str(e)
                            })
                            debug_info["parsing_results"]["templates_failed"] += 1
        
        # Debug style profiles
        for profile_dir in get_style_profile_paths():
            if os.path.exists(profile_dir):
                for filename in os.listdir(profile_dir):
                    if filename.endswith('.yaml'):
                        file_path = os.path.join(profile_dir, filename)
                        try:
                            profile_data = load_yaml_file_safe(file_path)
                            
                            debug_info["style_profiles"].append({
                                "filename": filename,
                                "id": profile_data.get('id', 'not_specified'),
                                "name": profile_data.get('name', 'not_specified'),
                                "has_system_prompt": bool(profile_data.get('system_prompt')),
                                "has_length_limit": bool(profile_data.get('length_limit')),
                                "has_settings": bool(profile_data.get('settings')),
                                "status": "parsed_successfully"
                            })
                            debug_info["parsing_results"]["profiles_loaded"] += 1
                            
                        except Exception as e:
                            debug_info["style_profiles"].append({
                                "filename": filename,
                                "status": "parse_failed",
                                "error": str(e)
                            })
                            debug_info["parsing_results"]["profiles_failed"] += 1
        
        return APIResponse(
            success=True,
            data=debug_info,
            requestId=request.state.requestId
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            error={"message": str(e)},
            requestId=request.state.requestId
        )

@app.get("/debug/mcp-status")
async def debug_mcp_status(request: Request):
    """Debug MCP integration status"""
    return APIResponse(
        success=True,
        data={
            "mcp_modules_available": MCP_AVAILABLE,
            "mcp_runtime_available": getattr(app.state, 'mcp_available', False),
            "environment": ENVIRONMENT,
            "api_key_configured": bool(API_KEY and API_KEY != "prod_api_key_2025_secure_content_gen_v1"),
            "auth_required": ENVIRONMENT == "production"
        },
        requestId=request.state.requestId
    )

if __name__ == "__main__":
    print("🚀 Starting Agentic Writer API Server")
    print(f"📊 LangGraph Available: {LANGGRAPH_AVAILABLE}")
    print(f"🔧 MCP Available: {MCP_AVAILABLE}")
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
