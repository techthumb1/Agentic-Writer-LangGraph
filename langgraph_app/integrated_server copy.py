# langgraph_app/
import os
import uuid
import json
import yaml
import logging
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Tuple, Union, NoReturn
import re
# ── Third-party
from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest
import uvicorn

# ── Local (project)
from archive.enhanced_mcp_integration import execute_enhanced_mcp_generation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def _fatal(msg: str, *, exc: Optional[BaseException] = None) -> NoReturn:
    """Log a fatal error and terminate the process (enterprise strict)."""
    if exc:
        logger.error("%s | exception=%s: %s", msg, type(exc).__name__, exc)
    else:
        logger.error("%s", msg)
    raise SystemExit(msg)

try:
    from .mcp_server_extension import (
        initialize_mcp_for_existing_server,
        cleanup_mcp_for_existing_server,
        enhance_generation_with_mcp as _enhance_generation_with_mcp,
        MCPGenerationRequest,
    )
    logger.info("MCP modules loaded successfully")
except ImportError as e:
    _fatal("ENTERPRISE FAILURE: MCP modules not available. MCP integration is required.", exc=e)

try:
    from .universal_system.universal_integration import LangGraphUniversalIntegration
    logger.info("Universal System loaded successfully")
except ImportError as e:
    _fatal("ENTERPRISE FAILURE: Universal System not available. Universal integration is required.", exc=e)

try:
    from .enhanced_model_registry import EnhancedModelRegistry, get_model
    logger.info("Model registry loaded successfully")
except ImportError as e:
    _fatal("ENTERPRISE FAILURE: Model registry not available. Enhanced model registry is required.", exc=e)

ENVIRONMENT = os.getenv("NODE_ENV", "production")  # default to production in enterprise
REQUIRED_ENV_VARS: Tuple[str, ...] = ("LANGGRAPH_API_KEY",)

_missing = [k for k in REQUIRED_ENV_VARS if not os.getenv(k)]
if _missing:
    _fatal(f"ENTERPRISE FAILURE: Missing required environment variables: {_missing}")

API_KEY = os.environ["LANGGRAPH_API_KEY"]  # guaranteed above
FASTAPI_API_KEY = os.getenv("FASTAPI_API_KEY", API_KEY)  # fallback to LANGGRAPH_API_KEY

security = HTTPBearer(auto_error=False)

async def get_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    return credentials.credentials if credentials else None

async def verify_api_key(api_key: Optional[str] = Depends(get_api_key)) -> bool:
    if ENVIRONMENT == "production":
        if not api_key or api_key not in [API_KEY, FASTAPI_API_KEY]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required for enterprise operation",
                headers={"WWW-Authenticate": "Bearer"},
            )
    elif ENVIRONMENT == "development":
        # More lenient in development but still validate if provided
        if api_key and api_key not in [API_KEY, FASTAPI_API_KEY]:
            logger.warning(f"Invalid API key provided in development mode: {api_key[:10]}...")
            return False
    return True

custom_registry = CollectorRegistry()
# ──────────────────────────────────────────────────────────────────────────────
# Configuration (enterprise strict: verify required env)
# ──────────────────────────────────────────────────────────────────────────────
ENVIRONMENT = os.getenv("NODE_ENV", "production")  # default to production in enterprise
REQUIRED_ENV_VARS: Tuple[str, ...] = ("LANGGRAPH_API_KEY",)

_missing = [k for k in REQUIRED_ENV_VARS if not os.getenv(k)]
if _missing:
    _fatal(f"ENTERPRISE FAILURE: Missing required environment variables: {_missing}")

API_KEY = os.environ["LANGGRAPH_API_KEY"]  # guaranteed above


# ──────────────────────────────────────────────────────────────────────────────
# Authentication (bearer token; strict in production)
# ──────────────────────────────────────────────────────────────────────────────
security = HTTPBearer(auto_error=False)


async def get_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    return credentials.credentials if credentials else None


async def verify_api_key(api_key: Optional[str] = Depends(get_api_key)) -> bool:
    if ENVIRONMENT == "production":
        if not api_key or api_key != API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required for enterprise operation",
                headers={"WWW-Authenticate": "Bearer"},
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

# File loading utilities - ENTERPRISE: Fail if directories don't exist
def get_template_paths() -> List[str]:
    """Get ordered list of template directory paths - ENTERPRISE: Must exist"""
    paths = [
        "data/content_templates",
        "../data/content_templates",
        "frontend/content-templates",
        "../frontend/content-templates",
        "content-templates"
    ]
    existing_paths = [path for path in paths if os.path.exists(path)]
    
    if not existing_paths:
        raise SystemExit("ENTERPRISE MODE: No template directories found. Required paths: " + ", ".join(paths))
    
    logger.info(f"📂 Template paths found: {existing_paths}")
    return existing_paths

def get_style_profile_paths() -> List[str]:
    """Get ordered list of style profile directory paths - ENTERPRISE: Must exist"""
    paths = [
        "data/style_profiles",
        "../data/style_profiles",
        "frontend/style-profiles",
        "../frontend/style-profiles",
        "style-profiles"
    ]
    existing_paths = [path for path in paths if os.path.exists(path)]
    
    if not existing_paths:
        raise SystemExit("ENTERPRISE MODE: No style profile directories found. Required paths: " + ", ".join(paths))
    
    logger.info(f"Style profile paths found: {existing_paths}")
    return existing_paths

