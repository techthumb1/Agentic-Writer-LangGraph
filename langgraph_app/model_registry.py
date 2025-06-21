# Location: langgraph_app/model_registry.py
"""
Enhanced Model Registry with Multi-Provider Support and Failover
Supports OpenAI, Anthropic, and local models with automatic failover capabilities
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import time
from abc import ABC, abstractmethod

import openai
import anthropic
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_model(agent_name: str) -> str:
    """
    Returns the model name for a given agent.
    Priority: Environment variable > default fallback
    """
    default_models = {
        "writer": "gpt-4o",
        "editor": "gpt-4o-mini",
        "seo": "gpt-4o-mini",
        "image": "dall-e-3",
        "code": "gpt-4o",
        "researcher": "gpt-4o-mini",
    }

    env_key = f"{agent_name.upper()}_MODEL"
    return os.getenv(env_key, default_models.get(agent_name, "gpt-4o"))
class ModelProvider(Enum):
    """Enum for supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic" 
    LOCAL = "local"
    OLLAMA = "ollama"

class ModelTier(Enum):
    """Model performance tiers for automatic selection"""
    PREMIUM = "premium"      # GPT-4, Claude-3.5-Sonnet
    STANDARD = "standard"    # GPT-3.5, Claude-3-Haiku
    BUDGET = "budget"        # Local models, smaller variants

@dataclass
class ModelConfig:
    """Configuration for individual models"""
    name: str
    provider: ModelProvider
    tier: ModelTier
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    cost_per_1k_tokens: float = 0.0
    rate_limit_rpm: int = 60
    priority: int = 1  # Lower number = higher priority
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class ModelResponse:
    """Standardized response from any model provider"""
    content: str
    model_used: str
    provider: ModelProvider
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    latency: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseModelProvider(ABC):
    """Abstract base class for model providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider client"""
        pass
    
    @abstractmethod
    async def generate(self, messages: List[Dict], model_config: ModelConfig) -> ModelResponse:
        """Generate response using the provider"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy"""
        pass

