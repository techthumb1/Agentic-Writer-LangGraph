# src/langgraph_app/core/model_registry.py
"""
SOTA October 2025 Multi-Provider Model Registry
Intelligent routing between OpenAI and Anthropic based on task characteristics
"""
from __future__ import annotations

import os
import logging
from typing import Dict, Any, Protocol, List, Optional
from dataclasses import dataclass
from enum import Enum

import openai
import anthropic

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class ModelCapability(Enum):
    """Model capability categories"""
    REASONING = "reasoning"
    CREATIVITY = "creativity"
    ANALYSIS = "analysis"
    STRUCTURED_OUTPUT = "structured_output"
    LONG_CONTEXT = "long_context"
    SPEED = "speed"
    AGENTIC = "agentic"  # New: For multi-step autonomous tasks
    CODING = "coding"     # New: For code generation tasks


@dataclass
class ModelSpec:
    """Model specification with capabilities"""
    provider: ModelProvider
    model_name: str
    capabilities: List[ModelCapability]
    max_tokens: int
    context_window: int
    cost_per_1k_tokens: float
    
    def matches_requirements(self, required_capabilities: List[ModelCapability]) -> bool:
        """Check if model has required capabilities"""
        return all(cap in self.capabilities for cap in required_capabilities)


# SOTA Model Specifications (October 2025)
MODEL_SPECS = {
    # ========================================================================
    # OpenAI GPT-5 Family (Released August 2025)
    # ========================================================================
    "gpt-5": ModelSpec(
        provider=ModelProvider.OPENAI,
        model_name="gpt-5",
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.CREATIVITY,
            ModelCapability.ANALYSIS,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.LONG_CONTEXT,
            ModelCapability.AGENTIC,
            ModelCapability.CODING
        ],
        max_tokens=16384,
        context_window=128000,
        cost_per_1k_tokens=2.50  # $2.50 input / $10.00 output
    ),
    "gpt-5-mini": ModelSpec(
        provider=ModelProvider.OPENAI,
        model_name="gpt-5-mini",
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.CREATIVITY,
            ModelCapability.ANALYSIS,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.SPEED,
            ModelCapability.AGENTIC
        ],
        max_tokens=16384,
        context_window=128000,
        cost_per_1k_tokens=0.15  # $0.15 input / $0.60 output
    ),
    "gpt-5-nano": ModelSpec(
        provider=ModelProvider.OPENAI,
        model_name="gpt-5-nano",
        capabilities=[
            ModelCapability.SPEED,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.REASONING
        ],
        max_tokens=16384,
        context_window=128000,
        cost_per_1k_tokens=0.04  # $0.04 input / $0.16 output
    ),
    "gpt-5-pro": ModelSpec(
        provider=ModelProvider.OPENAI,
        model_name="gpt-5-pro",
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.LONG_CONTEXT,
            ModelCapability.AGENTIC,
            ModelCapability.CODING
        ],
        max_tokens=16384,
        context_window=128000,
        cost_per_1k_tokens=15.00  # $15 input / $60 output (extended reasoning)
    ),
    
    # ========================================================================
    # OpenAI Legacy (Maintained for compatibility)
    # ========================================================================
    "gpt-4.1": ModelSpec(
        provider=ModelProvider.OPENAI,
        model_name="gpt-4.1",
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.LONG_CONTEXT
        ],
        max_tokens=4096,
        context_window=128000,
        cost_per_1k_tokens=2.50
    ),
    "gpt-4o": ModelSpec(
        provider=ModelProvider.OPENAI,
        model_name="gpt-4o",
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.CREATIVITY,
            ModelCapability.ANALYSIS,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.SPEED
        ],
        max_tokens=4096,
        context_window=128000,
        cost_per_1k_tokens=0.005
    ),
    
    # ========================================================================
    # Anthropic Claude 4 Family (Released May-October 2025)
    # ========================================================================
    "claude-sonnet-4.5": ModelSpec(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-sonnet-4-5-20250929",
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.CREATIVITY,
            ModelCapability.ANALYSIS,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.LONG_CONTEXT,
            ModelCapability.AGENTIC,
            ModelCapability.CODING
        ],
        max_tokens=8192,
        context_window=200000,  # 1M with beta header
        cost_per_1k_tokens=3.00  # $3 input / $15 output
    ),
    "claude-opus-4.1": ModelSpec(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-opus-4-1-20250514",
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.CREATIVITY,
            ModelCapability.LONG_CONTEXT,
            ModelCapability.AGENTIC,
            ModelCapability.CODING
        ],
        max_tokens=4096,
        context_window=200000,
        cost_per_1k_tokens=15.00  # $15 input / $75 output
    ),
    "claude-haiku-4.5": ModelSpec(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-haiku-4-5-20251015",
        capabilities=[
            ModelCapability.SPEED,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.REASONING,
            ModelCapability.CODING
        ],
        max_tokens=8192,
        context_window=200000,
        cost_per_1k_tokens=1.00  # $1 input / $5 output
    ),
    "claude-sonnet-4": ModelSpec(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-sonnet-4-20250514",
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.CREATIVITY,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.SPEED,
            ModelCapability.LONG_CONTEXT
        ],
        max_tokens=4096,
        context_window=200000,
        cost_per_1k_tokens=3.00
    ),
    "claude-haiku-3.5": ModelSpec(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-3-5-haiku-20241022",
        capabilities=[
            ModelCapability.SPEED,
            ModelCapability.STRUCTURED_OUTPUT
        ],
        max_tokens=8192,
        context_window=200000,
        cost_per_1k_tokens=0.80  # $0.80 input / $4 output
    )
}


