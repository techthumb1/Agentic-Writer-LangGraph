# src/langgraph_app/agents/planner.py
"""Enterprise Planner Agent - LLM-driven with YAML constraints"""
from __future__ import annotations

import logging
import json
from typing import Dict, Any

from .base import BaseAgent
from ..core.state import EnrichedContentState
from ..core.types import AgentType, ContentSpec, GenerationStatus, ContentPhase, PlanningOutput
from ..core.exceptions import StateValidationError, AgentExecutionError
from ..core.model_factory import get_model_for_generation

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """LLM-driven planner using YAML as guidance constraints"""

    def __init__(self):
        super().__init__(AgentType.PLANNER)

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute LLM-based planning with YAML constraints"""
        try:
            self.log_execution_start(state)
            self.validate_state(state, ["template_config", "style_config"])
            
            # Ensure content_spec exists
            if not state.content_spec or not state.content_spec.topic:
                raise StateValidationError("ENTERPRISE: content_spec.topic required")

            # Validate template-style compatibility
            self._validate_compatibility(state)

            # Generate plan via LLM
            planning_output = self._llm_generate_planning(state)

            # Update state
            state.planning_output = planning_output
            state.research_plan = planning_output
            state.status = GenerationStatus.PLANNING
            state.update_phase(ContentPhase.RESEARCH)

            self.log_execution_complete(state, {
                "template_type": state.template_config.get("template_type"),
                "style_profile": state.style_config.get("id"),
                "strategy": planning_output.content_strategy,
                "confidence": planning_output.planning_confidence
            })

            return state
            
        except Exception as e:
            logger.error(f"Planner execution failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Planner failed: {e}") from e

    def _validate_compatibility(self, state: EnrichedContentState) -> None:
        """Validate template-style compatibility"""
        template_type = state.template_config.get("template_type")
        style_profile_id = state.style_config.get("id")

        if not template_type or not style_profile_id:
            raise StateValidationError("ENTERPRISE: template_type and style_profile.id required")

        logger.info(f"Template-style validated: {template_type} + {style_profile_id}")

    def _llm_generate_planning(self, state: EnrichedContentState) -> PlanningOutput:
        """Generate planning via LLM with YAML constraints"""
        
        # Build constraint-based prompt
        system_prompt = self._build_system_prompt(state)
        user_prompt = self._build_user_prompt(state)
        
        # Get model for planning
        model = get_model_for_generation("planner", state.template_config.get("generation_settings", {}))
        
        # Call LLM
        try:
            response = model.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,  # Lower for structured output
                max_tokens=2000
            )
            
            # Parse structured JSON response
            planning_data = json.loads(response)
            
            return PlanningOutput(
                content_strategy=planning_data["content_strategy"],
                structure_approach=planning_data["structure_approach"],
                key_messages=planning_data["key_messages"],
                research_priorities=planning_data["research_priorities"],
                audience_insights=planning_data["audience_insights"],
                competitive_positioning=planning_data["competitive_positioning"],
                success_metrics=planning_data["success_metrics"],
                estimated_sections=planning_data["estimated_sections"],
                planning_confidence=planning_data.get("planning_confidence", 0.85)
            )
            
        except json.JSONDecodeError as e:
            raise AgentExecutionError(f"LLM returned invalid JSON: {e}")
        except KeyError as e:
            raise AgentExecutionError(f"LLM response missing required field: {e}")

    def _build_system_prompt(self, state: EnrichedContentState) -> str:
        """Build system prompt with style guidance"""
        style_config = state.style_config
        
        return f"""You are an expert content strategist and planner.

STYLE PROFILE: {style_config.get('name')}
- Tone: {style_config.get('tone')}
- Voice: {style_config.get('voice')}
- Audience: {style_config.get('audience')}
- Platform: {style_config.get('platform')}

{style_config.get('system_prompt', '')}

Generate a comprehensive content plan that adheres to these constraints.
Output ONLY valid JSON matching the exact schema provided in the user prompt."""

    def _build_user_prompt(self, state: EnrichedContentState) -> str:
        """Build user prompt with template constraints and schema"""
        template_config = state.template_config
        content_spec = state.content_spec
        
        # Extract constraints from YAML
        constraints = self._extract_constraints(template_config)
        
        return f"""Create a detailed content plan for the following:

TOPIC: {content_spec.topic}
TEMPLATE TYPE: {template_config.get('template_type')}
DESCRIPTION: {template_config.get('description')}

TEMPLATE CONSTRAINTS:
{self._format_constraints(constraints)}

REQUIRED OUTPUT (valid JSON only):
{{
  "content_strategy": "string - strategic approach tailored to topic and template",
  "structure_approach": "string - how content will be organized",
  "key_messages": ["string", "string", ...] - 3-5 core messages,
  "research_priorities": ["string", "string", ...] - 4-6 research focus areas,
  "audience_insights": {{
    "primary_audience": "string",
    "complexity_level": "string",
    "platform": "string",
    "style_category": "string"
  }},
  "competitive_positioning": "string - unique angle or approach",
  "success_metrics": {{
    "metric_name": 0.0
  }},
  "estimated_sections": [
    {{"name": "string", "estimated_words": number}},
    ...
  ],
  "planning_confidence": 0.0 - float between 0.7-0.99
}}

Generate the plan now. Output ONLY the JSON object."""

    def _extract_constraints(self, template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract guidance constraints from template YAML"""
        return {
            "parameters": template_config.get("parameters", {}),
            "requirements": template_config.get("requirements", {}),
            "output": template_config.get("output", {}),
            "style_specs": template_config.get("style", {}),
            "metadata": template_config.get("metadata", {})
        }

    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraints for prompt"""
        lines = []
        
        if constraints.get("requirements"):
            lines.append("REQUIREMENTS:")
            for key, value in constraints["requirements"].items():
                lines.append(f"  - {key}: {value}")
        
        if constraints.get("output"):
            lines.append("\nOUTPUT SPECIFICATIONS:")
            for key, value in constraints["output"].items():
                lines.append(f"  - {key}: {value}")
        
        if constraints.get("metadata"):
            meta = constraints["metadata"]
            if meta.get("complexity"):
                lines.append(f"\nCOMPLEXITY LEVEL: {meta['complexity']}")
            if meta.get("target_audience"):
                lines.append(f"TARGET AUDIENCE: {meta['target_audience']}")
        
        return "\n".join(lines)