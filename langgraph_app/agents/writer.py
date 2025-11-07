# langgraph_app/agents/writer.py

import os
import logging
from typing import Dict, Tuple
from langgraph_app.core.state import EnrichedContentState
from langgraph_app.core.model_registry import get_optimal_model
from langgraph_app.core.types import DraftContent
logger = logging.getLogger(__name__)

class WriterAgent:
    """Enterprise Writer Agent using intelligent model selection."""

    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY environment variable is required.")
    def _format_structure_requirements(self, structure: Dict) -> str:
        """Format structure requirements from template"""
        parts = []
        if structure.get('sections'):
            parts.append(f"Sections: {structure['sections']}")
        if structure.get('format'):
            parts.append(f"Format: {structure['format']}")
        if structure.get('format_requirements'):
            parts.append(f"Requirements: {structure['format_requirements']}")
        return " | ".join(parts) if parts else "Standard structure"

    def _format_planning_context(self, planning_output) -> str:
        """Extract planning guidance for writer"""
        parts = []
        if hasattr(planning_output, 'key_messages'):
            messages = getattr(planning_output, 'key_messages', [])
            if messages:
                parts.append(f"Key Messages: {', '.join(messages[:3])}")
        if hasattr(planning_output, 'structure_approach'):
            structure = getattr(planning_output, 'structure_approach', '')
            if structure:
                parts.append(f"Approach: {structure}")
        return "\n".join(parts) if parts else ""

    def _extract_user_inputs(self, state: EnrichedContentState) -> Dict:
        """Extract user inputs from dynamic_parameters"""
        inputs = {}
        if hasattr(state, 'dynamic_parameters'):
            dp = state.dynamic_parameters or {}
            if isinstance(dp, dict):
                for key, value in dp.items():
                    if key not in ['topic', 'target_audience', 'platform'] and value:
                        inputs[key] = value
        return inputs

    def _build_research_context(self, state: EnrichedContentState) -> str:
        """Extract research for writer prompt"""
        research = getattr(state, 'research_findings', None)
        if not research:
            return ""

        context_parts = []
        insights = getattr(research, 'primary_insights', [])
        if insights:
            context_parts.append("## KEY RESEARCH INSIGHTS:")
            for insight in insights[:5]:
                if isinstance(insight, dict):
                    finding = insight.get('finding', '')
                    if finding:
                        context_parts.append(f"- {finding}")

        return "\n".join(context_parts) if context_parts else ""
    def _extract_template_behavior_rules(self, template_config: Dict) -> str:
        """Extract template behavior enforcement rules from YAML"""
        rules = []

        # Template behavior
        behavior = template_config.get('template_behavior', {})
        if behavior:
            rules.append("TEMPLATE BEHAVIOR REQUIREMENTS:")
            rules.append(f"- Content Type: {behavior.get('content_type', 'standard')}")
            rules.append(f"- Output Format: {behavior.get('output_format', 'standard')}")
            if behavior.get('prevent_documentation'):
                rules.append("- CRITICAL: DO NOT generate documentation, guides, or tutorials")
            if behavior.get('require_post_format'):
                rules.append("- CRITICAL: Generate individual posts with captions, hashtags, CTAs")

        # Format enforcement
        enforcement = template_config.get('format_enforcement', {})
        if enforcement:
            forbidden = enforcement.get('forbidden_formats', [])
            if forbidden:
                rules.append(f"\nFORBIDDEN FORMATS (never generate):")
                for fmt in forbidden:
                    rules.append(f"  × {fmt}")

            required = enforcement.get('required_formats', [])
            if required:
                rules.append(f"\nREQUIRED FORMATS (must use):")
                for fmt in required:
                    rules.append(f"  ✓ {fmt}")

        # Coordination rules
        coordination = template_config.get('coordination_rules', {})
        if coordination:
            if coordination.get('force_casual_tone'):
                rules.append("\n- TONE: Must be casual and engaging")
            if coordination.get('require_engagement_elements'):
                rules.append("- ELEMENTS: Must include CTAs, hashtags, emojis")

        return "\n".join(rules) if rules else ""

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute writer with intelligently selected model."""
        if not state.planning_output or not state.research_findings:
            raise RuntimeError("ENTERPRISE: Writer requires planning_output and research_findings.")

        system_prompt, user_prompt = self._build_comprehensive_prompt(state)
        generation_settings = self._get_generation_settings(state)
        
        # Get optimal model based on task requirements
        model = get_optimal_model(
            task_type="writer",
            template_config=state.template_config,
            user_preferences=state.dynamic_parameters
        )

        logger.info(f"Generating content with {model.model_name}...")
        try:
            content = model.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=generation_settings["temperature"],
                max_tokens=generation_settings["max_tokens"]
            )
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise RuntimeError(f"ENTERPRISE: Content generation failed: {e}")

        if not content or len(content.strip()) < 150:
            logger.error(f"Generated content was insufficient. Length: {len(content.strip())}")
            raise RuntimeError(f"ENTERPRISE: Insufficient content generated. Length: {len(content.strip())}")

        # Extract title from content (first # heading or use topic)
        title = state.content_spec.topic if state.content_spec else "Untitled"
        first_heading = content.split('\n')[0] if content else ""
        if first_heading.startswith('#'):
            title = first_heading.lstrip('#').strip()
        
        # Create proper DraftContent object
        from langgraph_app.core.types import DraftContent
        state.draft_content = DraftContent(
            title=title,
            body=content,
            metadata={"generated_by": "writer", "length": len(content)}
        )
        state.content = content  # Legacy field
        
        logger.info(f"Writer completed, generated {len(content)} characters.")
        return state

    def _get_generation_settings(self, state: EnrichedContentState) -> Dict:
        """Use user settings from Settings page, with hard defaults only."""
        return {
            "temperature": state.dynamic_parameters.get("temperature", 0.7),
            "max_tokens": state.dynamic_parameters.get("max_tokens", 4000),
        }

    def _build_comprehensive_prompt(self, state: EnrichedContentState) -> tuple[str, str]:
        """Build system and user prompts with template behavior enforcement"""

        template_config = state.template_config
        style_config = state.style_config

        if not template_config or not style_config:
            raise RuntimeError("ENTERPRISE: template_config and style_config required")

        # Extract template behavior rules FIRST
        behavior_rules = self._extract_template_behavior_rules(template_config)

        # Build system prompt with behavior enforcement at top
        system_parts = []

        # 1. CRITICAL: Behavior rules first
        if behavior_rules:
            system_parts.append(f"=== CRITICAL TEMPLATE REQUIREMENTS ===\n{behavior_rules}\n{'='*50}\n")

        # 2. Template system prompt
        system_prompt = template_config.get('system_prompt', '')
        if system_prompt:
            system_parts.append(system_prompt)

        # 3. Style guide
        style_prompt = style_config.get('system_prompt', '')
        if style_prompt:
            system_parts.append(f"\nStyle Guide: {style_prompt}")

        system_parts.append(f"\nTone: {style_config.get('tone', 'professional')}")
        system_parts.append(f"Voice: {style_config.get('voice', 'authoritative')}")

        # 4. Template instructions
        instructions = template_config.get('instructions', '')
        if instructions:
            system_parts.append(f"\nInstructions: {instructions}")

        # 5. Structure requirements
        structure = template_config.get('structure', {})
        if structure:
            structure_text = self._format_structure_requirements(structure)
            system_parts.append(f"\nStructure: {structure_text}")

        # 6. Research context
        research_context = self._build_research_context(state)
        if research_context:
            system_parts.append(f"\n{research_context}")

        # Build user prompt
        user_parts = [
            f"Topic: {state.content_spec.topic}",
            f"Audience: {state.content_spec.target_audience}",
            f"Platform: {state.content_spec.platform}"
        ]

        # Add planning context
        if state.planning_output:
            planning_context = self._format_planning_context(state.planning_output)
            user_parts.append(f"\n{planning_context}")

        # Add dynamic parameters
        dynamic_params = self._extract_user_inputs(state)
        if dynamic_params:
            user_parts.append("\nParameters:")
            for key, value in dynamic_params.items():
                user_parts.append(f"- {key}: {value}")

        # CRITICAL: Re-emphasize format requirements in user prompt
        if behavior_rules:
            user_parts.append(f"\nREMINDER: Follow template behavior requirements above strictly.")

        system_content = "\n".join(system_parts)
        user_content = "\n".join(user_parts)

        return system_content, user_content
    
    def _format_list(self, items: list) -> str:
        if not items: return "  - None specified."
        return "\n".join([f"  - {item}" for item in items])

    def _format_insights(self, items: list) -> str:
        if not items: return "  - No specific insights provided."
        return "\n".join([f"  - {item.get('finding', '')} (Source: {item.get('source', 'N/A')})" for item in items])

    def _format_stats(self, items: list) -> str:
        if not items: return "  - No specific statistics provided."
        return "\n".join([f"  - {item.get('statistic', '')} (Source: {item.get('source', 'N/A')})" for item in items])

    def _format_quotes(self, items: list) -> str:
        if not items: return "  - No specific quotes provided."
        return "\n".join([f"  - {item.get('quote', '')} - {item.get('expert', 'N/A')}" for item in items])