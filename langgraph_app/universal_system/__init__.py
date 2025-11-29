# langgraph_app/universal_system/__init__.py
"""
Universal Dynamic Template System for WriterzRoom

This system replaces rigid YAML templates with AI-powered dynamic content generation
that adapts to ANY topic - from AI/ML to gardening to politics to cooking.

Key Components:
- UniversalDynamicGenerator: Analyzes requests and generates custom templates
- UniversalTemplateManager: Manages both static and dynamic templates
- LangGraphUniversalIntegration: Integrates with existing LangGraph workflow

Usage:
    from langgraph_app.universal_system import LangGraphUniversalIntegration
    
    integration = LangGraphUniversalIntegration()
    result = await integration.process_content_request(
        user_request="I want to write about machine learning optimization",
        user_context={"expertise_level": "intermediate"}
    )
"""

from .universal_dynamic_generator import (
    UniversalContentRequest,
    UniversalDynamicGenerator, 
    TrulyDynamicContentSystem
)

from .universal_template_system import (
    ContentGenerationPayload,
    UniversalTemplateManager,
    LangGraphUniversalIntegration
)

__all__ = [
    'UniversalContentRequest',
    'UniversalDynamicGenerator',
    'TrulyDynamicContentSystem', 
    'ContentGenerationPayload',
    'UniversalTemplateManager',
    'LangGraphUniversalIntegration'
]

__version__ = "1.0.0"