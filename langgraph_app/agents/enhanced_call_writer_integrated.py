# langgraph_app/agents/enhanced_call_writer_integrated.py
"""
Enterprise Call Writer Agent - coordinates multi-agent writing process.
Lightweight coordination layer between planner/researcher and writer.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from langgraph_app.core.state import EnrichedContentState, AgentType
from langgraph_app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class EnhancedCallWriterAgent(BaseAgent):
    """
    Call Writer coordinates the writing process by:
    - Extracting planning and research outputs
    - Building writing instructions for the writer agent
    - Validating prerequisites are met
    - Coordinating template-specific requirements
    """
    
    def __init__(self):
        super().__init__(AgentType.CALL_WRITER)
    
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Coordinate writing process with validation."""
        
        logger.info("📞 CALL_WRITER: Coordinating writing process")
        
        self.log_execution_start(state)
        
        # Validate prerequisites
        self.validate_state(state, ['content_spec', 'template_config'])
        
        if not state.planning_output:
            logger.warning("⚠️ No planning output - writer will use defaults")
        
        if not state.research_findings:
            logger.warning("⚠️ No research findings - writer proceeds without research")
        
        # Build comprehensive writing instructions
        writing_instructions = self._build_writing_instructions(state)
        
        # Store for writer agent
        state.writing_context = writing_instructions
        
        # Coordinate template-specific requirements
        self._coordinate_template_requirements(state)
        
        self.log_execution_complete(state, {
            "instructions_prepared": True,
            "research_available": bool(state.research_findings),
            "planning_available": bool(state.planning_output)
        })
        
        logger.info("✅ CALL_WRITER: Coordination complete")
        
        return state
    
    def _build_writing_instructions(self, state: EnrichedContentState) -> Dict[str, Any]:
        """Build comprehensive writing instructions."""
        
        # Extract planning guidance
        if state.planning_output:
            content_strategy = getattr(state.planning_output, 'content_strategy', 'balanced')
            structure_approach = getattr(state.planning_output, 'structure_approach', 'standard')
            key_messages = getattr(state.planning_output, 'key_messages', [])
            research_priorities = getattr(state.planning_output, 'research_priorities', [])
        else:
            content_strategy = 'balanced'
            structure_approach = 'standard'
            key_messages = []
            research_priorities = []
        
        # Extract research context
        research_context = {}
        if state.research_findings:
            research_context = {
                'primary_insights': getattr(state.research_findings, 'primary_insights', []),
                'statistical_evidence': getattr(state.research_findings, 'statistical_evidence', []),
                'credibility_sources': getattr(state.research_findings, 'credibility_sources', [])
            }
        
        # Build instructions
        instructions = {
            "strategy": content_strategy,
            "structure": structure_approach,
            "key_messages": key_messages,
            "research_priorities": research_priorities,
            "research_context": research_context,
            "template_type": state.content_spec.template_type if state.content_spec else "default",
            "target_audience": state.content_spec.target_audience if state.content_spec else "general",
            "topic": state.content_spec.topic if state.content_spec else "Content",
            "platform": state.content_spec.platform if state.content_spec else "web"
        }
        
        return instructions
    
    def _coordinate_template_requirements(self, state: EnrichedContentState) -> None:
        """Coordinate template-specific requirements."""
        
        template_config = state.template_config or {}
        template_type = template_config.get('template_type', '')
        
        # Set coordination flags based on template
        coordination_flags = {}
        
        if 'business' in template_type.lower() or 'proposal' in template_type.lower():
            coordination_flags['require_executive_summary'] = True
            coordination_flags['require_financial_section'] = True
            coordination_flags['require_implementation_plan'] = True
        
        if 'technical' in template_type.lower() or 'documentation' in template_type.lower():
            coordination_flags['require_code_examples'] = True
            coordination_flags['require_prerequisites'] = True
            coordination_flags['technical_depth'] = 'high'
        
        if 'pitch' in template_type.lower() or 'investor' in template_type.lower():
            coordination_flags['require_market_analysis'] = True
            coordination_flags['require_competitive_landscape'] = True
            coordination_flags['require_financial_projections'] = True
        
        # Store flags in writing context
        if not state.writing_context:
            state.writing_context = {}
        
        state.writing_context['coordination_flags'] = coordination_flags
        
        logger.info(f"📋 Coordination flags set: {list(coordination_flags.keys())}")