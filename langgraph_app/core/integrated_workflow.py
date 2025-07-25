from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    ContentSpecification,
    ContentPhase,
    AgentType
)
from langgraph_app.agents.enhanced_planner_integrated import EnhancedPlannerAgent
from langgraph_app.agents.enhanced_researcher_integrated import EnhancedResearcherAgent
from langgraph_app.agents.writer_integrated import IntegratedWriterAgent
from langgraph_app.agents.enhanced_editor_integrated import EnhancedEditorAgent

class IntegratedContentWorkflow:
    """Orchestrates the integrated agent workflow using EnrichedContentState"""
    
    def __init__(self):
        self.agents = {
            AgentType.PLANNER: EnhancedPlannerAgent(),
            AgentType.RESEARCHER: EnhancedResearcherAgent(),
            AgentType.WRITER: IntegratedWriterAgent(),
            AgentType.EDITOR: EnhancedEditorAgent(),
            # Add other agents as they're integrated
        }
        
        self.workflow_phases = [
            ContentPhase.PLANNING,
            ContentPhase.RESEARCH,
            ContentPhase.WRITING,
            ContentPhase.EDITING,
            ContentPhase.FORMATTING,
            ContentPhase.SEO_OPTIMIZATION,
            ContentPhase.PUBLISHING
        ]
    
    def execute_workflow(self, 
                        template_type: str,
                        topic: str, 
                        audience: str,
                        platform: str,
                        **kwargs) -> EnrichedContentState:
        """Execute the complete integrated workflow"""
        
        # Create initial state
        state = self._create_initial_state(template_type, topic, audience, platform, **kwargs)
        
        # Execute each phase
        for phase in self.workflow_phases:
            if phase == ContentPhase.PLANNING:
                state = self.agents[AgentType.PLANNER].execute(state)
            elif phase == ContentPhase.RESEARCH:
                state = self.agents[AgentType.RESEARCHER].execute(state)
            elif phase == ContentPhase.WRITING:
                state = self.agents[AgentType.WRITER].execute(state)
            elif phase == ContentPhase.EDITING:
                state = self.agents[AgentType.EDITOR].execute(state)
            # Add other phases as agents are integrated
            
            # Calculate confidence after each phase
            state.calculate_overall_confidence()
            
            # Log phase completion
            print(f"✅ Completed {phase.value} phase - Confidence: {state.overall_confidence:.2f}")
        
        # Finalize content
        state.final_content = state.draft_content
        state.current_phase = ContentPhase.COMPLETE
        
        return state
    
    def _create_initial_state(self, template_type: str, topic: str, audience: str, platform: str, **kwargs) -> EnrichedContentState:
        """Create initial enriched content state"""
        
        content_spec = ContentSpecification(
            template_type=template_type,
            topic=topic,
            audience=audience,
            platform=platform,
            target_length=kwargs.get('target_length', 1200),
            complexity_level=kwargs.get('complexity_level', 7),
            innovation_level=kwargs.get('innovation_level', 'balanced'),
            business_context=kwargs.get('business_context', {}),
            constraints=kwargs.get('constraints', {})
        )
        
        return EnrichedContentState(
            content_spec=content_spec,
            current_phase=ContentPhase.PLANNING
        )


# Usage Example
if __name__ == "__main__":
    # Create workflow
    workflow = IntegratedContentWorkflow()
    
    # Execute integrated content generation
    result_state = workflow.execute_workflow(
        template_type="business_proposal",
        topic="AI-Powered Customer Service Automation",
        audience="venture_capital_investors", 
        platform="deck_presentation",
        target_length=1500,
        complexity_level=8,
        innovation_level="innovative",
        business_context={
            "industry": "technology",
            "stage": "series_a",
            "market": "enterprise_software"
        }
    )
    
    # Access rich results
    print(f"Final content length: {len(result_state.final_content.split())} words")
    print(f"Overall confidence: {result_state.overall_confidence:.2f}")
    print(f"Agent execution log: {len(result_state.agent_execution_log)} entries")
    
    # Access specific agent outputs
    if result_state.planning_output:
        print(f"Key messages: {result_state.planning_output.key_messages}")
    
    if result_state.research_findings:
        print(f"Research insights: {len(result_state.research_findings.primary_insights)}")
    
    # Export state for analysis
    state_dict = result_state.to_dict()
    print(f"Exportable state keys: {list(state_dict.keys())}")
