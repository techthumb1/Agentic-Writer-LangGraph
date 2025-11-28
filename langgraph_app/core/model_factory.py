# src/langgraph_app/core/model_factory.py
"""
Model factory for dynamic LLM selection.
Enterprise-grade model routing with no fallback failures.
"""
from __future__ import annotations

import os
import logging
from typing import Dict, Any, Protocol
from dataclasses import dataclass

import openai

logger = logging.getLogger(__name__)


class ModelInterface(Protocol):
    """Expected model interface"""
    model_name: str
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """Generate response from LLM"""
        ...


@dataclass
class OpenAIModel:
    """OpenAI model wrapper"""
    model_name: str
    client: openai.OpenAI
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError(f"ENTERPRISE: {self.model_name} returned empty response")
            
            return content
            
        except openai.APIError as e:
            raise RuntimeError(f"ENTERPRISE: OpenAI API error: {e}")
        except Exception as e:
            raise RuntimeError(f"ENTERPRISE: Model generation failed: {e}")


# Agent-specific model configurations
AGENT_MODEL_CONFIGS = {
    "planner": {
        "preferred": "gpt-4-turbo-preview",
        "temperature": 0.3,  # Lower for structured output
        "max_tokens": 4000
    },
    "researcher": {
        "preferred": "gpt-4-turbo-preview",
        "temperature": 0.5,
        "max_tokens": 4000
    },
    "writer": {
        "preferred": "gpt-4-turbo-preview",
        "temperature": 0.7,
        "max_tokens": 4000
    },
    "editor": {
        "preferred": "gpt-4-turbo-preview",
        "temperature": 0.4,
        "max_tokens": 4000
    }
}


def get_model_for_generation(agent_type: str, settings: Dict[str, Any] = None) -> ModelInterface:
    """
    Get model instance for agent type.
    
    Args:
        agent_type: "planner", "researcher", "writer", "editor"
        settings: Optional template generation_settings override
    
    Returns:
        Model instance with generate() method
    
    Raises:
        RuntimeError: If API key missing or model unavailable
    """
    settings = settings or {}
    
    # Validate API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("ENTERPRISE: OPENAI_API_KEY environment variable required")
    
    # Get agent config
    agent_config = AGENT_MODEL_CONFIGS.get(agent_type)
    if not agent_config:
        raise ValueError(f"ENTERPRISE: Unknown agent_type '{agent_type}'")
    
    # Determine model (settings override > agent default)
    model_name = settings.get("model", agent_config["preferred"])
    
    # Validate model
    if not model_name:
        raise ValueError(f"ENTERPRISE: No model specified for {agent_type}")
    
    # Create OpenAI client and model
    client = openai.OpenAI(api_key=api_key)
    model = OpenAIModel(model_name=model_name, client=client)
    
    logger.info(f"Model factory: {agent_type} -> {model_name}")
    
    return model


def get_default_model() -> ModelInterface:
    """Get default model for general use"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("ENTERPRISE: OPENAI_API_KEY required")
    
    client = openai.OpenAI(api_key=api_key)
    return OpenAIModel(model_name="gpt-4-turbo-preview", client=client)