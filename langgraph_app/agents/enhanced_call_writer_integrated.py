# langgraph_app/agents/enhanced_call_writer_integrated.py
# FIXED: Synthesizes planning and research into final instructions for the writer.

import logging
from datetime import datetime
from langgraph_app.core.state import (
    EnrichedContentState,
    AgentType
)

logger = logging.getLogger(__name__)

class EnhancedCallWriterAgent:
    """
    Call Writer agent that prepares the final, definitive writing instructions
    by synthesizing the outputs from the Planner and Researcher.
    """

    def __init__(self):
        self.agent_type = AgentType.CALL_WRITER

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute call writer logic to create the final writing context."""
        logger.info("Executing Call Writer to synthesize instructions...")
        state.log_agent_execution(self.agent_type, {"status": "started"})

        if not state.planning_output or not state.research_findings:
            raise RuntimeError("ENTERPRISE: Call Writer requires both planning_output and research_findings.")

        # Synthesize all inputs into a final, structured writing context.
        # This becomes the single source of truth for the Writer agent.
        writing_context = {
            "topic": state.content_spec.topic,
            "target_audience": state.style_config.get("audience"),
            "platform": state.style_config.get("platform"),
            "template_type": state.template_config.get("template_type"),
            "style_profile_name": state.style_config.get("name"),

            # Synthesized from Planner
            "content_strategy": state.planning_output.content_strategy,
            "structure_approach": state.planning_output.structure_approach,
            "key_messages": state.planning_output.key_messages,
            "required_sections": [s['name'] for s in state.planning_output.estimated_sections],

            # Synthesized from Researcher
            "primary_insights": state.research_findings.primary_insights,
            "statistical_evidence": state.research_findings.statistical_evidence,
            "expert_quotes": state.research_findings.expert_quotes,
            "credibility_sources": state.research_findings.credibility_sources,

            # Directives for the Writer
            "instructions": state.template_config.get("instructions"),
            "style_prompt": state.style_config.get("system_prompt"),
            "voice": state.style_config.get("voice"),
            "tone": state.style_config.get("tone"),
        }

        # Store the unified context for the writer.
        state.writing_context = writing_context

        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "action": "writing_context_prepared",
            "strategy": writing_context["content_strategy"],
            "key_messages_count": len(writing_context["key_messages"]),
            "insights_count": len(writing_context["primary_insights"])
        })
        logger.info("Call Writer finished, writing_context is prepared.")
        return state