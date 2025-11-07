# src/langgraph_app/core/exceptions.py
"""
Enterprise-grade exception hierarchy for WriterzRoom.
All exceptions inherit from WriterzRoomError for centralized handling.
"""
from __future__ import annotations


class WriterzRoomError(Exception):
    """Base exception for all WriterzRoom errors."""
    pass


class StateValidationError(WriterzRoomError):
    """Raised when agent receives invalid or incomplete state."""
    pass


class AgentExecutionError(WriterzRoomError):
    """Raised when an agent fails during execution."""
    pass


class TemplateValidationError(WriterzRoomError):
    """Raised when template YAML validation fails."""
    pass


class StyleProfileValidationError(WriterzRoomError):
    """Raised when style profile YAML validation fails."""
    pass


class MCPToolError(WriterzRoomError):
    """Raised when MCP tool execution fails."""
    pass


class AIModelError(WriterzRoomError):
    """Raised when AI model (OpenAI/Anthropic) call fails."""
    pass


class ContentQualityError(WriterzRoomError):
    """Raised when generated content fails quality checks."""
    pass


class ConfigurationError(WriterzRoomError):
    """Raised when system configuration is invalid."""
    pass