class OpenAIProvider(BaseModelProvider):
    """OpenAI provider implementation"""
    
    async def initialize(self) -> bool:
        try:
            api_key = self.config.get('api_key') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("OpenAI API key not found")
                return False
            
            self.client = AsyncOpenAI(api_key=api_key)
            return await self.health_check()
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            return False
    
    async def generate(self, messages: List[Dict], model_config: ModelConfig) -> ModelResponse:
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=model_config.name,
                messages=messages,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                timeout=model_config.timeout
            )
            
            latency = time.time() - start_time
            tokens_used = response.usage.total_tokens if response.usage else None
            cost = (tokens_used / 1000 * model_config.cost_per_1k_tokens) if tokens_used else None
            
            return ModelResponse(
                content=response.choices[0].message.content,
                model_used=model_config.name,
                provider=ModelProvider.OPENAI,
                tokens_used=tokens_used,
                cost=cost,
                latency=latency,
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        try:
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False

class AnthropicProvider(BaseModelProvider):
    """Anthropic provider implementation"""
    
    async def initialize(self) -> bool:
        try:
            api_key = self.config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                logger.error("Anthropic API key not found")
                return False
            
            self.client = AsyncAnthropic(api_key=api_key)
            return await self.health_check()
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            return False
    
    async def generate(self, messages: List[Dict], model_config: ModelConfig) -> ModelResponse:
        start_time = time.time()
        
        try:
            # Convert OpenAI format to Anthropic format
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message += msg["content"] + "\n"
                else:
                    user_messages.append(msg)
            
            response = await self.client.messages.create(
                model=model_config.name,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                system=system_message.strip() if system_message else None,
                messages=user_messages
            )
            
            latency = time.time() - start_time
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = (tokens_used / 1000 * model_config.cost_per_1k_tokens) if tokens_used else None
            
            return ModelResponse(
                content=response.content[0].text,
                model_used=model_config.name,
                provider=ModelProvider.ANTHROPIC,
                tokens_used=tokens_used,
                cost=cost,
                latency=latency,
                metadata={"stop_reason": response.stop_reason}
            )
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        try:
            # Simple test message
            await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False

class EnhancedModelRegistry:
    """Enhanced model registry with multi-provider support and failover"""
    
    def __init__(self):
        self.providers: Dict[ModelProvider, BaseModelProvider] = {}
        self.models: Dict[str, ModelConfig] = {}
        self.provider_health: Dict[ModelProvider, bool] = {}
        self.last_health_check: Dict[ModelProvider, float] = {}
        self.health_check_interval = 300  # 5 minutes
        
        # Initialize default model configurations
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default model configurations"""
        default_models = [
            # OpenAI Models
            ModelConfig(
                name="gpt-4o",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.PREMIUM,
                max_tokens=4096,
                cost_per_1k_tokens=0.015,
                priority=1
            ),
            ModelConfig(
                name="gpt-4o-mini",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.STANDARD,
                max_tokens=4096,
                cost_per_1k_tokens=0.002,
                priority=2
            ),
            ModelConfig(
                name="gpt-3.5-turbo",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.BUDGET,
                max_tokens=4096,
                cost_per_1k_tokens=0.001,
                priority=3
            ),
            
            # Anthropic Models
            ModelConfig(
                name="claude-3-5-sonnet-20241022",
                provider=ModelProvider.ANTHROPIC,
                tier=ModelTier.PREMIUM,
                max_tokens=4096,
                cost_per_1k_tokens=0.015,
                priority=1
            ),
            ModelConfig(
                name="claude-3-haiku-20240307",
                provider=ModelProvider.ANTHROPIC,
                tier=ModelTier.STANDARD,
                max_tokens=4096,
                cost_per_1k_tokens=0.0025,
                priority=2
            ),
        ]
        
        for model in default_models:
            self.models[model.name] = model
    
    async def initialize_providers(self, provider_configs: Dict[str, Dict[str, Any]]):
        """Initialize all configured providers"""
        for provider_name, config in provider_configs.items():
            try:
                provider_enum = ModelProvider(provider_name.lower())
                
                if provider_enum == ModelProvider.OPENAI:
                    provider = OpenAIProvider(config)
                elif provider_enum == ModelProvider.ANTHROPIC:
                    provider = AnthropicProvider(config)
                else:
                    logger.warning(f"Unsupported provider: {provider_name}")
                    continue
                
                if await provider.initialize():
                    self.providers[provider_enum] = provider
                    self.provider_health[provider_enum] = True
                    self.last_health_check[provider_enum] = time.time()
                    logger.info(f"Successfully initialized {provider_name} provider")
                else:
                    logger.error(f"Failed to initialize {provider_name} provider")
                    
            except Exception as e:
                logger.error(f"Error initializing provider {provider_name}: {e}")
    
    async def _check_provider_health(self, provider: ModelProvider) -> bool:
        """Check and update provider health status"""
        current_time = time.time()
        last_check = self.last_health_check.get(provider, 0)
        
        # Skip if recently checked
        if current_time - last_check < self.health_check_interval:
            return self.provider_health.get(provider, False)
        
        if provider in self.providers:
            try:
                health = await self.providers[provider].health_check()
                self.provider_health[provider] = health
                self.last_health_check[provider] = current_time
                return health
            except Exception as e:
                logger.error(f"Health check failed for {provider}: {e}")
                self.provider_health[provider] = False
                return False
        
        return False
    
    def get_available_models(self, tier: Optional[ModelTier] = None, 
                           provider: Optional[ModelProvider] = None) -> List[ModelConfig]:
        """Get available models filtered by tier and/or provider"""
        models = []
        
        for model in self.models.values():
            if not model.enabled:
                continue
                
            if tier and model.tier != tier:
                continue
                
            if provider and model.provider != provider:
                continue
                
            # Check if provider is healthy
            if model.provider in self.provider_health:
                if not self.provider_health[model.provider]:
                    continue
            
            models.append(model)
        
        # Sort by priority (lower number = higher priority)
        return sorted(models, key=lambda x: x.priority)
    
    async def generate_with_fallback(self, 
                                   messages: List[Dict], 
                                   preferred_model: Optional[str] = None,
                                   tier: Optional[ModelTier] = None,
                                   max_retries: int = 3) -> ModelResponse:
        """Generate content with automatic fallback to other models"""
        
        # Get candidate models
        if preferred_model and preferred_model in self.models:
            candidates = [self.models[preferred_model]]
            # Add fallback models of same tier
            fallbacks = self.get_available_models(tier=self.models[preferred_model].tier)
            candidates.extend([m for m in fallbacks if m.name != preferred_model])
        else:
            candidates = self.get_available_models(tier=tier)
        
        if not candidates:
            raise Exception("No available models found")
        
        last_error = None
        
        for model_config in candidates:
            # Check provider health
            if not await self._check_provider_health(model_config.provider):
                logger.warning(f"Provider {model_config.provider} is unhealthy, skipping {model_config.name}")
                continue
            
            provider = self.providers.get(model_config.provider)
            if not provider:
                logger.warning(f"Provider {model_config.provider} not initialized")
                continue
            
            # Attempt generation with retries
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempting generation with {model_config.name} (attempt {attempt + 1})")
                    response = await provider.generate(messages, model_config)
                    logger.info(f"Successfully generated content with {model_config.name}")
                    return response
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"Generation failed with {model_config.name} (attempt {attempt + 1}): {e}")
                    
                    # Mark provider as unhealthy on repeated failures
                    if attempt == max_retries - 1:
                        self.provider_health[model_config.provider] = False
                    
                    # Wait before retry
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # All models failed
        raise Exception(f"All model attempts failed. Last error: {last_error}")
    
    def add_custom_model(self, model_config: ModelConfig):
        """Add a custom model configuration"""
        self.models[model_config.name] = model_config
        logger.info(f"Added custom model: {model_config.name}")
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_models": len(self.models),
            "enabled_models": len([m for m in self.models.values() if m.enabled]),
            "providers": list(self.providers.keys()),
            "provider_health": dict(self.provider_health),
            "models_by_tier": {
                tier.value: len([m for m in self.models.values() if m.tier == tier])
                for tier in ModelTier
            }
        }

# Example usage and configuration
async def example_usage():
    """Example of how to use the enhanced model registry"""
    
    # Initialize registry
    registry = EnhancedModelRegistry()
    
    # Configure providers
    provider_configs = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY")
        },
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY")
        }
    }
    
    # Initialize providers
    await registry.initialize_