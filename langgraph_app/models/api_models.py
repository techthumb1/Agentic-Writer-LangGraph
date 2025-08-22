# langgraph_app/models/api_models.py
"""
Pydantic models for API requests and responses
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator

# Core API Models
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    requestId: Optional[str] = None

class PaginationMetadata(BaseModel):
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
    totalPages: int = Field(..., ge=0)
    hasNext: bool
    hasPrev: bool

# Template Models
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

# Generation Models
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

# MCP Models
class MCPGenerationRequest(BaseModel):
    template: str = Field(..., min_length=1, max_length=100)
    style_profile: str = Field(..., min_length=1, max_length=100)
    dynamic_parameters: Dict[str, Any] = Field(default_factory=dict)
    enable_mcp: bool = Field(default=True)
    research_depth: str = Field(default="moderate", pattern=r'^(light|moderate|comprehensive)$')
    memory_namespace: Optional[str] = Field(None, max_length=100)
    timeout_seconds: int = Field(default=300, ge=60, le=1800)
    priority: int = Field(default=1, ge=1, le=5)

# Content Management Models
class ContentItem(BaseModel):
    id: str
    title: str
    content: str = Field(default="")
    contentHtml: Optional[str] = None
    status: str = Field(pattern=r'^(draft|published|archived)$')
    type: str = Field(default="article")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    views: int = Field(default=0)
    author: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    week: Optional[str] = None

class ContentUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    status: str = Field(default="draft", pattern=r'^(draft|published|archived)$')

# Analytics Models
class AnalyticsOverview(BaseModel):
    total_content: int = Field(default=0)
    total_views: int = Field(default=0)
    content_by_week: Dict[str, int] = Field(default_factory=dict)
    content_by_type: Dict[str, int] = Field(default_factory=dict)
    content_by_status: Dict[str, int] = Field(default_factory=dict)
    top_content: List[Dict[str, Any]] = Field(default_factory=list)
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)

# Health Check Models
class HealthResponse(BaseModel):
    status: str = Field(..., pattern=r'^(healthy|degraded|unhealthy|error)$')
    timestamp: datetime
    version: str = Field(default="2.0.0-enterprise")
    environment: str
    services: Optional[Dict[str, bool]] = None
    metrics: Optional[Dict[str, Any]] = None
    system: Optional[Dict[str, Any]] = None

# Batch Operation Models
class BatchGenerateRequest(BaseModel):
    requests: List[GenerateRequest] = Field(..., min_items=1, max_items=10)

class BatchStatus(BaseModel):
    batch_id: str
    overall_status: str = Field(..., pattern=r'^(pending|processing|completed|partial|failed)$')
    overall_progress: float = Field(..., ge=0.0, le=1.0)
    total_tasks: int
    completed_tasks: int
    tasks: Dict[str, Dict[str, Any]]

# Search Models
class SearchRequest(BaseModel):
    q: str = Field(..., min_length=1, max_length=200)
    type: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)

class SearchResult(BaseModel):
    id: str
    title: str
    type: str
    status: str
    created_at: str
    snippet: str = Field(default="")
    week: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
    limit: int