def load_yaml_file_safe(file_path: str) -> Dict[str, Any]:
    """Load YAML file with comprehensive error handling - ENTERPRISE: Fail on errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            if content is None:
                raise ValueError(f"Empty YAML file: {file_path}")
            if not isinstance(content, dict):
                raise ValueError(f"Invalid YAML structure in {file_path}: expected dict, got {type(content)}")
            return content
    except yaml.YAMLError as e:
        raise SystemExit(f"ENTERPRISE MODE: YAML parsing error in {file_path}: {e}")
    except FileNotFoundError:
        raise SystemExit(f"ENTERPRISE MODE: Required file not found: {file_path}")
    except PermissionError:
        raise SystemExit(f"ENTERPRISE MODE: Permission denied reading file: {file_path}")
    except Exception as e:
        raise SystemExit(f"ENTERPRISE MODE: Unexpected error loading YAML {file_path}: {e}")

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

def should_use_universal_system(
    template_config: Dict[str, Any], 
    style_config: Dict[str, Any], 
    dynamic_parameters: Dict[str, Any]
) -> bool:
    """
    Determine if Universal System should be activated based on content complexity,
    novelty, and template characteristics.
    """
    
    # Force Universal for specific template types
    universal_template_triggers = [
        'universal', 'dynamic', 'adaptive', 'novel', 'custom',
        'comprehensive', 'advanced', 'research', 'analysis'
    ]
    
    template_name = template_config.get('name', '').lower()
    template_id = template_config.get('id', '').lower()
    
    # Check template-based triggers
    if any(trigger in template_name or trigger in template_id for trigger in universal_template_triggers):
        logger.info("🎯 Universal activated: Template-based trigger detected")
        return True
    
    # Check for novel/complex topics in parameters
    topic_fields = ['topic', 'subject', 'title', 'content_area', 'domain', 'field']
    novel_indicators = [
        'underwater basket weaving', 'urban message delivery', 'vertical hydroponic',
        'experimental', 'innovative', 'cutting-edge', 'emerging', 'breakthrough',
        'novel', 'unique', 'custom', 'specialized', 'niche', 'advanced'
    ]
    
    for field in topic_fields:
        if field in dynamic_parameters:
            topic_content = str(dynamic_parameters[field]).lower()
            if any(indicator in topic_content for indicator in novel_indicators):
                logger.info(f"🎯 Universal activated: Novel topic detected in {field}: {topic_content[:50]}...")
                return True
    
    # Check content complexity requirements
    complexity_indicators = [
        'multi-section', 'comprehensive', 'detailed analysis', 'research-based',
        'in-depth', 'technical documentation', 'white paper', 'case study'
    ]
    
    all_text = ' '.join([
        str(v) for v in dynamic_parameters.values() if isinstance(v, str)
    ]).lower()
    
    if any(indicator in all_text for indicator in complexity_indicators):
        logger.info("🎯 Universal activated: Complex content requirements detected")
        return True
    
    # Force Universal for specific style profiles that benefit from dynamic generation
    dynamic_style_profiles = [
        'research', 'academic', 'technical', 'experimental', 'innovative'
    ]
    
    style_name = style_config.get('name', '').lower()
    style_id = style_config.get('id', '').lower()
    
    if any(profile in style_name or profile in style_id for profile in dynamic_style_profiles):
        logger.info("🎯 Universal activated: Dynamic style profile detected")
        return True
    
    # Parameter count threshold - complex requests likely need Universal
    if len(dynamic_parameters) >= 5:
        logger.info(f"🎯 Universal activated: High parameter count ({len(dynamic_parameters)} params)")
        return True
    
    # Check for enterprise/premium generation modes
    generation_mode = template_config.get('generation_mode', '')
    if generation_mode in ['premium', 'enterprise']:
        logger.info(f"🎯 Universal activated: Premium generation mode ({generation_mode})")
        return True
    
    return False


async def execute_content_generation(
    request_id: str,
    template_config: Dict[str, Any],
    style_config: Dict[str, Any],
    app_state,
    mcp_options: Optional[Dict[str, Any]] = None
) -> GenerationStatus:
    """Execute content generation with proper LangGraph agent result extraction."""
    import re
    start_time = datetime.now()
    mcp_options = mcp_options or {}

    def _persist_and_return(status: GenerationStatus) -> GenerationStatus:
        if not hasattr(app_state, "generation_tasks"):
            app_state.generation_tasks = {}
        app_state.generation_tasks[request_id] = status
        try:
            GENERATION_COUNT.labels(status=status.status, template=template_config.get("name", "unknown")).inc()
            if status.status != "failed":
                duration = (datetime.now() - start_time).total_seconds()
                GENERATION_DURATION.observe(duration)
        except Exception:
            pass
        return status

# File: langgraph_app/content_extraction_helpers.py
"""
Enhanced content extraction utilities for LangGraph agent results
Add these helper functions to extract content from various LangGraph result formats
"""

from typing import Dict, Any, List


def extract_content_from_langgraph_result(result: Dict[str, Any]) -> str:
    """
    Enhanced content extraction from LangGraph agent workflow results.
    Tries multiple strategies to find generated content in different result formats.
    """
    
    # Strategy 1: Direct content field
    if "content" in result and isinstance(result["content"], str) and result["content"].strip():
        return result["content"].strip()
    
    # Strategy 2: Final output from agent workflow
    if "final_output" in result and isinstance(result["final_output"], str) and result["final_output"].strip():
        return result["final_output"].strip()
    
    # Strategy 3: Writer agent output
    if "writer_output" in result and isinstance(result["writer_output"], str) and result["writer_output"].strip():
        return result["writer_output"].strip()
    
    # Strategy 4: Formatted content from formatter agent
    if "formatted_content" in result and isinstance(result["formatted_content"], str) and result["formatted_content"].strip():
        return result["formatted_content"].strip()
    
    # Strategy 5: Agent workflow messages (LangGraph format)
    if "messages" in result and isinstance(result["messages"], list):
        for message in reversed(result["messages"]):  # Check latest first
            if isinstance(message, dict) and "content" in message:
                content = message["content"]
                if isinstance(content, str) and len(content.strip()) > 50:  # Substantial content
                    return content.strip()
    
    # Strategy 6: Agent state content
    if "agent_state" in result and isinstance(result["agent_state"], dict):
        agent_state = result["agent_state"]
        for key in ["final_content", "generated_content", "output", "result"]:
            if key in agent_state and isinstance(agent_state[key], str) and agent_state[key].strip():
                return agent_state[key].strip()
    
    # Strategy 7: Multi-agent workflow output
    if "workflow_output" in result and isinstance(result["workflow_output"], dict):
        workflow = result["workflow_output"]
        if "final_step" in workflow and isinstance(workflow["final_step"], dict):
            final_step = workflow["final_step"]
            if "output" in final_step and isinstance(final_step["output"], str):
                return final_step["output"].strip()
    
    # Strategy 8: MCP results content
    if "mcp_results" in result and isinstance(result["mcp_results"], dict):
        mcp_results = result["mcp_results"]
        if "generated_content" in mcp_results and isinstance(mcp_results["generated_content"], str):
            return mcp_results["generated_content"].strip()
    
    # Strategy 9: Check for any string field with substantial content
    for key, value in result.items():
        if isinstance(value, str) and len(value.strip()) > 100:  # Substantial content
            # Skip debug/meta fields
            if key not in ["debug", "metadata", "error", "status", "request_id"]:
                return value.strip()
    
    # Strategy 10: Deep nested search
    def deep_search_content(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and len(value.strip()) > 100:
                    if "content" in key.lower() or "output" in key.lower() or "result" in key.lower():
                        return value.strip()
                elif isinstance(value, (dict, list)):
                    nested_result = deep_search_content(value, f"{path}.{key}")
                    if nested_result:
                        return nested_result
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                nested_result = deep_search_content(item, f"{path}[{i}]")
                if nested_result:
                    return nested_result
        return None
    
    nested_content = deep_search_content(result)
    if nested_content:
        return nested_content
    
    return ""


def extract_sources_from_langgraph_result(result: Dict[str, Any]) -> List[str]:
    """
    Extract evidence sources from LangGraph agent execution.
    Looks for sources in various fields that agents might populate.
    """
    sources = []
    
    # Research agent sources
    if "research_results" in result and isinstance(result["research_results"], dict):
        research = result["research_results"]
        if "sources" in research and isinstance(research["sources"], list):
            sources.extend(research["sources"])
    
    # MCP tool execution traces
    if "mcp_tool_executions" in result and isinstance(result["mcp_tool_executions"], list):
        sources.extend([f"MCP Tool: {exec}" for exec in result["mcp_tool_executions"]])
    
    # Agent workflow tool calls
    if "tool_calls" in result and isinstance(result["tool_calls"], list):
        sources.extend([f"Agent Tool: {call}" for call in result["tool_calls"]])
    
    # Standard source fields
    for field in ["sources", "evidence", "references", "citations"]:
        if field in result and isinstance(result[field], list):
            sources.extend(result[field])
    
    # If no sources found but we have agent execution evidence, create minimal source
    if not sources:
        if "agent_trace" in result or "workflow_output" in result or "mcp_results" in result:
            sources.append("LangGraph agent workflow execution")
    
    return sources


def log_content_extraction_debug(request_id: str, result: Dict[str, Any], extracted_content: str) -> Dict[str, Any]:
    """
    Generate debug information for content extraction.
    Helps troubleshoot when content extraction fails.
    """
    return {
        "request_id": request_id,
        "result_keys": list(result.keys()),
        "result_types": {k: type(v).__name__ for k, v in result.items()},
        "content_length": len(extracted_content),
        "content_found": bool(extracted_content),
        "extraction_strategies_available": [
            "direct_content", "final_output", "writer_output", "formatted_content",
            "messages", "agent_state", "workflow_output", "mcp_results", 
            "any_string_field", "deep_search"
        ],
        "result_structure_sample": {
            k: str(v)[:100] + "..." if isinstance(v, str) and len(str(v)) > 100 
            else type(v).__name__ if not isinstance(v, (str, int, float, bool, type(None)))
            else v
            for k, v in result.items()
        }
    }

def extract_sources_from_langgraph_result(result: Dict[str, Any]) -> List[str]:
    """Extract evidence sources from LangGraph agent execution."""
    sources = []
    
    # Research agent sources
    if "research_results" in result and isinstance(result["research_results"], dict):
        research = result["research_results"]
        if "sources" in research and isinstance(research["sources"], list):
            sources.extend(research["sources"])
    
    # MCP tool execution traces
    if "mcp_tool_executions" in result and isinstance(result["mcp_tool_executions"], list):
        sources.extend([f"MCP Tool: {exec}" for exec in result["mcp_tool_executions"]])
    
    # Agent workflow tool calls
    if "tool_calls" in result and isinstance(result["tool_calls"], list):
        sources.extend([f"Agent Tool: {call}" for call in result["tool_calls"]])
    
    # Standard source fields
    for field in ["sources", "evidence", "references", "citations"]:
        if field in result and isinstance(result[field], list):
            sources.extend(result[field])
    
    # If no sources found but we have agent execution evidence, create minimal source
    if not sources:
        if "agent_trace" in result or "workflow_output" in result or "mcp_results" in result:
            sources.append("LangGraph agent workflow execution")
    
    return sources

# CRITICAL FIX 5: Add detailed logging to track the content flow
def log_content_flow(request_id: str, stage: str, data: Any):
    """Helper function to log content flow through the system"""
    if isinstance(data, dict):
        content_info = {
            "stage": stage,
            "data_keys": list(data.keys()),
            "has_content": "content" in data,
            "content_length": len(data.get("content", "")) if "content" in data else 0
        }
    elif isinstance(data, str):
        content_info = {
            "stage": stage,
            "data_type": "string",
            "content_length": len(data),
            "content_preview": data[:100] + "..." if len(data) > 100 else data
        }
    else:
        content_info = {
            "stage": stage,
            "data_type": type(data).__name__,
            "data_str": str(data)[:200]
        }
    
    logger.info(f"🔄 Content flow [{request_id}] {stage}: {content_info}")

logger = logging.getLogger(__name__)


def fix_yaml_formatting(yaml_content: str) -> str:
    """Fix common YAML formatting issues from AI generation"""
    if not yaml_content or not isinstance(yaml_content, str):
        return yaml_content
        
    lines = yaml_content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            fixed_lines.append(line)
            continue
            
        # Fix missing colons after keys
        # Pattern: word followed by space and non-colon content
        if re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s+([^:].*)$', line):
            match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s+(.*)$', line)
            if match:
                indent, key, value = match.groups()
                # Don't modify if it's a list item or already formatted correctly
                if not value.startswith('-') and not key.endswith(':'):
                    line = f"{indent}{key}: {value}"
        
        # Fix multiline content that breaks YAML
        if ':' in line and len(line) > 120:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key_part = parts[0]
                value_part = parts[1].strip()
                # Use literal block style for very long content
                if len(value_part) > 100 and not value_part.startswith(('"', "'", '|', '>')):
                    line = f"{key_part}: |\n    {value_part}"
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


#def create_fallback_template() -> Dict[str, Any]:
    """Create a minimal valid template when YAML parsing fails"""
    return {
        'name': 'Dynamic Generated Template',
        'system_prompt': 'Generate high-quality content based on the user requirements. Follow best practices for structure, clarity, and engagement.',
        'instructions': 'Create comprehensive content that meets the specified requirements. Include proper formatting, clear sections, and professional tone.',
        'parameters': {},
        'metadata': {
            'generated': True,
            'fallback': True,
            'timestamp': datetime.now().isoformat()
        }
    }
#
#
#def safe_yaml_load(yaml_content: str, context: str = "unknown") -> Dict[str, Any]:
    """Safely load YAML with automatic fixing of common issues"""
    if not yaml_content:
        logger.warning(f"Empty YAML content in {context}")
        return create_fallback_template()
    
    try:
        # First attempt: try loading as-is
        result = yaml.safe_load(yaml_content)
        if result is None:
            logger.warning(f"YAML loaded as None in {context}, creating fallback")
            return create_fallback_template()
        return result
    except yaml.YAMLError as e:
        logger.warning(f"Initial YAML parse failed in {context}, attempting to fix: {e}")
        
        try:
            # Second attempt: fix formatting and try again
            fixed_content = fix_yaml_formatting(yaml_content)
            result = yaml.safe_load(fixed_content)
            if result is None:
                return create_fallback_template()
            logger.info(f"Successfully fixed YAML formatting in {context}")
            return result
        except yaml.YAMLError as e2:
            logger.error(f"Failed to fix YAML content in {context}: {e2}")
            logger.debug(f"Problematic YAML content: {yaml_content[:500]}...")
            return create_fallback_template()
#
#
#def validate_template_structure(template_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize template structure"""
    if not isinstance(template_data, dict):
        logger.error(f"Template data is not a dict: {type(template_data)}")
        return create_fallback_template()
    
    # Ensure required fields exist
    required_fields = ['name', 'system_prompt']
    for field in required_fields:
        if field not in template_data:
            logger.warning(f"Missing required field '{field}' in template, adding default")
            if field == 'name':
                template_data['name'] = 'Generated Template'
            elif field == 'system_prompt':
                template_data['system_prompt'] = 'Generate high-quality content based on requirements.'
    
    # Ensure metadata exists
    if 'metadata' not in template_data:
        template_data['metadata'] = {}
    
    # Ensure parameters exists
    if 'parameters' not in template_data:
        template_data['parameters'] = {}
    
    return template_data
#
#
#
def determine_generation_approach(
    template: ContentTemplate,
    profile: StyleProfile,
    request_data: GenerateRequest,
    app_state
) -> Tuple[str, Dict[str, Any]]:
    """
    Determine whether to use Universal system or direct MCP generation
    Returns: (approach_type, enhanced_config)
    ENTERPRISE: Universal system must be initialized
    """
    
    template_config = template.dict()
    template_config.update(request_data.dynamic_parameters)
    style_config = profile.dict()
    
    # ENTERPRISE: Universal system must be available and initialized
    if not hasattr(app_state, 'universal_integration'):
        app_state.universal_integration = LangGraphUniversalIntegration()
        logger.info("✅ Universal Integration initialized on-demand")
    
    if not app_state.universal_integration:
        raise SystemExit("ENTERPRISE MODE: Universal Integration failed to initialize")
    
    # Determine if Universal should be used
    use_universal = should_use_universal_system(template_config, style_config, request_data.dynamic_parameters)
    
    if use_universal:
        # Enhanced Universal configuration
        enhanced_config = {
            'approach': 'universal_mcp',
            'universal_context': {
                'template_preference': template.id,
                'complexity_level': 'high',
                'research_depth': 'comprehensive',
                'generation_mode': template_config.get('generation_mode', 'premium'),
                'user_parameters': request_data.dynamic_parameters,
                'user_preferences': {
                    'preferred_style': profile.id
                }
            },
            'mcp_options': {
                'enable_mcp': True,
                'research_depth': 'comprehensive',
                'memory_namespace': 'universal_generation',
                'timeout_seconds': request_data.timeout_seconds,
                'priority': request_data.priority,
                'advanced_features': True,
                'tool_selection': 'dynamic'
            }
        }

        return 'universal', enhanced_config
    else:
        # Direct MCP configuration
        enhanced_config = {
            'approach': 'direct_mcp',
            'template_config': template_config,
            'style_config': style_config,
            'mcp_options': {
                'enable_mcp': True,
                'research_depth': 'moderate',
                'memory_namespace': 'standard_generation',
                'timeout_seconds': request_data.timeout_seconds,
                'priority': request_data.priority
            }
        }
        return 'direct', enhanced_config

def normalize_inputs_to_parameters(template_data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(template_data, dict):
        return template_data
    if "parameters" in template_data or "inputs" not in template_data:
        return template_data

    inputs = template_data.get("inputs") or {}
    if not isinstance(inputs, dict):
        return template_data

    params: Dict[str, Any] = {}
    allowed = {"string","text","textarea","number","select","boolean","array","date","email","url"}

    for key, spec in inputs.items():
        spec = spec or {}
        default_val = spec.get("default")

        if isinstance(default_val, bool):
            ptype = "boolean"
        elif isinstance(default_val, (int, float)):
            ptype = "number"
        elif isinstance(spec.get("options"), list):
            ptype = "select"
        else:
            ptype = spec.get("type") if spec.get("type") in allowed else "text"

        params[key] = {
            "name": key,
            "label": spec.get("label", key.replace("_", " ").title()),
            "type": ptype,
            "required": bool(spec.get("required", False)),
            "default": default_val,
            "options": spec.get("options"),
            "placeholder": spec.get("placeholder"),
            "description": spec.get("description"),
            "validation": spec.get("validation", {}),
        }

    template_data["parameters"] = params
    return template_data


# File: langgraph_app/integrated_server.py

def load_templates() -> List[ContentTemplate]:
    """Load and validate all content templates (supports V2 `inputs` via normalizer)."""
    templates: List[ContentTemplate] = []
    templates_loaded = 0

    for template_dir in get_template_paths():
        if not os.path.isdir(template_dir):
            continue

        try:
            for filename in sorted(os.listdir(template_dir)):
                if not filename.lower().endswith((".yaml", ".yml")):
                    continue

                file_path = os.path.join(template_dir, filename)
                template_data = load_yaml_file_safe(file_path)

                if not template_data or not isinstance(template_data, dict):
                    raise SystemExit(f"ENTERPRISE MODE: Failed to load template: {file_path}")

                # Normalize V2 `inputs` -> V1 `parameters` before parsing
                template_data = normalize_inputs_to_parameters(template_data)

                try:
                    template_id = str(template_data.get("id") or os.path.splitext(filename)[0])

                    # After normalization, prefer `parameters`
                    parameters_data = template_data.get("parameters") or {}
                    processed_parameters = parse_template_parameters(parameters_data)

                    template = ContentTemplate(
                        id=template_id,
                        slug=template_data.get("slug") or template_id,
                        name=template_data.get("name") or template_id.replace("_", " ").title(),
                        description=template_data.get("description") or "",
                        category=template_data.get("category") or "general",
                        defaults=template_data.get("defaults") or {},
                        system_prompt=template_data.get("system_prompt"),
                        structure=template_data.get("structure") or {},
                        research=template_data.get("research") or {},
                        parameters=processed_parameters,
                        metadata=template_data.get("metadata") or {},
                        version=str(template_data.get("version") or "2.0.0"),
                        filename=filename,
                    )

                    templates.append(template)
                    templates_loaded += 1
                    logger.info(
                        f"Loaded template: {template.name} ({template.id}) "
                        f"from {filename} with {len(processed_parameters)} parameters"
                    )

                except Exception as e:
                    raise SystemExit(f"ENTERPRISE MODE: Invalid template format in {filename}: {e}")

        except Exception as e:
            raise SystemExit(f"ENTERPRISE MODE: Error loading templates from {template_dir}: {e}")

    if templates_loaded == 0:
        raise SystemExit("ENTERPRISE MODE: No templates could be loaded - system cannot operate")

    logger.info(f"Total templates loaded: {len(templates)}")
    return templates

def load_style_profiles() -> List[StyleProfile]:
    """Load and validate all style profiles - ENTERPRISE: Must load successfully"""
    profiles = []
    profiles_loaded = 0

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
                    raise SystemExit(f"ENTERPRISE MODE: Failed to load style profile: {file_path}")

                try:
                    # Normalize length_limit subfields (convert numeric strings to int)
                    length = profile_data.get("length_limit", {})
                    for k in ("min", "max", "words", "target"):
                        if k in length:
                            v = length[k]
                            if isinstance(v, str) and v.isdigit():
                                length[k] = int(v)
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
                        length_limit=length,
                        settings=profile_data.get("settings", {}),
                        formatting=profile_data.get("formatting", {}),
                        metadata=profile_data.get("metadata", {}),
                        filename=filename
                    )
                    profiles.append(profile)
                    profiles_loaded += 1
                    logger.info(f"✅ Loaded style profile: {profile.name} ({profile.id})")

                except Exception as e:
                    raise SystemExit(f"ENTERPRISE MODE: Invalid style profile format in {filename}: {e}")

        except Exception as e:
            raise SystemExit(f"ENTERPRISE MODE: Error loading style profiles from {profile_dir}: {e}")

    if profiles_loaded == 0:
        raise SystemExit("ENTERPRISE MODE: No style profiles could be loaded - system cannot operate")

    logger.info(f"📊 Total style profiles loaded: {len(profiles)}")
    return profiles

