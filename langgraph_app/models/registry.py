# src/langgraph_app/models/registry.py
"""
Centralized AI model registry for dynamic model selection.
Supports OpenAI and Anthropic with agent-specific optimizations.
"""
from __future__ import annotations

import os
import logging
from typing import Dict, Any, Literal
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..core.types import AgentType
from ..core.exceptions import AIModelError, ConfigurationError

logger = logging.getLogger(__name__)

ModelProvider = Literal["openai", "anthropic"]


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    provider: ModelProvider
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60


# Agent-specific model configurations
AGENT_MODEL_MAP: Dict[AgentType, ModelConfig] = {
    # Planner: Claude Sonnet (strategic reasoning)
    AgentType.PLANNER: ModelConfig(
        provider="anthropic",
        model_name="claude-sonnet-4-20250514",
        temperature=0.3,
        max_tokens=2000
    ),
    
    # Researcher: Claude Sonnet (analysis and synthesis)
    AgentType.RESEARCHER: ModelConfig(
        provider="anthropic",
        model_name="claude-sonnet-4-20250514",
        temperature=0.2,
        max_tokens=3000
    ),
    
    # Call Writer: GPT-4 (instruction synthesis)
    AgentType.CALL_WRITER: ModelConfig(
        provider="openai",
        model_name="gpt-4-turbo",
        temperature=0.5,
        max_tokens=2000
    ),
    
    # Writer: GPT-4 (creative content generation)
    AgentType.WRITER: ModelConfig(
        provider="openai",
        model_name="gpt-4-turbo",
        temperature=0.7,
        max_tokens=4000
    ),
    
    # Editor: Claude Opus (quality and precision)
    AgentType.EDITOR: ModelConfig(
        provider="anthropic",
        model_name="claude-opus-4-20250514",
        temperature=0.1,
        max_tokens=4000
    ),
    
    # Formatter: Deterministic (no LLM needed, but fallback available)
    AgentType.FORMATTER: ModelConfig(
        provider="openai",
        model_name="gpt-3.5-turbo",
        temperature=0.0,
        max_tokens=1000
    ),
    
    # SEO: Claude Sonnet (technical optimization)
    AgentType.SEO: ModelConfig(
        provider="anthropic",
        model_name="claude-sonnet-4-20250514",
        temperature=0.2,
        max_tokens=2000
    ),
    
    # Image: Stable for prompt generation
    AgentType.IMAGE: ModelConfig(
        provider="openai",
        model_name="gpt-4-turbo",
        temperature=0.8,
        max_tokens=500
    ),
    
    # Code: GPT-4 (technical code generation)
    AgentType.CODE: ModelConfig(
        provider="openai",
        model_name="gpt-4-turbo",
        temperature=0.2,
        max_tokens=3000
    ),
    
    # Publisher: Minimal processing
    AgentType.PUBLISHER: ModelConfig(
        provider="openai",
        model_name="gpt-3.5-turbo",
        temperature=0.0,
        max_tokens=500
    ),
}


def get_model_for_agent(
    agent_type: AgentType,
    override_config: Dict[str, Any] | None = None
) -> ChatOpenAI | ChatAnthropic:
    """
    Get the appropriate LLM for a specific agent type.
    
    Args:
        agent_type: The type of agent requesting the model
        override_config: Optional dict to override default settings
        
    Returns:
        Configured LangChain chat model instance
        
    Raises:
        AIModelError: If model initialization fails
        ConfigurationError: If API keys are missing
    """
    if agent_type not in AGENT_MODEL_MAP:
        raise AIModelError(f"No model configured for agent type: {agent_type}")
    
    config = AGENT_MODEL_MAP[agent_type]
    
    # Apply overrides if provided
    if override_config:
        config = ModelConfig(
            provider=override_config.get("provider", config.provider),
            model_name=override_config.get("model_name", config.model_name),
            temperature=override_config.get("temperature", config.temperature),
            max_tokens=override_config.get("max_tokens", config.max_tokens),
            timeout=override_config.get("timeout", config.timeout)
        )
    
    try:
        if config.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ConfigurationError("OPENAI_API_KEY environment variable not set")
            
            return ChatOpenAI(
                model=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                openai_api_key=api_key
            )
        
        elif config.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ConfigurationError("ANTHROPIC_API_KEY environment variable not set")
            
            return ChatAnthropic(
                model=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                anthropic_api_key=api_key
            )
        
        else:
            raise AIModelError(f"Unsupported model provider: {config.provider}")
    
    except Exception as e:
        logger.error(f"Failed to initialize model for {agent_type}: {e}")
        raise AIModelError(f"Model initialization failed: {e}") from e


def get_model_config(agent_type: AgentType) -> ModelConfig:
    """Get the model configuration for an agent without initializing the model."""
    if agent_type not in AGENT_MODEL_MAP:
        raise AIModelError(f"No model configured for agent type: {agent_type}")
    return AGENT_MODEL_MAP[agent_type]