from typing import Dict, Any
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    PlanningOutput
)
from datetime import datetime

class EnhancedPlannerAgent:
    """Integrated Planner Agent using EnrichedContentState"""
    
    def __init__(self):
        self.agent_type = AgentType.PLANNER
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute planning with dynamic instructions"""
        
        # Get dynamic instructions from the state
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "instructions_received": len(instructions.primary_objectives),
            "confidence_threshold": instructions.confidence_threshold
        })
        
        # Execute planning logic with dynamic instructions
        planning_output = self._execute_planning_logic(state, instructions)
        
        # Update state with planning results
        state.planning_output = planning_output
        state.update_phase(ContentPhase.RESEARCH)
        
        # Log execution completion
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "confidence_score": planning_output.planning_confidence,
            "key_decisions": len(planning_output.key_messages),
            "research_priorities": len(planning_output.research_priorities)
        })
        
        return state
    
    def _execute_planning_logic(self, state: EnrichedContentState, instructions) -> PlanningOutput:
        """Core planning logic using dynamic instructions"""
        spec = state.content_spec
        
        # Use instructions to guide planning decisions
        content_strategy = self._develop_content_strategy(spec, instructions)
        structure_approach = self._determine_structure_approach(spec, instructions)
        key_messages = self._identify_key_messages(spec, instructions)
        research_priorities = self._set_research_priorities(spec, instructions)
        
        return PlanningOutput(
            content_strategy=content_strategy,
            structure_approach=structure_approach,
            key_messages=key_messages,
            research_priorities=research_priorities,
            audience_insights=self._analyze_audience(spec),
            competitive_positioning=self._determine_positioning(spec),
            success_metrics=self._define_success_metrics(spec),
            estimated_sections=self._estimate_sections(spec),
            planning_confidence=0.85
        )
    
    def _develop_content_strategy(self, spec, instructions) -> str:
        """Develop strategy using dynamic instructions"""
        if spec.template_type == "business_proposal":
            if "venture_capital" in spec.audience.lower():
                return "investor_focused_growth_narrative"
            elif "enterprise" in spec.audience.lower():
                return "enterprise_solution_positioning"
        elif spec.template_type == "technical_documentation":
            if spec.complexity_level > 7:
                return "expert_technical_deep_dive"
            else:
                return "accessible_technical_guide"
        
        return f"adaptive_{spec.innovation_level}_approach"
    
    def _determine_structure_approach(self, spec, instructions) -> str:
        """Determine structure using contextual guidance"""
        # Use instructions.contextual_guidance to inform decisions
        if "strategic narrative" in instructions.contextual_guidance:
            return "narrative_driven_structure"
        elif "technical content" in instructions.contextual_guidance:
            return "problem_solution_implementation"
        
        return "discovery_insight_application"
    
    def _identify_key_messages(self, spec, instructions) -> list:
        """Extract key messages from objectives"""
        key_messages = []
        
        for objective in instructions.primary_objectives:
            if "strategic" in objective.lower():
                key_messages.append("Strategic value proposition")
            elif "technical" in objective.lower():
                key_messages.append("Technical excellence and implementation")
            elif "roi" in objective.lower() or "financial" in objective.lower():
                key_messages.append("Financial impact and ROI")
        
        # Add template-specific messages
        if spec.template_type == "business_proposal":
            key_messages.extend([
                "Market opportunity and timing",
                "Competitive advantage",
                "Implementation roadmap"
            ])
        
        return key_messages[:5]  # Limit to top 5 messages
    
    def _set_research_priorities(self, spec, instructions) -> list:
        """Set research priorities based on requirements"""
        priorities = []
        
        # Extract from instructions
        requirements = instructions.specific_requirements
        if "market_data" in requirements.get("evidence_types", []):
            priorities.append("Market size and growth trends")
        if "financial_metrics" in requirements.get("evidence_types", []):
            priorities.append("Financial benchmarks and ROI data")
        if "case_studies" in requirements.get("evidence_types", []):
            priorities.append("Success stories and implementations")
        
        # Add context-specific priorities
        if spec.template_type == "business_proposal":
            priorities.extend([
                "Competitive landscape analysis",
                "Industry trend validation",
                "Target audience pain points"
            ])
        
        return priorities[:6]  # Limit research scope
    
    def _analyze_audience(self, spec) -> dict:
        """Analyze target audience"""
        return {
            "primary_audience": spec.audience,
            "expertise_level": spec.complexity_level,
            "decision_factors": self._identify_decision_factors(spec),
            "communication_preferences": self._determine_comm_preferences(spec)
        }
    
    def _determine_positioning(self, spec) -> str:
        """Determine competitive positioning"""
        if spec.innovation_level == "experimental":
            return "innovation_leader"
        elif spec.innovation_level == "conservative":
            return "reliable_proven_solution"
        else:
            return "balanced_innovation_reliability"
    
    def _define_success_metrics(self, spec) -> dict:
        """Define success metrics"""
        return {
            "engagement_target": 0.75,
            "comprehension_target": 0.80,
            "action_target": 0.60,
            "platform_specific": self._get_platform_metrics(spec.platform)
        }
    
    def _estimate_sections(self, spec) -> list:
        """Estimate content sections"""
        if spec.template_type == "business_proposal":
            return [
                {"name": "Executive Summary", "estimated_words": 200},
                {"name": "Problem & Opportunity", "estimated_words": 350},
                {"name": "Solution & Value Prop", "estimated_words": 450},
                {"name": "Financial Analysis", "estimated_words": 350},
                {"name": "Implementation Plan", "estimated_words": 250}
            ]
        elif spec.template_type == "technical_documentation":
            return [
                {"name": "Overview", "estimated_words": 200},
                {"name": "Technical Specifications", "estimated_words": 500},
                {"name": "Implementation Guide", "estimated_words": 700},
                {"name": "Examples & Best Practices", "estimated_words": 500},
                {"name": "Troubleshooting", "estimated_words": 300}
            ]
        
        # Default structure
        return [
            {"name": "Introduction", "estimated_words": 200},
            {"name": "Main Content", "estimated_words": 800},
            {"name": "Conclusion", "estimated_words": 200}
        ]
    
    def _identify_decision_factors(self, spec) -> list:
        """Identify what influences audience decisions"""
        if "investor" in spec.audience.lower():
            return ["ROI potential", "Market size", "Competitive advantage", "Team credibility"]
        elif "technical" in spec.audience.lower():
            return ["Implementation feasibility", "Technical specifications", "Documentation quality"]
        
        return ["Clarity", "Credibility", "Actionability"]
    
    def _determine_comm_preferences(self, spec) -> dict:
        """Determine communication preferences"""
        return {
            "formality_level": "high" if spec.complexity_level > 7 else "moderate",
            "detail_preference": "comprehensive" if spec.complexity_level > 6 else "concise",
            "visual_preference": "data_rich" if "business" in spec.template_type else "explanatory"
        }
    
    def _get_platform_metrics(self, platform: str) -> dict:
        """Get platform-specific success metrics"""
        metrics = {
            "linkedin": {"engagement_rate": 0.05, "click_through": 0.02},
            "medium": {"read_time": 8, "highlight_rate": 0.15},
            "substack": {"open_rate": 0.45, "click_rate": 0.08}
        }
        return metrics.get(platform, {"engagement": 0.05})

