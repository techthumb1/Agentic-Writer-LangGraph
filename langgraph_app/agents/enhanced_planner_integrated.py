# langgraph_app/agents/enhanced_planner_integrated.py
# FIXED: Replaced generic logic with direct YAML extraction for deterministic planning.

import logging
from typing import Dict, Any, List
from langgraph_app.core.state import (
    EnrichedContentState,
    ContentSpec,
    GenerationStatus,
    ContentPhase,
    PlanningOutput,
    AgentType
)

logger = logging.getLogger(__name__)

class EnhancedPlannerAgent:
    """Enterprise Planner Agent - Pure YAML-driven extraction"""

    def __init__(self):
        self.name = "planner"
        self.agent_type = AgentType.PLANNER

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute planning using pure YAML extraction"""

        # Ensure content_spec exists for all environments
        if not hasattr(state, 'content_spec') or not state.content_spec or not state.content_spec.topic:
            topic = (state.template_config.get("dynamic_parameters", {})
                     .get("dynamic_overrides", {})
                     .get("topic", "No Topic Provided"))
            if topic == "No Topic Provided":
                 raise RuntimeError("ENTERPRISE: Planner requires a topic in template_config or content_spec.")

            state.content_spec = ContentSpec(topic=topic)
            logger.info("PLANNER: Created content_spec from template_config topic")

        # ENTERPRISE: Validate template-style compatibility
        self._validate_template_style_compatibility(state)

        # Extract all data from YAML configurations
        planning_output = self._extract_planning_from_yaml(state)

        # Update state
        state.planning_output = planning_output
        # The 'research_plan' attribute is deprecated in favor of 'planning_output' but kept for compatibility.
        state.research_plan = planning_output
        state.status = GenerationStatus.PLANNING
        state.update_phase(ContentPhase.RESEARCH)

        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "template_type": state.template_config.get("template_type"),
            "style_profile": state.style_config.get("id"),
            "strategy": planning_output.content_strategy,
            "confidence": planning_output.planning_confidence
        })

        return state

    def _validate_template_style_compatibility(self, state: EnrichedContentState) -> None:
        """Validate compatibility and block incompatible combinations"""
        from langgraph_app.template_style_validator import validate_template_style_match

        template_type = state.template_config.get("template_type")
        style_profile_id = state.style_config.get("id")

        if not template_type or not style_profile_id:
            raise RuntimeError("ENTERPRISE: template_type and style_profile.id are required for validation.")

        result = validate_template_style_match(template_type, style_profile_id)

        if not result.compatible:
            raise RuntimeError(f"ENTERPRISE: Incompatible combination blocked: Template '{template_type}' with Style '{style_profile_id}'. Reason: {result.reason}")

        logger.info(f"Template-style validated: {template_type} + {style_profile_id}")

    def _extract_planning_from_yaml(self, state: EnrichedContentState) -> PlanningOutput:
        """Extract all planning data directly from YAML configurations"""
        template_config = state.template_config
        style_config = state.style_config
        dynamic_params = state.dynamic_parameters or {}

        # Extract values directly from the validated configs
        content_strategy = self._extract_content_strategy(template_config, style_config, dynamic_params)
        structure_approach = self._extract_structure_approach(template_config)
        key_messages = self._extract_key_messages(template_config)
        research_priorities = self._extract_research_priorities(template_config)
        estimated_sections = self._extract_sections(template_config)

        return PlanningOutput(
            content_strategy=content_strategy,
            structure_approach=structure_approach,
            key_messages=key_messages,
            research_priorities=research_priorities,
            audience_insights=self._extract_audience_insights(template_config, style_config, dynamic_params),
            competitive_positioning=self._extract_positioning(template_config, style_config),
            success_metrics=self._extract_success_metrics(template_config),
            estimated_sections=estimated_sections,
            planning_confidence=0.98  # High confidence for deterministic YAML-driven planning
        )

    def _extract_content_strategy(self, template_config: Dict, style_config: Dict, dynamic_params: Dict) -> str:
        """Extract content strategy from template metadata."""
        strategy = template_config.get("metadata", {}).get("strategy")
        if not strategy:
             raise RuntimeError(f"ENTERPRISE: Template '{template_config.get('id')}' must define a 'strategy' in its metadata.")
        return strategy

    def _extract_structure_approach(self, template_config: Dict) -> str:
        """Extract structure approach from template configuration."""
        structure = template_config.get("structure", {})
        approach = structure.get("approach")
        if not approach:
            raise RuntimeError(f"ENTERPRISE: Template '{template_config.get('id')}' must define an 'approach' in its structure.")
        return approach

    def _extract_key_messages(self, template_config: Dict) -> List[str]:
        """Extract key messages from template requirements."""
        messages = template_config.get("requirements", {}).get("key_messages")
        if not messages or not isinstance(messages, list):
            raise RuntimeError(f"ENTERPRISE: Template '{template_config.get('id')}' must define 'key_messages' as a list in its requirements.")
        return messages

    def _extract_research_priorities(self, template_config: Dict) -> List[str]:
        """Extract research priorities from template research configuration."""
        priorities = template_config.get("research", {}).get("priorities")
        if not priorities or not isinstance(priorities, list):
            raise RuntimeError(f"ENTERPRISE: Template '{template_config.get('id')}' must define 'priorities' as a list in its research section.")
        return priorities

    def _extract_sections(self, template_config: Dict) -> List[Dict[str, Any]]:
        """Extract sections directly from template configuration."""
        sections = template_config.get("structure", {}).get("sections")
        if not sections or not isinstance(sections, list):
            raise RuntimeError(f"ENTERPRISE: Template '{template_config.get('id')}' must define 'sections' as a list in its structure.")
        
        # Ensure sections are in the correct format
        formatted_sections = []
        for section in sections:
            if isinstance(section, str):
                formatted_sections.append({"name": section, "estimated_words": 300})
            elif isinstance(section, dict) and "name" in section:
                formatted_sections.append(section)
            else:
                 raise RuntimeError(f"ENTERPRISE: Invalid section format in template '{template_config.get('id')}'.")
        return formatted_sections

    def _extract_audience_insights(self, template_config: Dict, style_config: Dict, dynamic_params: Dict) -> Dict[str, Any]:
        """Extract audience insights from configurations."""
        audience = style_config.get("audience")
        if not audience:
            raise RuntimeError(f"ENTERPRISE: Style profile '{style_config.get('id')}' must define an 'audience'.")
        return {
            "primary_audience": audience,
            "complexity_level": template_config.get("metadata", {}).get("complexity", 5),
            "platform": style_config.get("platform", "web"),
            "style_category": style_config.get("category", "general")
        }

    def _extract_positioning(self, template_config: Dict, style_config: Dict) -> str:
        """Extract positioning from template and style."""
        positioning = template_config.get("metadata", {}).get("positioning")
        if not positioning:
            raise RuntimeError(f"ENTERPRISE: Template '{template_config.get('id')}' must define 'positioning' in its metadata.")
        return f"{positioning} delivered in a {style_config.get('name', 'default')} style."

    def _extract_success_metrics(self, template_config: Dict) -> Dict[str, Any]:
        """Extract success metrics from template requirements."""
        metrics = template_config.get("requirements", {}).get("success_metrics")
        if not metrics or not isinstance(metrics, dict):
            raise RuntimeError(f"ENTERPRISE: Template '{template_config.get('id')}' must define 'success_metrics' as a dict in its requirements.")
        return metrics