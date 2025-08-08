# langgraph_app/schemas.py

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class MCPGenerationRequest(BaseModel):
    """MCP Generation Request Schema"""
    template: str = Field(..., min_length=1, max_length=100)
    style_profile: str = Field(..., min_length=1, max_length=100)
    dynamic_parameters: Dict[str, Any] = Field(default_factory=dict, max_items=50)
    priority: int = Field(default=1, ge=1, le=5)
    timeout_seconds: int = Field(default=300, ge=60, le=1800)
    enable_mcp: bool = Field(default=True)
    research_depth: str = Field(default="moderate", pattern=r'^(light|moderate|deep)$')


__all__ = ['MCPGenerationRequest']