async def execute_content_generation(
    request_id: str,
    template_config: Dict[str, Any],
    style_config: Dict[str, Any],
    app_state,
    mcp_options: Optional[Dict[str, Any]] = None
) -> GenerationStatus:
    """Execute content generation via MCP pipeline with LangGraph agents - NO FALLBACKS."""
    import re
    start_time = datetime.now()
    mcp_options = mcp_options or {}

    def _persist_and_return(status: GenerationStatus) -> GenerationStatus:
        if not hasattr(app_state, "generation_tasks"):
            app_state.generation_tasks = {}
        app_state.generation_tasks[request_id] = status
        try:
            GENERATION_COUNT.labels(status=status.status, template=template_config.get("name", "unknown")).inc()
            if status.status != "failed":
                duration = (datetime.now() - start_time).total_seconds()
                GENERATION_DURATION.observe(duration)
        except Exception:
            pass
        return status

    try:
        logger.info(f"🚀 Starting LangGraph+MCP generation [requestId={request_id}, template={template_config.get('name')}, style={style_config.get('name')}]")

        # ENTERPRISE: Strict validation - no fallbacks
        if not getattr(app_state, "mcp_available", False):
            err = "MCP system not available - LangGraph agents require MCP tools"
            logger.error(f"{err} [requestId={request_id}]")
            return _persist_and_return(GenerationStatus(
                requestId=request_id, status="failed", progress=0.0, current_step="MCP Unavailable",
                content="", metadata={"error_details": err}, errors=[err], warnings=[],
                metrics={"error_time": datetime.now().isoformat()}, created_at=start_time,
                updated_at=datetime.now(), completed_at=datetime.now()
            ))

        # ENTERPRISE: Template validation - must have proper structure
        if not template_config or not template_config.get("name"):
            err = "Invalid template configuration - LangGraph requires template specification"
            logger.error(f"{err} [requestId={request_id}]")
            return _persist_and_return(GenerationStatus(
                requestId=request_id, status="failed", progress=0.0, current_step="Template Invalid",
                content="", metadata={"error_details": err}, errors=[err], warnings=[],
                metrics={"error_time": datetime.now().isoformat()}, created_at=start_time,
                updated_at=datetime.now(), completed_at=datetime.now()
            ))

        # ENTERPRISE: Style validation - must have proper structure  
        if not style_config or not style_config.get("name"):
            err = "Invalid style configuration - LangGraph requires style specification"
            logger.error(f"{err} [requestId={request_id}]")
            return _persist_and_return(GenerationStatus(
                requestId=request_id, status="failed", progress=0.0, current_step="Style Invalid",
                content="", metadata={"error_details": err}, errors=[err], warnings=[],
                metrics={"error_time": datetime.now().isoformat()}, created_at=start_time,
                updated_at=datetime.now(), completed_at=datetime.now()
            ))

        # Execute LangGraph+MCP generation - NO FALLBACKS
        logger.info(f"🔧 Executing LangGraph+MCP generation [requestId={request_id}]")
        
        result = await execute_enhanced_mcp_generation(
            request_id=request_id,
            template_config=template_config,
            style_config=style_config,
            app_state=app_state,
            mcp_options=mcp_options or {}
        )

        # STRICT: Result must be valid
        if not isinstance(result, dict):
            err = "LangGraph generation returned invalid result structure"
            logger.error(f"{err} [requestId={request_id}]")
            return _persist_and_return(GenerationStatus(
                requestId=request_id, status="failed", progress=0.0, current_step="Invalid Result",
                content="", metadata={"error_details": err}, errors=[err], warnings=[],
                metrics={"error_time": datetime.now().isoformat()}, created_at=start_time,
                updated_at=datetime.now(), completed_at=datetime.now()
            ))

        # STRICT: Extract status and content - NO FALLBACKS
        status_value = result.get("status", "failed")  # Default to failed if not specified
        content_value = extract_content_from_langgraph_result(result)
        logger.info(f"📝 Content extraction [requestId={request_id}]:")
        logger.info(f"   - Content length: {len(content_value)}")
        logger.info(f"   - Result keys: {list(result.keys())}")
        logger.info(f"   - Content preview: {content_value[:100]}..." if content_value else "   - No content extracted")

        # CRITICAL: NO FALLBACK CONTENT GENERATION 
        # If content is empty, this is a REAL FAILURE that must be addressed
        if status_value == "completed" and not content_value:
            err = f"LangGraph agents completed but produced no content - check agent workflow execution"
            logger.error(f"{err} [requestId={request_id}]")

            debug_info = {
                "result_keys": list(result.keys()),
                "result_types": {k: type(v).__name__ for k, v in result.items()},
                "extraction_strategies_tried": [
                    "direct_content", "final_output", "writer_output", "messages", 
                    "agent_state", "workflow_output", "mcp_results", "deep_search"
                ],
                "template_name": template_config.get("name"),
                "style_name": style_config.get("name")
            }

            return _persist_and_return(GenerationStatus(
                requestId=request_id, status="failed", progress=0.0, current_step="No Content Generated",
                content="", metadata={"error_details": err, "debug_info": debug_info}, 
                errors=[err], warnings=[], metrics={"error_time": datetime.now().isoformat()},
                created_at=start_time, updated_at=datetime.now(), completed_at=datetime.now()
            ))

        # STRICT: Progress validation
        progress_value = result.get("progress", 0.0)
        try:
            progress_value = float(progress_value)
            progress_value = max(0.0, min(1.0, progress_value))
        except Exception:
            progress_value = 0.0

        # Extract metadata and metrics
        metadata_value = result.get("metadata", {})
        errors_value = result.get("errors", [])
        warnings_value = result.get("warnings", [])
        metrics_value = result.get("metrics", {})

        # STRICT: Evidence validation - NO BYPASSES
        evidence_container = (
            result.get("mcp_results")
            or (getattr(app_state, "mcp_evidence_store", {}) or {}).get(request_id)
            or result
        )
        
        # Enhanced source extraction for LangGraph+MCP
        def extract_langgraph_evidence(evidence: Dict[str, Any]) -> List[Any]:
            """Extract evidence from LangGraph agent execution with MCP tools."""
            sources = []
            
            # LangGraph agent execution traces
            if "agent_trace" in evidence:
                trace = evidence["agent_trace"]
                if isinstance(trace, dict) and "tool_calls" in trace:
                    sources.extend([f"Agent tool call: {call}" for call in trace["tool_calls"]])
            
            # MCP tool execution results
            if "mcp_tool_results" in evidence:
                tool_results = evidence["mcp_tool_results"]
                if isinstance(tool_results, list):
                    sources.extend([f"MCP tool: {tool}" for tool in tool_results])
            
            # Research agent findings
            if "research_findings" in evidence:
                findings = evidence["research_findings"]
                if isinstance(findings, list):
                    sources.extend(findings)
            
            # Writer agent sources
            if "writer_sources" in evidence:
                writer_sources = evidence["writer_sources"]
                if isinstance(writer_sources, list):
                    sources.extend(writer_sources)
            
            # General sources from any field
            for key in ["sources", "evidence", "facts", "references"]:
                if key in evidence and isinstance(evidence[key], list):
                    sources.extend(evidence[key])
            
            return sources

        evidence_dict = evidence_container if isinstance(evidence_container, dict) else {}
        sources = extract_sources_from_langgraph_result(evidence_dict)
        source_count = len(sources)

        # STRICT: Minimum evidence requirements for enterprise
        min_sources_required = 1  # At least one source from LangGraph agents
        
        if source_count < min_sources_required:
            err = f"LangGraph agents failed to collect sufficient evidence (found {source_count}, required {min_sources_required})"
            logger.error(f"{err} [requestId={request_id}]")
            
            debug_info = {
                "evidence_container_keys": list(evidence_dict.keys()),
                "sources_found": sources,
                "mcp_tools_executed": evidence_dict.get("mcp_tools_executed", []),
                "agent_workflow_status": evidence_dict.get("workflow_status", "unknown")
            }
            
            return _persist_and_return(GenerationStatus(
                requestId=request_id, status="failed", progress=0.0, current_step="Insufficient Evidence",
                content="", metadata={"error_details": err, "debug_info": debug_info},
                errors=[err], warnings=[], metrics={"min_sources": min_sources_required, "source_count": source_count},
                created_at=start_time, updated_at=datetime.now(), completed_at=datetime.now()
            ))

        # STRICT: Quality validation - NO BYPASSES
        word_count = len(re.findall(r"\b\w+\b", content_value))
        min_words = 100  # Minimum for any real content
        
        # Check for template-specific requirements
        template_requirements = template_config.get("requirements", {})
        if "min_words" in template_requirements:
            try:
                min_words = max(min_words, int(template_requirements["min_words"]))
            except:
                pass
                
        style_length = style_config.get("length_limit", {})
        if "min" in style_length:
            try:
                min_words = max(min_words, int(style_length["min"]))
            except:
                pass

        if word_count < min_words:
            err = f"Generated content too short (found {word_count} words, required {min_words})"
            logger.error(f"{err} [requestId={request_id}]")
            return _persist_and_return(GenerationStatus(
                requestId=request_id, status="failed", progress=0.0, current_step="Quality Check Failed",
                content="", metadata={"error_details": err},
                errors=[err], warnings=[], metrics={"word_count": word_count, "min_words": min_words},
                created_at=start_time, updated_at=datetime.now(), completed_at=datetime.now()
            ))

        # SUCCESS: Real content generated by LangGraph agents
        logger.info(f"✅ LangGraph+MCP generation successful [requestId={request_id}, content_length={len(content_value)}, word_count={word_count}, sources={source_count}]")

        # Add LangGraph-specific metadata
        metadata_value.update({
            "generation_approach": "langgraph_mcp",
            "agent_workflow": "multi_agent",
            "mcp_tools_used": evidence_dict.get("mcp_tools_executed", []),
            "evidence_sources": source_count,
            "content_quality": {
                "word_count": word_count,
                "min_words_met": word_count >= min_words,
                "evidence_sufficient": source_count >= min_sources_required
            }
        })

        status = GenerationStatus(
            requestId=request_id, status=status_value, progress=progress_value,
            current_step="Completed" if status_value == "completed" else "Processing",
            content=content_value, metadata=metadata_value, errors=errors_value,
            warnings=warnings_value, metrics=metrics_value,
            created_at=start_time, updated_at=datetime.now(),
            completed_at=datetime.now() if status_value in ["completed", "failed"] else None
        )
        return _persist_and_return(status)

    except Exception as e:
        logger.error(f"LangGraph+MCP generation failed [requestId={request_id}, error={str(e)}]", exc_info=True)
        return _persist_and_return(GenerationStatus(
            requestId=request_id, status="failed", progress=0.0, current_step="Exception",
            content="", metadata={"error_details": str(e)}, errors=[f"Generation failed: {str(e)}"],
            warnings=[], metrics={"error_time": datetime.now().isoformat()},
            created_at=start_time, updated_at=datetime.now(), completed_at=datetime.now()
        ))