class ModelInterface(Protocol):
    """Unified model interface across providers"""
    provider: ModelProvider
    model_name: str
    spec: ModelSpec
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 10000,
        **kwargs
    ) -> str:
        """Generate response"""
        ...
    
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Dict[str, Any],
        temperature: float = 0.3,
        max_tokens: int = 10000
    ) -> Dict[str, Any]:
        """Generate structured JSON response"""
        ...


@dataclass
class OpenAIModel:
    """OpenAI model wrapper"""
    provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = "gpt-5"
    spec: ModelSpec = None
    client: openai.OpenAI = None
    
    def __post_init__(self):
        if not self.client:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("ENTERPRISE: OPENAI_API_KEY required")
            self.client = openai.OpenAI(api_key=api_key)
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 10000,
        **kwargs
    ) -> str:
        """Generate response using OpenAI"""
        try:
            token_param = (
                "max_completion_tokens" if self.model_name.startswith("gpt-5")
                else "max_tokens"
            )

            # GPT-5 only supports temperature=1.0
            actual_temp = 1.0 if self.model_name.startswith("gpt-5") else temperature
            
            # CRITICAL: GPT-5 requires minimum 10000 tokens for complex prompts with research
            if self.model_name.startswith("gpt-5"):
                actual_max_tokens = max(10000, max_tokens)
                logger.info(f"GPT-5 token enforcement: {max_tokens} → {actual_max_tokens}")
            else:
                actual_max_tokens = max_tokens

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=actual_temp,
                **{token_param: actual_max_tokens},
                **kwargs
            )
            
            content = response.choices[0].message.content
            
            # Debug logging
            logger.error(f"🔍 OpenAI - model: {self.model_name}, "
                        f"finish_reason: {response.choices[0].finish_reason}, "
                        f"content: {repr(content)[:100]}, "
                        f"length: {len(content) if content else 0}")
            
            if content is None:
                logger.error(f"Full response: {response.model_dump()}")
                raise ValueError(f"ENTERPRISE: {self.model_name} returned None")
            
            if not content.strip():
                logger.error(f"Empty content. Prompt lengths - system: {len(system_prompt)}, user: {len(user_prompt)}")
                raise ValueError(f"ENTERPRISE: Empty from {self.model_name}")
            
            return content.strip()
            
        except openai.APIError as e:
            raise RuntimeError(f"ENTERPRISE: OpenAI API error: {e}")
    
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Dict[str, Any],
        temperature: float = 0.3,
        max_tokens: int = 10000
    ) -> Dict[str, Any]:
        """Generate structured JSON using response_format"""
        import json
        token_param = (
            "max_completion_tokens" if self.model_name.startswith("gpt-5")
            else "max_tokens"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                **{token_param: max_tokens},
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except (openai.APIError, json.JSONDecodeError) as e:
            raise RuntimeError(f"ENTERPRISE: OpenAI structured generation failed: {e}")

@dataclass
class AnthropicModel:
    """Anthropic model wrapper"""
    provider: ModelProvider = ModelProvider.ANTHROPIC
    model_name: str = "claude-sonnet-4-5-20250929"
    spec: ModelSpec = None
    client: anthropic.Anthropic = None
    
    def __post_init__(self):
        if not self.client:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError("ENTERPRISE: ANTHROPIC_API_KEY required")
            self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 10000,
        **kwargs
    ) -> str:
        """Generate response using Anthropic"""
        try:
            # Anthropic uses messages API
            response = self.client.messages.create(
                model=self.model_name,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            content = response.content[0].text

            # Debug logging
            logger.info(f"Anthropic response - model: {self.model_name}, "
                        f"stop_reason: {response.stop_reason}, "
                        f"content_type: {type(content)}, "
                        f"content_length: {len(content) if content else 0}")

            if content is None:
                logger.error(f"Response object: {response}")
                raise ValueError(f"ENTERPRISE: {self.model_name} returned None")

            if not content.strip():
                logger.error(f"Empty content. Prompt lengths - system: {len(system_prompt)}, user: {len(user_prompt)}")
                raise ValueError(f"ENTERPRISE: Empty response from {self.model_name}")

            return content.strip()
            
        except anthropic.APIError as e:
            raise RuntimeError(f"ENTERPRISE: Anthropic API error: {e}")
    
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Dict[str, Any],
        temperature: float = 0.3,
        max_tokens: int = 10000
    ) -> Dict[str, Any]:
        """Generate structured JSON using prompt engineering"""
        import json
        import re
        
        enhanced_prompt = f"""{user_prompt}

CRITICAL: Output ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Output the JSON object now with no additional text."""
        
        try:
            response = self.generate(
                system_prompt=system_prompt,
                user_prompt=enhanced_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            return json.loads(json_match.group(0))
            
        except (json.JSONDecodeError, ValueError) as e:
            raise RuntimeError(f"ENTERPRISE: Anthropic structured generation failed: {e}")


def get_optimal_model(
    task_type: str,
    template_config: Dict[str, Any],
    user_preferences: Optional[Dict[str, Any]] = None
) -> ModelInterface:
    """
    SOTA intelligent model selection based on task characteristics.
    
    Selection criteria:
    1. Task complexity (template metadata)
    2. Required capabilities
    3. User preferences (cost vs quality)
    4. Context length requirements
    
    Returns optimal model instance.
    """
    # Extract task requirements
    requirements = _analyze_task_requirements(task_type, template_config)
    
    # Get user preferences
    preferences = user_preferences or {}
    priority = preferences.get("priority", "balanced")  # quality, speed, cost, balanced
    
    # Filter models by capabilities
    candidate_models = [
        (key, spec) for key, spec in MODEL_SPECS.items()
        if spec.matches_requirements(requirements["capabilities"])
    ]
    
    if not candidate_models:
        raise ValueError(f"ENTERPRISE: No models available with required capabilities: {requirements['capabilities']}")
    
    # Select based on priority
    selected_key, selected_spec = _select_by_priority(candidate_models, priority, requirements)
    
    # Instantiate model
    if selected_spec.provider == ModelProvider.OPENAI:
        model = OpenAIModel(model_name=selected_spec.model_name, spec=selected_spec)
    else:
        model = AnthropicModel(model_name=selected_spec.model_name, spec=selected_spec)
    
    logger.info(f"Model selection: {task_type} -> {selected_key} ({selected_spec.provider.value})")
    
    return model


def _analyze_task_requirements(task_type: str, template_config: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze task to determine required model capabilities"""
    requirements = {
        "capabilities": [],
        "complexity": template_config.get("metadata", {}).get("complexity", 5),
        "context_length": 0
    }
    
    # Determine capabilities by task type
    if task_type == "planner":
        requirements["capabilities"] = [
            ModelCapability.REASONING,
            ModelCapability.STRUCTURED_OUTPUT,
            ModelCapability.AGENTIC
        ]
        if requirements["complexity"] > 7:
            requirements["capabilities"].append(ModelCapability.ANALYSIS)
    
    elif task_type == "researcher":
        requirements["capabilities"] = [
            ModelCapability.ANALYSIS,
            ModelCapability.REASONING,
            ModelCapability.AGENTIC
        ]
        if template_config.get("real_time_support", {}).get("enabled"):
            requirements["capabilities"].append(ModelCapability.LONG_CONTEXT)
    
    elif task_type == "writer":
        requirements["capabilities"] = [ModelCapability.CREATIVITY]
        
        template_type = template_config.get("template_type", "")
        if "creative" in template_type or "social" in template_type:
            requirements["capabilities"].append(ModelCapability.CREATIVITY)
        if "technical" in template_type or "analysis" in template_type:
            requirements["capabilities"].append(ModelCapability.REASONING)
        if "code" in template_type:
            requirements["capabilities"].append(ModelCapability.CODING)
        
        # Check context length needs
        estimated_words = sum(
            section.get("estimated_words", 0) 
            for section in template_config.get("structure", {}).get("sections", [])
        )
        requirements["context_length"] = estimated_words * 2  # tokens ~ 2x words
    
    elif task_type == "editor":
        requirements["capabilities"] = [
            ModelCapability.ANALYSIS,
            ModelCapability.REASONING
        ]
    
    elif task_type == "code":
        requirements["capabilities"] = [
            ModelCapability.CODING,
            ModelCapability.REASONING,
            ModelCapability.STRUCTURED_OUTPUT
        ]
    
    return requirements


def _select_by_priority(
    candidates: List[tuple[str, ModelSpec]],
    priority: str,
    requirements: Dict[str, Any]
) -> tuple[str, ModelSpec]:
    """Select model based on user priority"""
    
    if priority == "quality":
        # Select most capable (GPT-5 or Claude Sonnet 4.5)
        # Prefer models with AGENTIC + CODING capabilities
        premium = [
            (k, s) for k, s in candidates
            if ModelCapability.AGENTIC in s.capabilities and
               ModelCapability.CODING in s.capabilities
        ]
        if premium:
            return max(premium, key=lambda x: x[1].context_window)
        return max(candidates, key=lambda x: x[1].cost_per_1k_tokens)
    
    elif priority == "speed":
        # Select fastest model (nano, haiku variants)
        speed_models = [
            (k, s) for k, s in candidates 
            if ModelCapability.SPEED in s.capabilities
        ]
        if speed_models:
            return min(speed_models, key=lambda x: x[1].cost_per_1k_tokens)
        return candidates[0]
    
    elif priority == "cost":
        # Select cheapest capable model
        return min(candidates, key=lambda x: x[1].cost_per_1k_tokens)
    
    else:  # balanced
        # Balance cost and capability
        complexity = requirements["complexity"]
        
        if complexity >= 8:
            # High complexity: use top-tier models (GPT-5, Claude Sonnet 4.5)
            top_tier = [
                (k, s) for k, s in candidates 
                if s.cost_per_1k_tokens >= 2.50 and
                   ModelCapability.AGENTIC in s.capabilities
            ]
            return top_tier[0] if top_tier else candidates[0]
        
        elif complexity <= 3:
            # Low complexity: use efficient models (nano, haiku)
            efficient = [
                (k, s) for k, s in candidates 
                if ModelCapability.SPEED in s.capabilities or
                   s.cost_per_1k_tokens < 1.00
            ]
            return efficient[0] if efficient else candidates[0]
        
        else:
            # Medium complexity: use balanced models (mini, haiku 4.5)
            mid_tier = [
                (k, s) for k, s in candidates 
                if 0.15 <= s.cost_per_1k_tokens <= 3.00
            ]
            return mid_tier[0] if mid_tier else candidates[0]