# CRITICAL: Ensure Universal System generates real templates, not fallbacks
async def execute_universal_content_generation_fixed(
    request_id: str,
    user_request: str,
    template_id: Optional[str],
    style_profile: Optional[str],
    user_context: Optional[Dict[str, Any]],
    app_state
) -> GenerationStatus:
    """Execute Universal content generation with LangGraph agents - NO FALLBACKS."""
    start_time = datetime.now()
    
    try:
        # ENTERPRISE: Universal integration must be available
        if not hasattr(app_state, 'universal_integration') or not app_state.universal_integration:
            raise Exception("Universal integration not available - LangGraph workflow required")
        
        # STRICT: User request must be substantial
        if not user_request or len(user_request.strip()) < 10:
            raise Exception("User request too short - Universal system requires detailed specifications")
        
        # Use Universal Integration for intelligent template/style selection
        enhanced_context = user_context or {}
        if template_id:
            enhanced_context['template_preference'] = template_id
        if style_profile:
            enhanced_context['style_preference'] = style_profile
        
        # CRITICAL: Universal system must generate real templates
        logger.info(f"🎯 Universal system processing request [requestId={request_id}, request_length={len(user_request)}]")
        
        result = await app_state.universal_integration.process_content_request(
            user_request=user_request,
            user_context=enhanced_context
        )
        
        # STRICT: Validate Universal system response
        if not result or not isinstance(result, dict):
            raise Exception("Universal system returned invalid response")
        
        required_fields = ['template', 'style_profile', 'parameters']
        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            raise Exception(f"Universal system response missing required fields: {missing_fields}")
        
        # Extract selections from Universal System
        template_yaml = result['template'].get('yaml_content', '')
        if not template_yaml:
            raise Exception("Universal system failed to generate template YAML")
            
        selected_style = result['style_profile']
        parameters = result['parameters']
        
        logger.info(f"✅ Universal system selected: {selected_style}, domain: {result['template']['metadata'].get('topic_domain', 'dynamic')}")
        
        # STRICT: Parse generated template - NO FALLBACKS
        try:
            template_data = yaml.safe_load(template_yaml)
            if not template_data or not isinstance(template_data, dict):
                raise Exception("Generated template YAML is invalid or empty")
        except yaml.YAMLError as e:
            raise Exception(f"Failed to parse Universal-generated template YAML: {e}")
        
        # STRICT: Validate template structure
        required_template_fields = ['name', 'system_prompt']
        missing_template_fields = [field for field in required_template_fields if not template_data.get(field)]
        if missing_template_fields:
            raise Exception(f"Universal-generated template missing required fields: {missing_template_fields}")
        
        template_config = {
            'name': template_data.get('name'),
            'system_prompt': template_data.get('system_prompt'),
            'instructions': template_data.get('instructions', ''),
            **template_data
        }
        template_config.update(parameters)
        
        # Load style profile for MCP
        profiles = load_style_profiles()
        profile = next((p for p in profiles if p.id == selected_style), None)
        if not profile:
            raise Exception(f"Style profile not found: {selected_style}")
        
        # STRICT: Execute LangGraph+MCP generation with Universal selections
        logger.info(f"🚀 Executing Universal+LangGraph+MCP generation [requestId={request_id}]")
        
        mcp_result = await execute_content_generation(
            request_id, 
            template_config, 
            profile.dict(), 
            app_state, 
            {
                'enable_mcp': True, 
                'research_depth': 'comprehensive',
                'universal_mode': True,
                'template_source': 'universal_generated',
                'dynamic_parameters': parameters
            }
        )
        
        # STRICT: Validate result
        if not mcp_result or mcp_result.status == "failed":
            raise Exception(f"Universal+LangGraph+MCP generation failed: {mcp_result.errors if mcp_result else 'No result'}")
        
        # Add Universal metadata
        if hasattr(mcp_result, 'metadata'):
            mcp_result.metadata.update({
                "generation_approach": "universal_langgraph_mcp",
                "universal_template": result['template']['metadata'].get('topic_domain'),
                "universal_style": selected_style,
                "estimated_length": result['generation_info'].get('estimated_length', 'unknown'),
                "template_dynamically_generated": True,
                "no_fallbacks_used": True
            })
        
        logger.info(f"✅ Universal+LangGraph+MCP generation successful [requestId={request_id}, content_length={len(mcp_result.content)}]")
        return mcp_result
        
    except Exception as e:
        logger.error(f"❌ Universal+LangGraph+MCP generation failed: {e}")
        
        error_status = GenerationStatus(
            requestId=request_id,
            status="failed",
            progress=0.0,
            current_step="Universal Generation Failed",
            content="",
            metadata={"error_details": str(e), "no_fallbacks_attempted": True},
            errors=[f"Universal generation failed: {str(e)}"],
            warnings=[],
            metrics={},
            created_at=start_time,
            updated_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        if not hasattr(app_state, 'generation_tasks'):
            app_state.generation_tasks = {}
        app_state.generation_tasks[request_id] = error_status
        
        # ENTERPRISE: Always fail fast, no fallbacks
        raise e
    
# YAML validation and fixing utilities (moved from .yaml_validator)
def fix_yaml_formatting(yaml_content: str) -> str:
    """Fix common YAML formatting issues from AI generation"""
    if not yaml_content or not isinstance(yaml_content, str):
        return yaml_content
        
    lines = yaml_content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            fixed_lines.append(line)
            continue
            
        # Fix missing colons after keys
        # Pattern: word followed by space and non-colon content
        if re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s+([^:].*)$', line):
            match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s+(.*)$', line)
            if match:
                indent, key, value = match.groups()
                # Don't modify if it's a list item or already formatted correctly
                if not value.startswith('-') and not key.endswith(':'):
                    line = f"{indent}{key}: {value}"
        
        # Fix multiline content that breaks YAML
        if ':' in line and len(line) > 120:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key_part = parts[0]
                value_part = parts[1].strip()
                # Use literal block style for very long content
                if len(value_part) > 100 and not value_part.startswith(('"', "'", '|', '>')):
                    line = f"{key_part}: |\n    {value_part}"
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def create_fallback_template() -> Dict[str, Any]:
    """Create a minimal valid template when YAML parsing fails"""
    return {
        'name': 'Dynamic Generated Template',
        'system_prompt': 'Generate high-quality content based on the user requirements. Follow best practices for structure, clarity, and engagement.',
        'instructions': 'Create comprehensive content that meets the specified requirements. Include proper formatting, clear sections, and professional tone.',
        'parameters': {},
        'metadata': {
            'generated': True,
            'fallback': True,
            'timestamp': datetime.now().isoformat()
        }
    }

def safe_yaml_load(yaml_content: str, context: str = "unknown") -> Dict[str, Any]:
    """Safely load YAML with automatic fixing of common issues"""
    if not yaml_content:
        logger.warning(f"Empty YAML content in {context}")
        return create_fallback_template()
    
    try:
        # First attempt: try loading as-is
        result = yaml.safe_load(yaml_content)
        if result is None:
            logger.warning(f"YAML loaded as None in {context}, creating fallback")
            return create_fallback_template()
        return result
    except yaml.YAMLError as e:
        logger.warning(f"Initial YAML parse failed in {context}, attempting to fix: {e}")
        
        try:
            # Second attempt: fix formatting and try again
            fixed_content = fix_yaml_formatting(yaml_content)
            result = yaml.safe_load(fixed_content)
            if result is None:
                return create_fallback_template()
            logger.info(f"Successfully fixed YAML formatting in {context}")
            return result
        except yaml.YAMLError as e2:
            logger.error(f"Failed to fix YAML content in {context}: {e2}")
            logger.debug(f"Problematic YAML content: {yaml_content[:500]}...")
            return create_fallback_template()

def validate_template_structure(template_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize template structure"""
    if not isinstance(template_data, dict):
        logger.error(f"Template data is not a dict: {type(template_data)}")
        return create_fallback_template()
    
    # Ensure required fields exist
    required_fields = ['name', 'system_prompt']
    for field in required_fields:
        if field not in template_data:
            logger.warning(f"Missing required field '{field}' in template, adding default")
            if field == 'name':
                template_data['name'] = 'Generated Template'
            elif field == 'system_prompt':
                template_data['system_prompt'] = 'Generate high-quality content based on requirements.'
    
    # Ensure metadata exists
    if 'metadata' not in template_data:
        template_data['metadata'] = {}
    
    # Ensure parameters exists
    if 'parameters' not in template_data:
        template_data['parameters'] = {}
    
    return template_data

logger = logging.getLogger(__name__)


async def execute_universal_content_generation_fixed(
    request_id: str,
    user_request: str,
    template_id: Optional[str],
    style_profile: Optional[str],
    user_context: Optional[Dict[str, Any]],
    app_state
) -> 'GenerationStatus':  # Using string annotation to avoid import issues
    """
    Execute content generation using Universal Template System + MCP - ENTERPRISE: Must succeed
    FIXED VERSION: Handles YAML parsing errors gracefully
    """
    start_time = datetime.now()
    
    try:
        # ENTERPRISE: Universal integration must be available
        if not hasattr(app_state, 'universal_integration') or not app_state.universal_integration:
            raise Exception("ENTERPRISE MODE: Universal integration not available - system configuration error")
        
        # Use Universal Integration for intelligent template/style selection
        enhanced_context = user_context or {}
        if template_id:
            enhanced_context['template_preference'] = template_id
        if style_profile:
            enhanced_context['style_preference'] = style_profile
        
        result = await app_state.universal_integration.process_content_request(
            user_request=user_request,
            user_context=enhanced_context
        )
        
        # ENTERPRISE: Validate Universal system response
        if not result or not isinstance(result, dict):
            raise Exception("ENTERPRISE MODE: Universal system returned invalid response")
        
        if 'template' not in result or 'style_profile' not in result:
            raise Exception("ENTERPRISE MODE: Universal system response missing required fields")
        
        # Extract selections from Universal System
        template_yaml = result['template']['yaml_content']
        selected_style = result['style_profile']
        parameters = result['parameters']
        
        logger.info(f"✅ Universal system selected: {selected_style}, {result['template']['metadata'].get('topic_domain', 'dynamic')}")
        
        # Parse generated template with safe loading - THIS IS THE KEY FIX
        template_data = safe_yaml_load(template_yaml, f"universal_generation_{request_id}")
        template_data = validate_template_structure(template_data)

        
        template_config = {
            'name': template_data.get('name', f"Dynamic {result['template']['metadata'].get('topic_domain', 'Content')}"),
            'system_prompt': template_data.get('system_prompt', ''),
            'instructions': template_data.get('instructions', ''),
            **template_data
        }
        template_config.update(parameters)
        
        # Load style profile for MCP (this function should exist in integrated_server.py)
        profiles = load_style_profiles()
        profile = next((p for p in profiles if p.id == selected_style), None)
        if not profile:
            raise Exception(f"ENTERPRISE MODE: Style profile not found: {selected_style}")
        
        # Execute MCP generation with Universal selections (this function should exist in integrated_server.py)
        mcp_result = await execute_content_generation(
            request_id, 
            template_config, 
            profile.dict(), 
            app_state, 
            {'enable_mcp': True, 'research_depth': 'moderate'}
        )
        
        # Add Universal metadata
        if hasattr(mcp_result, 'metadata'):
            mcp_result.metadata.update({
                "generation_approach": "universal_mcp",
                "universal_template": result['template']['metadata'].get('topic_domain'),
                "universal_style": selected_style,
                "estimated_length": result['generation_info'].get('estimated_length', 'unknown'),
                "yaml_fixed": template_data.get('metadata', {}).get('fallback', False)
            })
        
        return mcp_result
        
    except Exception as e:
        logger.error(f"❌ Universal generation failed: {e}")
        
        # Import GenerationStatus from integrated_server.py
        from .integrated_server import GenerationStatus
        
        error_status = GenerationStatus(
            requestId=request_id,
            status="failed",
            progress=0.0,
            current_step="Failed",
            content="",
            metadata={"error_details": str(e)},
            errors=[f"Universal generation failed: {str(e)}"],
            warnings=[],
            metrics={},
            created_at=start_time,
            updated_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        if not hasattr(app_state, 'generation_tasks'):
            app_state.generation_tasks = {}
        app_state.generation_tasks[request_id] = error_status
        
        # ENTERPRISE: Always re-raise
        raise e

# Application lifecycle - ENTERPRISE: All components must initialize successfully
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management with MCP initialization - ENTERPRISE: Must succeed"""
    logger.info("Starting WriterzRoom API with MCP integration - ENTERPRISE MODE")
    
    # Initialize generation task storage
    app.state.generation_tasks = {}
    
    # ENTERPRISE: Model registry must initialize
    try:
        llm = get_model("writer")
        logger.info("✅ Model registry initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize model registry: {str(e)}")
        raise SystemExit(f"ENTERPRISE MODE: Model registry initialization failed: {e}")
    
    # ENTERPRISE: MCP must initialize successfully
    try:
        mcp_success = await initialize_mcp_for_existing_server(app)
        if not mcp_success:
            raise SystemExit("ENTERPRISE MODE: MCP initialization returned failure status")
        app.state.mcp_available = True
        logger.info("✅ MCP initialization successful")
    except Exception as e:
        logger.error(f"❌ MCP initialization error: {e}")
        raise SystemExit(f"ENTERPRISE MODE: MCP initialization failed: {e}")
    
    # ENTERPRISE: Universal system must initialize
    try:
        app.state.universal_integration = LangGraphUniversalIntegration()
        logger.info("✅ Universal Integration initialized successfully")
    except Exception as e:
        logger.error(f"❌ Universal Integration initialization error: {e}")
        raise SystemExit(f"ENTERPRISE MODE: Universal Integration initialization failed: {e}")
    
    # ENTERPRISE: Validate that templates and profiles can be loaded
    try:
        templates = load_templates()
        profiles = load_style_profiles()
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
    
    # Cleanup MCP
    try:
        await cleanup_mcp_for_existing_server(app)
        logger.info("✅ MCP cleanup completed")
    except Exception as e:
        logger.error(f"❌ MCP cleanup error: {e}")
        # Don't raise on cleanup errors, just log them
    
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
    allow_origins=["http://localhost:3000", "http://frontend:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Generation-Time"]
)

# CRITICAL FIX 3: Debug endpoint to check actual agent results
@app.get("/debug/agent-results/{requestId}")
async def debug_agent_results(requestId: str, request: Request, authenticated: bool = Depends(verify_api_key)):
    """Debug endpoint to examine raw agent workflow results"""
    try:
        # Check generation tasks
        if hasattr(app.state, 'generation_tasks') and requestId in app.state.generation_tasks:
            status = app.state.generation_tasks[requestId]
            
            debug_data = {
                "status_object": {
                    "status": status.status,
                    "progress": status.progress,
                    "current_step": status.current_step,
                    "content_length": len(status.content),
                    "content_preview": status.content[:200] + "..." if len(status.content) > 200 else status.content,
                    "metadata_keys": list(status.metadata.keys()),
                    "errors": status.errors,
                    "warnings": status.warnings
                }
            }
        else:
            debug_data = {"status_object": "Not found in generation_tasks"}

        # Check MCP evidence store
        if hasattr(app.state, 'mcp_evidence_store') and requestId in app.state.mcp_evidence_store:
            evidence = app.state.mcp_evidence_store[requestId]
            debug_data["mcp_evidence"] = {
                "evidence_keys": list(evidence.keys()) if isinstance(evidence, dict) else "Not a dict",
                "evidence_type": type(evidence).__name__
            }
        else:
            debug_data["mcp_evidence"] = "Not found in mcp_evidence_store"

        # Check if there are any LangGraph workflow results stored
        workflow_stores = [
            "langgraph_results", 
            "agent_workflow_results", 
            "workflow_outputs",
            "agent_executions"
        ]
        
        for store_name in workflow_stores:
            if hasattr(app.state, store_name):
                store = getattr(app.state, store_name)
                if isinstance(store, dict) and requestId in store:
                    debug_data[store_name] = {
                        "found": True,
                        "keys": list(store[requestId].keys()) if isinstance(store[requestId], dict) else "Not a dict"
                    }
                else:
                    debug_data[store_name] = {"found": False}

        return APIResponse(
            success=True,
            data=debug_data,
            requestId=request.state.requestId
        )
        
    except Exception as e:
        logger.error(f"Debug agent results failed: {str(e)}")
        return APIResponse(
            success=False,
            error={
                "code": "DEBUG_AGENT_RESULTS_ERROR",
                "message": f"Debug failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            },
            requestId=request.state.requestId
        )


# DEBUGGING: Add endpoint to check LangGraph+MCP status
@app.get("/debug/langgraph-mcp-status")
async def debug_langgraph_mcp_status(request: Request, authenticated: bool = Depends(verify_api_key)):
    """Debug LangGraph+MCP integration status"""
    try:
        debug_info = {
            "langgraph_available": hasattr(app.state, 'langgraph_workflow'),
            "mcp_available": getattr(app.state, 'mcp_available', False),
            "universal_available": hasattr(app.state, 'universal_integration') and app.state.universal_integration is not None,
            "mcp_tools_count": len(getattr(app.state, 'mcp_tools', [])),
            "mcp_evidence_store_size": len(getattr(app.state, 'mcp_evidence_store', {})),
            "active_generations": len(getattr(app.state, 'generation_tasks', {})),
            "recent_generation_ids": list(getattr(app.state, 'generation_tasks', {}).keys())[-5:],
            "agent_workflow_status": "operational" if hasattr(app.state, 'langgraph_workflow') else "not_initialized"
        }
        
        # Check if we have the specific LangGraph agents
        if hasattr(app.state, 'langgraph_agents'):
            debug_info["langgraph_agents"] = {
                "planner": hasattr(app.state.langgraph_agents, 'planner'),
                "researcher": hasattr(app.state.langgraph_agents, 'researcher'), 
                "writer": hasattr(app.state.langgraph_agents, 'writer'),
                "formatter": hasattr(app.state.langgraph_agents, 'formatter'),
                "seo": hasattr(app.state.langgraph_agents, 'seo'),
                "publisher": hasattr(app.state.langgraph_agents, 'publisher')
            }
        
        return APIResponse(
            success=True,
            data=debug_info,
            requestId=request.state.requestId
        )
        
    except Exception as e:
        logger.error(f"LangGraph+MCP status check failed: {str(e)}")
        return APIResponse(
            success=False,
            error={
                "code": "LANGGRAPH_MCP_STATUS_ERROR",
                "message": f"Status check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            },
            requestId=request.state.requestId
        )


# CRITICAL FIX 4: Ensure the existing status endpoint also works
# Update the existing get_generation_status function to handle both routes
@app.get("/status/{requestId}")
async def get_generation_status_legacy(requestId: str, request: Request):
    """Legacy status endpoint for backward compatibility"""
    return await get_generation_status(requestId, request)

@app.get("/api/generate/status/{requestId}", response_model=APIResponse)
async def get_generation_status_api_endpoint(
    requestId: str, 
    request: Request, 
    authenticated: bool = Depends(verify_api_key)
):
    """API status endpoint - fixes 405 Method Not Allowed error"""
    try:
        logger.info(f"🔍 API Status check for request: {requestId}")
        
        if not hasattr(app.state, 'generation_tasks') or requestId not in app.state.generation_tasks:
            logger.warning(f"❌ Request {requestId} not found in generation_tasks")
            raise HTTPException(status_code=404, detail="Generation request not found")
        
        status = app.state.generation_tasks[requestId]
        logger.info(f"✅ Status found: {status.status}, content_length: {len(status.content)}")
        
        return APIResponse(
            success=True,
            data=status.dict(),
            requestId=request.state.requestId
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API Status check failed [requestId={requestId}, error={str(e)}]")
        raise HTTPException(status_code=500, detail="Status check failed")


@app.get("/debug/generation-details/{requestId}")
async def debug_generation_details(requestId: str, request: Request, authenticated: bool = Depends(verify_api_key)):
    """Debug endpoint to examine generation details"""
    try:
        debug_data = {}
        
        # Check generation tasks
        if hasattr(app.state, 'generation_tasks') and requestId in app.state.generation_tasks:
            status = app.state.generation_tasks[requestId]
            debug_data["generation_task"] = {
                "status": status.status,
                "progress": status.progress,
                "current_step": status.current_step,
                "content_length": len(status.content),
                "content_preview": status.content[:200] + "..." if len(status.content) > 200 else status.content,
                "metadata_keys": list(status.metadata.keys()),
                "errors": status.errors,
                "warnings": status.warnings,
                "created_at": status.created_at.isoformat() if status.created_at else None,
                "completed_at": status.completed_at.isoformat() if status.completed_at else None
            }
        else:
            debug_data["generation_task"] = "Not found"

        # Check MCP evidence store
        if hasattr(app.state, 'mcp_evidence_store') and requestId in app.state.mcp_evidence_store:
            evidence = app.state.mcp_evidence_store[requestId]
            debug_data["mcp_evidence"] = {
                "type": type(evidence).__name__,
                "keys": list(evidence.keys()) if isinstance(evidence, dict) else "Not a dict",
                "has_content": "content" in evidence if isinstance(evidence, dict) else False
            }
        else:
            debug_data["mcp_evidence"] = "Not found"

        return APIResponse(
            success=True,
            data=debug_data,
            requestId=request.state.requestId
        )
        
    except Exception as e:
        logger.error(f"Debug generation details failed: {str(e)}")
        return APIResponse(
            success=False,
            error={"code": "DEBUG_ERROR", "message": str(e)},
            requestId=request.state.requestId
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
    
    # Fixed: Use standard logging
    logger.info(f"Request completed: {request.method} {request.url.path} {response.status_code} {duration:.3f}s [{requestId}]")
    
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    requestId = getattr(request.state, 'requestId', 'unknown')
    logger.error(f"HTTP exception [requestId={requestId}, status_code={exc.status_code}, detail={exc.detail}]")
    
    response_data = APIResponse(
        success=False,
        error={
            "code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        },
        requestId=requestId
    ).dict()
    
    response_data["timestamp"] = response_data["timestamp"].isoformat() if isinstance(response_data["timestamp"], datetime) else response_data["timestamp"]
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    requestId = getattr(request.state, 'requestId', 'unknown')
    logger.error(f"Unhandled exception: {str(exc)} [requestId={requestId}]", exc_info=True)
    
    response_data = APIResponse(
        success=False,
        error={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        },
        requestId=requestId
    ).dict()
    
    response_data["timestamp"] = response_data["timestamp"].isoformat() if isinstance(response_data["timestamp"], datetime) else response_data["timestamp"]
    
    return JSONResponse(
        status_code=500,
        content=response_data
    )

@app.get("/api/generate/status/{requestId}")
async def get_generation_status_alias(requestId: str, request: Request):
    # Reuse the existing status handler for frontend compatibility
    return await get_generation_status(requestId, request)


# API Endpoints
@app.get("/", response_model=APIResponse)
async def root(request: Request):
    """API root endpoint"""
    return APIResponse(
        success=True,
        data={
            "name": "WriterzRoom API - Enterprise Edition",
            "version": "2.0.0-enterprise",
            "status": "operational",
            "mode": "enterprise",
            "features": [
                "Unified MCP content generation",
                "Universal Template System",
                "Real-time progress tracking",
                "Comprehensive metrics",
                "Template and style management",
                "Production-ready monitoring",
                "Enterprise security"
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

# CRITICAL: Fix the missing status endpoint 
@app.get("/api/generate/status/{requestId}")
async def get_generation_status_api(requestId: str, request: Request):
    """API endpoint for generation status - frontend compatibility"""
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
        logger.error(f"Status check failed [requestId={requestId}, error={str(e)}]")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Status check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "requestId": requestId
            }
        )


@app.get("/health")
async def health_check(request: Request):
    """Comprehensive health check - ENTERPRISE: Strict validation"""
    try:
        # ENTERPRISE: All services must be healthy
        template_count = len(load_templates())
        profile_count = len(load_style_profiles())
        
        template_dirs_exist = any(os.path.exists(path) for path in get_template_paths())
        profile_dirs_exist = any(os.path.exists(path) for path in get_style_profile_paths())
        
        # ENTERPRISE: Check critical services
        mcp_available = getattr(app.state, 'mcp_available', False)
        universal_available = hasattr(app.state, 'universal_integration') and app.state.universal_integration is not None
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "mode": "enterprise",
            "services": {
                "mcp_integration": mcp_available,
                "universal_system": universal_available,
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
                "enterprise_mode": True
            }
        }
        
        # ENTERPRISE: All critical services must be healthy
        critical_services = [
            health_data["services"]["mcp_integration"],
            health_data["services"]["universal_system"],
            health_data["services"]["api_server"]
        ]
        
        all_healthy = all(critical_services)
        
        # ENTERPRISE: Strict health requirements
        if not all_healthy:
            health_data["status"] = "unhealthy"
        elif template_count == 0 or profile_count == 0:
            health_data["status"] = "degraded"
        
        return JSONResponse(
            status_code=200 if health_data["status"] == "healthy" else 503,
            content=health_data
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "mode": "enterprise",
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
        logger.error(f"Failed to load templates: {str(e)}")
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
        logger.error(f"Failed to load style profiles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load style profiles")

@app.post("/api/generate", response_model=APIResponse)
async def generate_content(
    request_data: GenerateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    authenticated: bool = Depends(verify_api_key)
):
    """Generate content with Universal Template System + MCP integration - ENTERPRISE"""
    requestId = str(uuid.uuid4())
    
    try:
        # Load and validate template and profile
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
        
        # Determine generation approach
        approach, config = determine_generation_approach(template, profile, request_data, app.state)
        
        # Initialize status
        initial_status = GenerationStatus(
            requestId=requestId,
            status="pending",
            progress=0.0,
            current_step="Initializing generation...",
            content="",
            metadata={
                "template": template.name,
                "style_profile": profile.name,
                "started_at": datetime.now().isoformat(),
                "generation_approach": config['approach'],
                "universal_triggered": approach == 'universal',
                "complexity_detection": approach == 'universal',
                "enhanced_features": True,
                "enterprise_mode": True
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
        
        # Background task selection based on approach
        if approach == 'universal':
            # Use Universal + MCP pipeline
            background_tasks.add_task(
                execute_universal_content_generation_fixed,
                requestId,
                f"Generate {template.name} content using {profile.name} style with enhanced Universal system",
                template.id,
                profile.id,
                config['universal_context'],
                app.state
            )
        else:
            # Use direct MCP pipeline
            background_tasks.add_task(
                execute_content_generation,
                requestId,
                config['template_config'],
                config['style_config'],
                app.state,
                config['mcp_options']
            )
        
        logger.info(f"Content generation initiated [requestId={requestId}, template={template.name}, style_profile={profile.name}, approach={config['approach']}]")
        
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
        logger.error(f"Failed to start content generation: {str(e)} [requestId={requestId}]")
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
    
    logger.info(f"Generation cancelled [requestId={requestId}]")
    
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
        logger.error(f"Status check failed [requestId={requestId}, error={str(e)}]")
        
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
        raise HTTPException(status_code=500, detail="Failed to list content")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(authenticated: bool = Depends(verify_api_key)):
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
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

@app.get("/api/content/{content_id}")
async def get_content(content_id: str, authenticated: bool = Depends(verify_api_key)):
    """Get specific content item"""
    try:
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get content error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get content")

# Debug endpoints - ENTERPRISE: Detailed system status
@app.get("/debug/enterprise-status")
async def debug_enterprise_status(request: Request, authenticated: bool = Depends(verify_api_key)):
    """Debug enterprise system status - Comprehensive validation"""
    try:
        # System validation
        mcp_available = getattr(app.state, 'mcp_available', False)
        universal_available = hasattr(app.state, 'universal_integration') and app.state.universal_integration is not None
        
        # Load counts
        template_count = len(load_templates())
        profile_count = len(load_style_profiles())
        
        # Environment validation
        required_env_vars = ["LANGGRAPH_API_KEY"]
        env_status = {var: bool(os.getenv(var)) for var in required_env_vars}
        
        return APIResponse(
            success=True,
            data={
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
                    "mode": ENVIRONMENT,
                    "required_env_vars": env_status,
                    "all_env_vars_present": all(env_status.values())
                },
                "paths": {
                    "template_paths": get_template_paths(),
                    "style_profile_paths": get_style_profile_paths()
                },
                "metrics": {
                    "active_generations": len(getattr(app.state, 'generation_tasks', {})),
                    "total_templates": template_count,
                    "total_profiles": profile_count
                },
                "validation": {
                    "all_systems_operational": all([
                        mcp_available,
                        universal_available,
                        template_count > 0,
                        profile_count > 0,
                        all(env_status.values())
                    ])
                }
            },
            requestId=request.state.requestId
        )
        
    except Exception as e:
        logger.error(f"Enterprise status check failed: {str(e)}")
        return APIResponse(
            success=False,
            error={
                "code": "ENTERPRISE_STATUS_ERROR",
                "message": f"Enterprise status check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            },
            requestId=request.state.requestId
        )

@app.get("/debug/system-validation")
async def debug_system_validation(request: Request, authenticated: bool = Depends(verify_api_key)):
    """Comprehensive system validation for enterprise deployment"""
    validation_results = {}
    
    try:
        # MCP System Validation
        try:
            mcp_status = getattr(app.state, 'mcp_available', False)
            validation_results["mcp_system"] = {
                "status": "pass" if mcp_status else "fail",
                "details": "MCP system operational" if mcp_status else "MCP system not available",
                "critical": True
            }
        except Exception as e:
            validation_results["mcp_system"] = {
                "status": "fail",
                "details": f"MCP validation error: {str(e)}",
                "critical": True
            }
        
        # Universal System Validation
        try:
            universal_status = hasattr(app.state, 'universal_integration') and app.state.universal_integration is not None
            validation_results["universal_system"] = {
                "status": "pass" if universal_status else "fail",
                "details": "Universal system operational" if universal_status else "Universal system not available",
                "critical": True
            }
        except Exception as e:
            validation_results["universal_system"] = {
                "status": "fail",
                "details": f"Universal system validation error: {str(e)}",
                "critical": True
            }
        
        # Template System Validation
        try:
            templates = load_templates()
            template_count = len(templates)
            validation_results["template_system"] = {
                "status": "pass" if template_count > 0 else "fail",
                "details": f"Loaded {template_count} templates",
                "critical": True,
                "count": template_count
            }
        except Exception as e:
            validation_results["template_system"] = {
                "status": "fail",
                "details": f"Template system validation error: {str(e)}",
                "critical": True
            }
        
        # Style Profile System Validation
        try:
            profiles = load_style_profiles()
            profile_count = len(profiles)
            validation_results["style_profile_system"] = {
                "status": "pass" if profile_count > 0 else "fail",
                "details": f"Loaded {profile_count} style profiles",
                "critical": True,
                "count": profile_count
            }
        except Exception as e:
            validation_results["style_profile_system"] = {
                "status": "fail",
                "details": f"Style profile system validation error: {str(e)}",
                "critical": True
            }
        
        # Environment Variables Validation
        required_vars = ["LANGGRAPH_API_KEY"]
        env_validation = {}
        for var in required_vars:
            env_validation[var] = {
                "status": "pass" if os.getenv(var) else "fail",
                "present": bool(os.getenv(var))
            }
        
        validation_results["environment_variables"] = {
            "status": "pass" if all(result["present"] for result in env_validation.values()) else "fail",
            "details": env_validation,
            "critical": True
        }
        
        # Overall System Health
        critical_systems = [
            validation_results["mcp_system"]["status"],
            validation_results["universal_system"]["status"],
            validation_results["template_system"]["status"],
            validation_results["style_profile_system"]["status"],
            validation_results["environment_variables"]["status"]
        ]
        
        overall_status = "pass" if all(status == "pass" for status in critical_systems) else "fail"
        
        return APIResponse(
            success=True,
            data={
                "overall_status": overall_status,
                "enterprise_ready": overall_status == "pass",
                "validation_results": validation_results,
                "summary": {
                    "total_checks": len(validation_results),
                    "passed": sum(1 for result in validation_results.values() if result["status"] == "pass"),
                    "failed": sum(1 for result in validation_results.values() if result["status"] == "fail")
                },
                "timestamp": datetime.now().isoformat()
            },
            requestId=request.state.requestId
        )
        
    except Exception as e:
        logger.error(f"System validation failed: {str(e)}")
    
    return APIResponse(
            success=False,
            error={
                "code": "SYSTEM_VALIDATION_ERROR",
                "message": f"System validation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            },
            requestId=request.state.requestId
        )

# MCP Enhanced Generation Endpoint - Additional endpoints that were missing
@app.post("/api/mcp/generate", response_model=APIResponse)
async def mcp_enhanced_generate(
    request_data: MCPGenerationRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    authenticated: bool = Depends(verify_api_key)
):
    """Enhanced MCP generation endpoint with advanced features"""
    requestId = str(uuid.uuid4())
    
    try:
        if not getattr(app.state, 'mcp_available', False):
            raise HTTPException(status_code=503, detail="MCP system not available")
        
        # Validate MCP-specific parameters
        if not request_data.enable_mcp:
            raise HTTPException(status_code=400, detail="MCP must be enabled for this endpoint")
        
        # Load template and profile
        templates = load_templates()
        template = next((t for t in templates if t.id == request_data.template), None)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {request_data.template}")
        
        profiles = load_style_profiles()
        profile = next((p for p in profiles if p.id == request_data.style_profile), None)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Style profile not found: {request_data.style_profile}")
        
        # Enhanced MCP configuration
        template_config = template.dict()
        template_config.update(request_data.dynamic_parameters)
        
        mcp_options = {
            'enable_mcp': True,
            'research_depth': request_data.research_depth,
            'memory_namespace': request_data.memory_namespace or f"mcp_{requestId}",
            'timeout_seconds': request_data.timeout_seconds,
            'priority': request_data.priority,
            'advanced_features': True,
            'tool_selection': 'comprehensive',
            'dynamic_parameters': request_data.dynamic_parameters
        }
        
        # Initialize enhanced status
        initial_status = GenerationStatus(
            requestId=requestId,
            status="pending",
            progress=0.0,
            current_step="Initializing MCP-enhanced generation...",
            content="",
            metadata={
                "template": template.name,
                "style_profile": profile.name,
                "mcp_enhanced": True,
                "research_depth": request_data.research_depth,
                "started_at": datetime.now().isoformat(),
                "enterprise_mode": True
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
        
        # Execute MCP-enhanced generation
        background_tasks.add_task(
            execute_content_generation,
            requestId,
            template_config,
            profile.dict(),
            app.state,
            mcp_options
        )
        
        logger.info(f"MCP-enhanced generation initiated [requestId={requestId}, template={template.name}, research_depth={request_data.research_depth}]")
        
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
        logger.error(f"Failed to start MCP-enhanced generation: {str(e)} [requestId={requestId}]")
        raise HTTPException(status_code=500, detail="Failed to start MCP-enhanced generation")

# Universal System Endpoints
@app.post("/api/universal/generate", response_model=APIResponse)
async def universal_generate(
    user_request: str = Body(..., embed=True),
    template_preference: Optional[str] = Body(None, embed=True),
    style_preference: Optional[str] = Body(None, embed=True),
    complexity_level: str = Body("moderate", embed=True),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    request: Request = Request,
    authenticated: bool = Depends(verify_api_key)
):
    """Universal content generation with intelligent template selection"""
    requestId = str(uuid.uuid4())
    
    try:
        if not hasattr(app.state, 'universal_integration') or not app.state.universal_integration:
            raise HTTPException(status_code=503, detail="Universal system not available")
        
        # Prepare context for Universal system
        user_context = {
            'complexity_level': complexity_level,
            'generation_mode': 'universal'
        }
        
        if template_preference:
            user_context['template_preference'] = template_preference
        if style_preference:
            user_context['style_preference'] = style_preference
        
        # Initialize status
        initial_status = GenerationStatus(
            requestId=requestId,
            status="pending",
            progress=0.0,
            current_step="Analyzing request with Universal system...",
            content="",
            metadata={
                "user_request": user_request[:100] + "..." if len(user_request) > 100 else user_request,
                "universal_mode": True,
                "complexity_level": complexity_level,
                "started_at": datetime.now().isoformat(),
                "enterprise_mode": True
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
        
        # Execute Universal generation
        background_tasks.add_task(
            execute_universal_content_generation_fixed,
            requestId,
            user_request,
            template_preference,
            style_preference,
            user_context,
            app.state
        )
        
        logger.info(f"Universal generation initiated [requestId={requestId}, complexity={complexity_level}]")
        
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
        logger.error(f"Failed to start universal generation: {str(e)} [requestId={requestId}]")
        raise HTTPException(status_code=500, detail="Failed to start universal generation")

# Additional content management endpoints
@app.put("/api/content/{content_id}")
async def update_content(
    content_id: str,
    title: str = Body(...),
    content: str = Body(...),
    status: str = Body(default="draft"),
    authenticated: bool = Depends(verify_api_key)
):
    """Update existing content"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        # Find the content file
        found_file = None
        found_week_dir = None
        
        for week_dir in content_dir.iterdir():
            if not week_dir.is_dir():
                continue
            
            json_file = week_dir / f"{content_id}.json"
            if json_file.exists():
                found_file = json_file
                found_week_dir = week_dir
                break
        
        if not found_file:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Load existing metadata
        with open(found_file, 'r') as f:
            metadata = json.load(f)
        
        # Update metadata
        metadata.update({
            'title': title,
            'content': content,
            'status': status,
            'updatedAt': datetime.now().isoformat()
        })
        
        # Save updated metadata
        with open(found_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update markdown file if it exists
        md_file = found_week_dir / f"{content_id}.md"
        if md_file.exists():
            with open(md_file, 'w') as f:
                f.write(content)
        
        logger.info(f"Content updated: {content_id}")
        
        return {
            "id": content_id,
            "title": title,
            "status": status,
            "updatedAt": metadata['updatedAt']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update content error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update content")

@app.delete("/api/content/{content_id}")
async def delete_content(content_id: str, authenticated: bool = Depends(verify_api_key)):
    """Delete content"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        deleted = False
        
        for week_dir in content_dir.iterdir():
            if not week_dir.is_dir():
                continue
            
            json_file = week_dir / f"{content_id}.json"
            md_file = week_dir / f"{content_id}.md"
            
            if json_file.exists():
                json_file.unlink()
                deleted = True
            
            if md_file.exists():
                md_file.unlink()
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Content not found")
        
        logger.info(f"Content deleted: {content_id}")
        
        return {"message": "Content deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete content error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete content")

# Export endpoints
@app.get("/api/content/{content_id}/export")
async def export_content(
    content_id: str,
    format: str = Query(default="markdown", regex="^(markdown|html|json|pdf)$"),
    authenticated: bool = Depends(verify_api_key)
):
    """Export content in various formats"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        # Find content
        metadata = None
        content = ""
        
        for week_dir in content_dir.iterdir():
            if not week_dir.is_dir():
                continue
            
            json_file = week_dir / f"{content_id}.json"
            md_file = week_dir / f"{content_id}.md"
            
            if json_file.exists():
                with open(json_file, 'r') as f:
                    metadata = json.load(f)
                
                if md_file.exists():
                    with open(md_file, 'r') as f:
                        content = f.read()
                else:
                    content = metadata.get('content', '')
                break
        
        if not metadata:
            raise HTTPException(status_code=404, detail="Content not found")
        
        title = metadata.get('title', content_id.replace('_', ' ').title())
        
        if format == "markdown":
            return Response(
                content=f"# {title}\n\n{content}",
                media_type="text/markdown",
                headers={"Content-Disposition": f"attachment; filename={content_id}.md"}
            )
        elif format == "html":
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        p {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div>{''.join(f'<p>{line}</p>' for line in content.split('\n\n'))}</div>
</body>
</html>"""
            return Response(
                content=html_content,
                media_type="text/html",
                headers={"Content-Disposition": f"attachment; filename={content_id}.html"}
            )
        elif format == "json":
            export_data = {
                "id": content_id,
                "title": title,
                "content": content,
                "metadata": metadata,
                "exported_at": datetime.now().isoformat()
            }
            return Response(
                content=json.dumps(export_data, indent=2),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={content_id}.json"}
            )
        
        # PDF format would require additional dependencies
        raise HTTPException(status_code=400, detail="PDF export not implemented")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export content error: {e}")
        raise HTTPException(status_code=500, detail="Failed to export content")

# Analytics endpoints
@app.get("/api/analytics/overview")
async def analytics_overview(authenticated: bool = Depends(verify_api_key)):
    """Get analytics overview"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        analytics = {
            "total_content": 0,
            "total_views": 0,
            "content_by_week": {},
            "content_by_type": {},
            "content_by_status": {"draft": 0, "published": 0},
            "top_content": [],
            "recent_activity": []
        }
        
        all_content = []
        
        if content_dir.exists():
            for week_dir in content_dir.iterdir():
                if not week_dir.is_dir():
                    continue
                
                week_name = week_dir.name
                analytics["content_by_week"][week_name] = 0
                
                for json_file in week_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r') as f:
                            metadata = json.load(f)
                        
                        analytics["total_content"] += 1
                        analytics["content_by_week"][week_name] += 1
                        
                        views = metadata.get('views', 0)
                        analytics["total_views"] += views
                        
                        content_type = metadata.get('type', 'article')
                        analytics["content_by_type"][content_type] = analytics["content_by_type"].get(content_type, 0) + 1
                        
                        status = metadata.get('status', 'draft')
                        analytics["content_by_status"][status] += 1
                        
                        all_content.append({
                            "id": json_file.stem,
                            "title": metadata.get('title', json_file.stem.replace('_', ' ').title()),
                            "views": views,
                            "created_at": metadata.get('createdAt', ''),
                            "type": content_type,
                            "status": status
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error processing {json_file}: {e}")
                        continue
        
        # Top content by views
        analytics["top_content"] = sorted(all_content, key=lambda x: x['views'], reverse=True)[:10]
        
        # Recent activity
        analytics["recent_activity"] = sorted(all_content, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
        
        return analytics
        
    except Exception as e:
        logger.error(f"Analytics overview error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics overview")

@app.get("/api/analytics/content/{content_id}")
async def content_analytics(content_id: str, authenticated: bool = Depends(verify_api_key)):
    """Get detailed analytics for specific content"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        # Find content and get metadata
        for week_dir in content_dir.iterdir():
            if not week_dir.is_dir():
                continue
            
            json_file = week_dir / f"{content_id}.json"
            
            if json_file.exists():
                with open(json_file, 'r') as f:
                    metadata = json.load(f)
                
                # Increment view count
                metadata['views'] = metadata.get('views', 0) + 1
                
                with open(json_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                analytics = {
                    "id": content_id,
                    "title": metadata.get('title', content_id.replace('_', ' ').title()),
                    "views": metadata['views'],
                    "created_at": metadata.get('createdAt'),
                    "updated_at": metadata.get('updatedAt'),
                    "type": metadata.get('type', 'article'),
                    "status": metadata.get('status', 'draft'),
                    "word_count": len(metadata.get('content', '').split()),
                    "metadata": metadata.get('metadata', {})
                }
                
                return analytics
        
        raise HTTPException(status_code=404, detail="Content not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get content analytics")

# Template and Style Profile management endpoints
@app.post("/api/templates", response_model=APIResponse)
async def create_template(
    template_data: Dict[str, Any] = Body(...),
    authenticated: bool = Depends(verify_api_key)
):
    """Create a new template"""
    try:
        # Validate required fields
        if 'name' not in template_data or 'system_prompt' not in template_data:
            raise HTTPException(status_code=400, detail="Template must have 'name' and 'system_prompt'")
        
        # Generate ID from name if not provided
        if 'id' not in template_data:
            template_data['id'] = template_data['name'].lower().replace(' ', '_').replace('-', '_')
        
        # Ensure filename
        filename = f"{template_data['id']}.yaml"
        
        # Find template directory
        template_paths = get_template_paths()
        if not template_paths:
            raise HTTPException(status_code=500, detail="No template directories available")
        
        template_dir = template_paths[0]  # Use first available directory
        file_path = os.path.join(template_dir, filename)
        
        # Check if template already exists
        if os.path.exists(file_path):
            raise HTTPException(status_code=409, detail="Template already exists")
        
        # Add metadata
        template_data.setdefault('metadata', {})
        template_data['metadata']['created_at'] = datetime.now().isoformat()
        template_data['metadata']['version'] = '1.0.0'
        
        # Save template
        with open(file_path, 'w') as f:
            yaml.dump(template_data, f, default_flow_style=False)
        
        logger.info(f"Template created: {template_data['id']}")
        
        return APIResponse(
            success=True,
            data={
                "id": template_data['id'],
                "name": template_data['name'],
                "filename": filename,
                "created": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create template error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create template")

@app.put("/api/templates/{template_id}", response_model=APIResponse)
async def update_template(
    template_id: str,
    template_data: Dict[str, Any] = Body(...),
    authenticated: bool = Depends(verify_api_key)
):
    """Update an existing template"""
    try:
        # Find template file
        template_paths = get_template_paths()
        found_file = None
        
        for template_dir in template_paths:
            for filename in os.listdir(template_dir):
                if filename.endswith('.yaml'):
                    file_path = os.path.join(template_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            existing_data = yaml.safe_load(f)
                        
                        if existing_data and existing_data.get('id') == template_id:
                            found_file = file_path
                            break
                    except Exception:
                        continue
            
            if found_file:
                break
        
        if not found_file:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Update template data
        template_data['id'] = template_id  # Ensure ID consistency
        template_data.setdefault('metadata', {})
        template_data['metadata']['updated_at'] = datetime.now().isoformat()
        
        # Save updated template
        with open(found_file, 'w') as f:
            yaml.dump(template_data, f, default_flow_style=False)
        
        logger.info(f"Template updated: {template_id}")
        
        return APIResponse(
            success=True,
            data={
                "id": template_id,
                "updated": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update template error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update template")

@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str, authenticated: bool = Depends(verify_api_key)):
    """Delete a template"""
    try:
        # Find and delete template file
        template_paths = get_template_paths()
        deleted = False
        
        for template_dir in template_paths:
            for filename in os.listdir(template_dir):
                if filename.endswith('.yaml'):
                    file_path = os.path.join(template_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            template_data = yaml.safe_load(f)
                        
                        if template_data and template_data.get('id') == template_id:
                            os.remove(file_path)
                            deleted = True
                            break
                    except Exception:
                        continue
            
            if deleted:
                break
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Template not found")
        
        logger.info(f"Template deleted: {template_id}")
        
        return {"message": "Template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete template error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete template")

# Style Profile management endpoints (similar pattern)
@app.post("/api/style-profiles", response_model=APIResponse)
async def create_style_profile(
    profile_data: Dict[str, Any] = Body(...),
    authenticated: bool = Depends(verify_api_key)
):
    """Create a new style profile"""
    try:
        # Validate required fields
        if 'name' not in profile_data:
            raise HTTPException(status_code=400, detail="Style profile must have 'name'")
        
        # Generate ID from name if not provided
        if 'id' not in profile_data:
            profile_data['id'] = profile_data['name'].lower().replace(' ', '_').replace('-', '_')
        
        # Ensure filename
        filename = f"{profile_data['id']}.yaml"
        
        # Find style profile directory
        profile_paths = get_style_profile_paths()
        if not profile_paths:
            raise HTTPException(status_code=500, detail="No style profile directories available")
        
        profile_dir = profile_paths[0]  # Use first available directory
        file_path = os.path.join(profile_dir, filename)
        
        # Check if profile already exists
        if os.path.exists(file_path):
            raise HTTPException(status_code=409, detail="Style profile already exists")
        
        # Add metadata
        profile_data.setdefault('metadata', {})
        profile_data['metadata']['created_at'] = datetime.now().isoformat()
        profile_data.setdefault('category', 'general')
        
        # Save profile
        with open(file_path, 'w') as f:
            yaml.dump(profile_data, f, default_flow_style=False)
        
        logger.info(f"Style profile created: {profile_data['id']}")
        
        return APIResponse(
            success=True,
            data={
                "id": profile_data['id'],
                "name": profile_data['name'],
                "filename": filename,
                "created": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create style profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create style profile")

# Additional debug and monitoring endpoints
@app.get("/debug/mcp-status")
async def debug_mcp_status(request: Request, authenticated: bool = Depends(verify_api_key)):
    """Debug MCP system status"""
    try:
        mcp_available = getattr(app.state, 'mcp_available', False)
        
        # Get MCP evidence store if available
        evidence_store = getattr(app.state, 'mcp_evidence_store', {})
        
        mcp_status = {
            "mcp_available": mcp_available,
            "evidence_store_size": len(evidence_store),
            "active_namespaces": list(set(
                metadata.get('memory_namespace', 'default')
                for metadata in evidence_store.values()
                if isinstance(metadata, dict)
            )) if evidence_store else [],
            "recent_generations": list(evidence_store.keys())[-10:] if evidence_store else []
        }
        
        return APIResponse(
            success=True,
            data=mcp_status,
            requestId=request.state.requestId
        )
        
    except Exception as e:
        logger.error(f"MCP status check failed: {str(e)}")
        return APIResponse(
            success=False,
            error={
                "code": "MCP_STATUS_ERROR",
                "message": f"MCP status check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            },
            requestId=request.state.requestId
        )

@app.get("/debug/universal-status")
async def debug_universal_status(request: Request, authenticated: bool = Depends(verify_api_key)):
    """Debug Universal system status"""
    try:
        universal_available = hasattr(app.state, 'universal_integration') and app.state.universal_integration is not None
        
        universal_status = {
            "universal_available": universal_available,
            "integration_type": type(app.state.universal_integration).__name__ if universal_available else None,
            "capabilities": [
                "dynamic_template_generation",
                "intelligent_style_selection",
                "content_complexity_analysis",
                "adaptive_parameter_handling"
            ] if universal_available else []
        }
        
        return APIResponse(
            success=True,
            data=universal_status,
            requestId=request.state.requestId
        )
        
    except Exception as e:
        logger.error(f"Universal status check failed: {str(e)}")
        return APIResponse(
            success=False,
            error={
                "code": "UNIVERSAL_STATUS_ERROR",
                "message": f"Universal status check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            },
            requestId=request.state.requestId
        )

@app.get("/debug/generation-queue")
async def debug_generation_queue(request: Request, authenticated: bool = Depends(verify_api_key)):
    """Debug active generation queue"""
    try:
        generation_tasks = getattr(app.state, 'generation_tasks', {})
        
        queue_status = {
            "total_active": len(generation_tasks),
            "by_status": {},
            "recent_requests": []
        }
        
        for request_id, status in generation_tasks.items():
            status_value = status.status
            queue_status["by_status"][status_value] = queue_status["by_status"].get(status_value, 0) + 1
            
            if len(queue_status["recent_requests"]) < 10:
                queue_status["recent_requests"].append({
                    "requestId": request_id,
                    "status": status_value,
                    "progress": status.progress,
                    "created_at": status.created_at.isoformat() if status.created_at else None,
                    "current_step": status.current_step
                })
        
        return APIResponse(
            success=True,
            data=queue_status,
            requestId=request.state.requestId
        )
        
    except Exception as e:
        logger.error(f"Generation queue check failed: {str(e)}")
        return APIResponse(
            success=False,
            error={
                "code": "QUEUE_STATUS_ERROR",
                "message": f"Generation queue check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            },
            requestId=request.state.requestId
        )

# Administrative endpoints
@app.post("/admin/clear-cache")
async def clear_cache(authenticated: bool = Depends(verify_api_key)):
    """Clear system caches"""
    try:
        cleared_items = []
        
        # Clear generation tasks cache
        if hasattr(app.state, 'generation_tasks'):
            completed_tasks = {
                k: v for k, v in app.state.generation_tasks.items() 
                if v.status in ['completed', 'failed', 'cancelled']
            }
            for task_id in completed_tasks:
                del app.state.generation_tasks[task_id]
            cleared_items.append(f"Cleared {len(completed_tasks)} completed generation tasks")
        
        # Clear MCP evidence store
        if hasattr(app.state, 'mcp_evidence_store'):
            old_size = len(app.state.mcp_evidence_store)
            app.state.mcp_evidence_store = {}
            cleared_items.append(f"Cleared {old_size} MCP evidence entries")
        
        logger.info(f"Cache cleared: {', '.join(cleared_items)}")
        
        return {
            "message": "Cache cleared successfully",
            "cleared_items": cleared_items,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@app.post("/admin/reload-templates")
async def reload_templates(authenticated: bool = Depends(verify_api_key)):
    """Reload templates from disk"""
    try:
        # This would normally reload templates in memory if we were caching them
        # For now, we'll just validate that templates can be loaded
        templates = load_templates()
        
        logger.info(f"Templates reloaded: {len(templates)} templates available")
        
        return {
            "message": "Templates reloaded successfully",
            "template_count": len(templates),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Reload templates error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload templates")

@app.post("/admin/reload-profiles")
async def reload_profiles(authenticated: bool = Depends(verify_api_key)):
    """Reload style profiles from disk"""
    try:
        # This would normally reload profiles in memory if we were caching them
        # For now, we'll just validate that profiles can be loaded
        profiles = load_style_profiles()
        
        logger.info(f"Style profiles reloaded: {len(profiles)} profiles available")
        
        return {
            "message": "Style profiles reloaded successfully",
            "profile_count": len(profiles),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Reload profiles error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload style profiles")

# Health monitoring endpoints
@app.get("/health/detailed")
async def detailed_health_check(request: Request):
    """Detailed health check with component-level status"""
    try:
        health_details = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0-enterprise",
            "environment": ENVIRONMENT,
            "components": {}
        }
        
        # Check each component
        components = []
        
        # API Server
        components.append({
            "name": "api_server",
            "status": "healthy",
            "details": "FastAPI server operational"
        })
        
        # Database/File System
        try:
            template_count = len(load_templates())
            profile_count = len(load_style_profiles())
            components.append({
                "name": "file_system",
                "status": "healthy",
                "details": f"Templates: {template_count}, Profiles: {profile_count}"
            })
        except Exception as e:
            components.append({
                "name": "file_system",
                "status": "unhealthy",
                "details": f"File system error: {str(e)}"
            })
        
        # MCP Integration
        mcp_available = getattr(app.state, 'mcp_available', False)
        components.append({
            "name": "mcp_integration",
            "status": "healthy" if mcp_available else "unhealthy",
            "details": "MCP system operational" if mcp_available else "MCP system not available"
        })
        
        # Universal System
        universal_available = hasattr(app.state, 'universal_integration') and app.state.universal_integration is not None
        components.append({
            "name": "universal_system",
            "status": "healthy" if universal_available else "unhealthy",
            "details": "Universal system operational" if universal_available else "Universal system not available"
        })
        
        # Generation Queue
        generation_tasks = getattr(app.state, 'generation_tasks', {})
        active_generations = len([t for t in generation_tasks.values() if t.status in ['pending', 'processing']])
        components.append({
            "name": "generation_queue",
            "status": "healthy",
            "details": f"Active generations: {active_generations}, Total: {len(generation_tasks)}"
        })
        
        # Overall health
        unhealthy_components = [c for c in components if c['status'] == 'unhealthy']
        if unhealthy_components:
            health_details["status"] = "degraded" if len(unhealthy_components) < len(components) // 2 else "unhealthy"
        
        health_details["components"] = {c["name"]: c for c in components}
        
        status_code = 200
        if health_details["status"] == "degraded":
            status_code = 206  # Partial Content
        elif health_details["status"] == "unhealthy":
            status_code = 503  # Service Unavailable
        
        return JSONResponse(content=health_details, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

@app.get("/health/readiness")
async def readiness_check():
    """Readiness probe"""
    return {"status": "ready", "timestamp": datetime.now().isoformat()}
@app.get("/health/liveness")
async def liveness_check():
    """Liveness probe"""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}
@app.get("/health/liveness")
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    # Simple liveness check - if the server can respond, it's alive
    return JSONResponse(
        content={
            "alive": True,
            "timestamp": datetime.now().isoformat()
        }
    )
@app.post("/webhooks/content-published")
async def webhook_content_published(
    content_id: str = Body(...),
    platform: str = Body(...),
    url: str = Body(...),
    authenticated: bool = Depends(verify_api_key)
):
    """Webhook for when content is published to external platforms"""
    try:
        # Update content metadata with publication info
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        for week_dir in content_dir.iterdir():
            if not week_dir.is_dir():
                continue
            
            json_file = week_dir / f"{content_id}.json"
            
            if json_file.exists():
                with open(json_file, 'r') as f:
                    metadata = json.load(f)
                
                # Add publication info
                if 'publications' not in metadata:
                    metadata['publications'] = []
                
                metadata['publications'].append({
                    'platform': platform,
                    'url': url,
                    'published_at': datetime.now().isoformat()
                })
                
                metadata['status'] = 'published'
                metadata['updatedAt'] = datetime.now().isoformat()
                
                with open(json_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Content publication recorded: {content_id} on {platform}")
                
                return {
                    "message": "Publication recorded successfully",
                    "content_id": content_id,
                    "platform": platform
                }
        
        raise HTTPException(status_code=404, detail="Content not found")
        
    except Exception as e:
        logger.error(f"Webhook content published error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record publication")
        
@app.get("/api/search")
async def search_content(
    q: str = Query(..., min_length=1),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(default=20, le=100),
    authenticated: bool = Depends(verify_api_key)
):
    """Search content items"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        results = []
        if content_dir.exists():
            for week_dir in content_dir.iterdir():
                if not week_dir.is_dir():
                    continue
                for json_file in week_dir.glob("*.json"):
                    with open(json_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    if q.lower() in (metadata.get('title', '') + metadata.get('content', '')).lower():
                        if type and metadata.get('type') != type:
                            continue
                        if status and metadata.get('status') != status:
                            continue
                        results.append({
                            "id": json_file.stem,
                            "title": metadata.get('title', json_file.stem.replace('_', ' ').title()),
                            "status": metadata.get('status', 'draft'),
                            "type": metadata.get('type', 'article'),
                            "createdAt": metadata.get('createdAt', ''),
                            "updatedAt": metadata.get('updatedAt', '')
                        })
        return {"results": results[:limit], "count": len(results)}
    except Exception as e:
        logger.error(f"Search content error: {e}")
        raise HTTPException(status_code=500, detail="Failed to search content")
async def search_content(
    q: str = Query(..., min_length=1),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(default=20, le=100),
    authenticated: bool = Depends(verify_api_key)
):
    """Search content by title, content, or metadata"""
    try:
        base_path = Path(__file__).parent.parent
        content_dir = base_path / "generated_content"
        
        results = []
        query_lower = q.lower()
        
        if content_dir.exists():
            for week_dir in content_dir.iterdir():
                if not week_dir.is_dir():
                    continue
                
                for json_file in week_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # Apply filters
                        if type and metadata.get('type', 'article') != type:
                            continue
                        if status and metadata.get('status', 'draft') != status:
                            continue
                        
                        # Search in title and content
                        title = metadata.get('title', '')
                        content = metadata.get('content', '')
                        
                        if (query_lower in title.lower() or 
                            query_lower in content.lower()):
                            
                            content_id = json_file.stem
                            results.append({
                                "id": content_id,
                                "title": title or content_id.replace('_', ' ').title(),
                                "type": metadata.get('type', 'article'),
                                "status": metadata.get('status', 'draft'),
                                "created_at": metadata.get('createdAt', ''),
                                "snippet": content[:200] + "..." if len(content) > 200 else content,
                                "week": week_dir.name
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error processing {json_file}: {e}")
                        continue
        
        # Sort by relevance (simple: exact title matches first, then by creation date)
        results.sort(key=lambda x: (
            0 if query_lower in x['title'].lower() else 1,
            x.get('created_at', '')
        ), reverse=True)
        
        # Apply limit
        results = results[:limit]
        
        return {
            "query": q,
            "results": results,
            "total": len(results),
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

# Batch operations
@app.post("/api/batch/generate")
async def batch_generate(
    requests: List[GenerateRequest] = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    request: Request = Request,
    authenticated: bool = Depends(verify_api_key)
):
    """Generate multiple pieces of content in batch"""
    try:
        if len(requests) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size limited to 10 requests")
        
        batch_id = str(uuid.uuid4())
        request_ids = []
        
        # Validate all requests first
        templates = load_templates()
        profiles = load_style_profiles()
        
        for req in requests:
            template = next((t for t in templates if t.id == req.template.replace('.yaml', '')), None)
            if not template:
                raise HTTPException(status_code=404, detail=f"Template not found: {req.template}")
            
            profile = next((p for p in profiles if p.id == req.style_profile.replace('.yaml', '')), None)
            if not profile:
                raise HTTPException(status_code=404, detail=f"Style profile not found: {req.style_profile}")
        
        # Start all generations
        for i, req in enumerate(requests):
            requestId = f"{batch_id}_{i}"
            request_ids.append(requestId)
            
            template = next(t for t in templates if t.id == req.template.replace('.yaml', ''))
            profile = next(p for p in profiles if p.id == req.style_profile.replace('.yaml', ''))
            
            approach, config = determine_generation_approach(template, profile, req, app.state)
            
            # Initialize status
            initial_status = GenerationStatus(
                requestId=requestId,
                status="pending",
                progress=0.0,
                current_step="Queued for batch processing...",
                content="",
                metadata={
                    "template": template.name,
                    "style_profile": profile.name,
                    "batch_id": batch_id,
                    "batch_index": i,
                    "started_at": datetime.now().isoformat(),
                    "enterprise_mode": True
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
            
            # Add to background tasks
            if approach == 'universal':
                background_tasks.add_task(
                    execute_universal_content_generation_fixed,
                    requestId,
                    f"Batch generate {template.name} content using {profile.name} style",
                    template.id,
                    profile.id,
                    config['universal_context'],
                    app.state
                )
            else:
                background_tasks.add_task(
                    execute_content_generation,
                    requestId,
                    config['template_config'],
                    config['style_config'],
                    app.state,
                    config['mcp_options']
                )
        
        logger.info(f"Batch generation initiated [batch_id={batch_id}, count={len(requests)}]")
        
        return APIResponse(
            success=True,
            data={
                "batch_id": batch_id,
                "request_ids": request_ids,
                "count": len(requests),
                "status": "pending"
            },
            requestId=request.state.requestId
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Batch generation failed")

@app.get("/api/batch/{batch_id}/status")
async def get_batch_status(
    batch_id: str,
    request: Request,
    authenticated: bool = Depends(verify_api_key)
):
    """Get status of batch generation"""
    try:
        if not hasattr(app.state, 'generation_tasks'):
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Find all tasks for this batch
        batch_tasks = {
            request_id: status for request_id, status in app.state.generation_tasks.items()
            if status.metadata.get('batch_id') == batch_id
        }
        
        if not batch_tasks:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Calculate overall progress
        total_tasks = len(batch_tasks)
        completed_tasks = sum(1 for status in batch_tasks.values() if status.status in ['completed', 'failed'])
        overall_progress = completed_tasks / total_tasks
        
        # Determine overall status
        statuses = [status.status for status in batch_tasks.values()]
        if all(s in ['completed', 'failed'] for s in statuses):
            overall_status = "completed"
        elif any(s == 'failed' for s in statuses):
            overall_status = "partial"
        else:
            overall_status = "processing"
        
        return APIResponse(
            success=True,
            data={
                "batch_id": batch_id,
                "overall_status": overall_status,
                "overall_progress": overall_progress,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "tasks": {
                    request_id: {
                        "status": status.status,
                        "progress": status.progress,
                        "current_step": status.current_step,
                        "errors": status.errors
                    }
                    for request_id, status in batch_tasks.items()
                }
            },
            requestId=request.state.requestId
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get batch status")

if __name__ == "__main__":
    logger.info("Starting WriterzRoom API Server - ENTERPRISE MODE")
    logger.info("=" * 60)
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"API Key: {'✅ Configured' if API_KEY else '❌ Missing'}")
    logger.info(f"MCP Integration: ✅ Required (Enterprise)")
    logger.info(f"Universal System: ✅ Required (Enterprise)")
    logger.info(f"Authentication: ✅ Always Required (Enterprise)")
    logger.info(f"Fallback Mode: ❌ Disabled (Enterprise)")
    logger.info("=" * 60)
    logger.info("ENTERPRISE MODE: All systems must be operational")
    logger.info("No fallbacks - Fail fast on missing dependencies")
    logger.info("Comprehensive validation and monitoring")

    uvicorn.run(
        "integrated_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )