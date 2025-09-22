# File: langgraph_app/agents/enhanced_planner_integrated.py

"""
Enhanced Planner Agent for WriterzRoom content generation.
Merges template-driven coordination with working state management.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from types import SimpleNamespace
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    ContentSpec, 
    ContentType, 
    GenerationStatus,
    ContentPhase,
    PlanningOutput,
    AgentType
)

logger = logging.getLogger(__name__)
class EnhancedPlannerAgent:
    """Enhanced planner agent with template-driven coordination"""
    
    def __init__(self):
        self.name = "planner"
        self.agent_type = AgentType.PLANNER
        self.available = True
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute planning logic with template coordination"""
        self._require_valid_state(state)
        
        # Get and PERSIST template_config (enterprise: no fallbacks)
        # FIXED: Get or create template_config with fallback
        if not hasattr(state, 'template_config') or not isinstance(state.template_config, dict) or not state.template_config:
            raise RuntimeError("Planner requires state.template_config (non-empty dict) - enterprise mode, no fallbacks")
        template_config = state.template_config
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "instructions_received": len(instructions.primary_objectives) if hasattr(instructions, 'primary_objectives') else 0,
            "template_config_found": True,
            "template_type": template_config.get('template_type', 'default')
        })
        
        # Create content spec if missing
        if not state.content_spec:
            state.content_spec = self._create_default_content_spec(state, template_config)
        
        # Execute template-driven planning
        planning_output = self._execute_planning_logic(state, instructions, template_config)
        
        # Update state
        state.status = GenerationStatus.PLANNING
        state.current_agent = "planner"
        state.updated_at = datetime.now().isoformat()
        state.planning_output = planning_output
        state.research_plan = planning_output
        state.update_phase(ContentPhase.RESEARCH)
        
        # Ensure content_strategy exists
        if not hasattr(planning_output, 'content_strategy'):
            planning_output.content_strategy = "template_driven_strategy"
        
        # Update debug info
        if not state.debug_info:
            state.debug_info = {}
        
        state.debug_info.update({
            "planner_execution": {
                "timestamp": datetime.now().isoformat(),
                "action": "template_driven_planning_completed",
                "next_agent": "researcher",
                "content_strategy": planning_output.content_strategy,
                "research_priorities": len(planning_output.research_priorities)
            }
        })
        
        # Log execution completion
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "confidence_score": getattr(planning_output, 'planning_confidence', 0.85),
            "key_decisions": len(planning_output.key_messages),
            "research_priorities": len(planning_output.research_priorities),
            "template_strategy_applied": planning_output.content_strategy
        })
        
        return state
    
    def _execute_planning_logic(self, state: EnrichedContentState, instructions, template_config: dict) -> PlanningOutput:
        """Core planning logic using template configuration and dynamic instructions"""
        
        content_strategy = self._develop_content_strategy(state, instructions, template_config)
        structure_approach = self._determine_structure_approach(state, instructions, template_config) 
        key_messages = self._identify_key_messages(state, instructions, template_config)
        research_priorities = self._set_research_priorities(state, instructions, template_config)
        
        return PlanningOutput(
            content_strategy=content_strategy,
            structure_approach=structure_approach,
            key_messages=key_messages,
            research_priorities=research_priorities,
            audience_insights=self._analyze_audience(state, template_config),
            competitive_positioning=self._determine_positioning(state, template_config),
            success_metrics=self._define_success_metrics(state, template_config),
            estimated_sections=self._estimate_sections(state, template_config),
            planning_confidence=0.85
        )

    def _develop_content_strategy(self, state: EnrichedContentState, instructions, template_config: dict) -> str:
        """Develop content strategy from template config and instructions"""
        
        # TEMPLATE ENFORCEMENT: Use template-specific strategy first
        if template_config.get('content_strategy'):
            return template_config['content_strategy']

        # Use instructions for dynamic strategy
        if hasattr(instructions, 'primary_objectives'):
            for objective in instructions.primary_objectives:
                if "strategic" in objective.lower():
                    return "strategic_insight_narrative"
                elif "technical" in objective.lower():
                    return "technical_implementation_focus"

        # DYNAMIC FALLBACK: Generate strategy based on content characteristics
        return self._generate_dynamic_content_strategy(state, instructions, template_config)
    
    def _generate_dynamic_content_strategy(self, state: EnrichedContentState, instructions, template_config: dict) -> str:
        """Generate dynamic content strategy based on content characteristics"""

        topic_keywords = state.content_spec.topic.lower().split()
        audience_type = state.content_spec.target_audience.lower()
        complexity = state.content_spec.complexity_level
        
        # Strategy based on topic analysis
        if any(keyword in topic_keywords for keyword in ['ai', 'machine', 'learning', 'artificial', 'intelligence']):
            if complexity > 7:
                return "ai_technical_innovation_strategy"
            else:
                return "ai_accessible_education_strategy"
        
        elif any(keyword in topic_keywords for keyword in ['business', 'strategy', 'growth', 'market']):
            if "executive" in audience_type:
                return "executive_strategic_decision_strategy"
            elif "startup" in audience_type:
                return "startup_growth_acceleration_strategy"
            else:
                return "business_optimization_strategy"
        
        elif any(keyword in topic_keywords for keyword in ['health', 'medical', 'healthcare', 'clinical']):
            if "professional" in audience_type:
                return "healthcare_professional_insight_strategy"
            else:
                return "healthcare_patient_education_strategy"
        
        elif any(keyword in topic_keywords for keyword in ['tech', 'software', 'development', 'coding']):
            return "technical_implementation_strategy"
        
        # Strategy based on audience analysis
        if "investor" in audience_type:
            return "investment_opportunity_strategy"
        elif "developer" in audience_type:
            return "developer_enablement_strategy"
        elif "researcher" in audience_type:
            return "research_insight_strategy"
        
        # Default strategy
        return "balanced_content_approach_strategy"
    
    def _determine_structure_approach(self, state: EnrichedContentState, instructions, template_config: dict) -> str:
        """Determine structure using template config and contextual guidance"""
        
        # TEMPLATE ENFORCEMENT: Use template-defined structure
        if template_config.get('structure_approach'):
            return template_config['structure_approach']
        
        template_type = template_config.get('template_type', state.content_spec.template_type)
        
        # Template-specific structure approaches
        if template_type == "business_proposal":
            return "problem_solution_roi_implementation"
        elif template_type == "venture_capital_pitch":
            return "market_solution_traction_team_financials"
        elif template_type == "technical_documentation":
            return "overview_specification_implementation_examples"
        elif template_type == "api_documentation_template":
            return "api_overview_endpoints_examples_integration"
        
        # Use instructions contextual guidance
        if hasattr(instructions, 'contextual_guidance') and instructions.contextual_guidance:
            if "strategic narrative" in instructions.contextual_guidance:
                return "narrative_driven_structure"
            elif "technical content" in instructions.contextual_guidance:
                return "problem_solution_implementation"
        
        # DYNAMIC FALLBACK: Generate structure based on content analysis
        return self._generate_dynamic_structure_approach(state, instructions, template_config)
    
    def _generate_dynamic_structure_approach(self, state: EnrichedContentState, instructions, template_config: dict) -> str:
        """Generate dynamic structure approach based on content characteristics"""
        
        topic_lower = state.content_spec.topic.lower()
        audience_lower = state.content_spec.target_audience.lower()
        
        # Educational content structure
        if any(word in topic_lower for word in ['guide', 'tutorial', 'how-to', 'learn']):
            return "educational_step_by_step_structure"
        
        # Analysis content structure
        elif any(word in topic_lower for word in ['analysis', 'study', 'research', 'investigation']):
            return "analytical_findings_structure"
        
        # Comparison content structure
        elif any(word in topic_lower for word in ['vs', 'versus', 'compare', 'comparison']):
            return "comparative_analysis_structure"
        
        # Case study structure
        elif any(word in topic_lower for word in ['case', 'study', 'example', 'story']):
            return "case_study_narrative_structure"
        
        # Audience-driven structure
        if "executive" in audience_lower:
            return "executive_summary_driven_structure"
        elif "technical" in audience_lower:
            return "technical_specification_structure"
        elif "beginner" in audience_lower:
            return "foundational_building_structure"
        
        # Default structure
        return "discovery_insight_application_structure"
    
    def _identify_key_messages(self, state: EnrichedContentState, instructions, template_config: dict) -> List[str]:
        """Extract key messages from template config and objectives"""
        
        key_messages = []
        
        # TEMPLATE ENFORCEMENT: Use template-defined messages first
        if template_config.get('key_messages'):
            key_messages.extend(template_config['key_messages'])
        
        # Extract from instructions
        if hasattr(instructions, 'primary_objectives'):
            for objective in instructions.primary_objectives:
                if "strategic" in objective.lower():
                    key_messages.append("Strategic value proposition")
                elif "technical" in objective.lower():
                    key_messages.append("Technical excellence and implementation")
                elif "roi" in objective.lower() or "financial" in objective.lower():
                    key_messages.append("Financial impact and ROI")
        
        # Add template-specific messages
        template_type = template_config.get('template_type', state.content_spec.template_type)
        
        if template_type == "business_proposal":
            key_messages.extend([
                "Market opportunity and timing",
                "Competitive advantage",
                "Implementation roadmap"
            ])
        elif template_type == "venture_capital_pitch":
            key_messages.extend([
                "Massive market opportunity",
                "Proven traction and growth",
                "Experienced team execution",
                "Clear path to profitability"
            ])
        elif template_type == "technical_documentation":
            key_messages.extend([
                "Clear implementation guidance",
                "Best practices and standards",
                "Scalable architecture approach"
            ])
        elif template_type == "api_documentation_template":
            key_messages.extend([
                "Complete API endpoint coverage",
                "Developer-friendly implementation",
                "Integration examples and best practices"
            ])
        
        # DYNAMIC FALLBACK: Generate messages based on content analysis
        if not key_messages:
            key_messages = self._generate_dynamic_key_messages(state, instructions, template_config)
        
        return key_messages[:6]  # Limit to top 6 messages
    
    def _generate_dynamic_key_messages(self, state: EnrichedContentState, instructions, template_config: dict) -> List[str]:
        """Generate dynamic key messages based on content characteristics"""
        
        topic_keywords = state.content_spec.topic.lower().split()
        audience_type = state.content_spec.target_audience.lower()
        
        messages = []
        
        # Topic-based messages
        if any(keyword in topic_keywords for keyword in ['ai', 'artificial', 'intelligence', 'machine', 'learning']):
            messages.extend([
                f"AI innovation in {state.content_spec.topic}",
                "Practical AI implementation strategies",
                "Future-ready AI solutions"
            ])
        
        elif any(keyword in topic_keywords for keyword in ['business', 'strategy', 'growth']):
            messages.extend([
                f"Strategic {state.content_spec.topic} opportunity",
                "Measurable business impact",
                "Competitive market positioning"
            ])
        
        elif any(keyword in topic_keywords for keyword in ['health', 'medical', 'healthcare']):
            messages.extend([
                f"Healthcare innovation in {state.content_spec.topic}",
                "Patient-centered solutions",
                "Clinical efficacy and safety"
            ])
        
        # Audience-based messages
        if "executive" in audience_type:
            messages.extend([
                "Executive decision framework",
                "Strategic ROI potential"
            ])
        elif "developer" in audience_type:
            messages.extend([
                "Developer-friendly implementation",
                "Technical best practices"
            ])
        elif "investor" in audience_type:
            messages.extend([
                "Investment opportunity validation",
                "Market scalability potential"
            ])
        
        # Generic value-driven messages if still empty
        if not messages:
            messages = [
                f"Core insights about {state.content_spec.topic}",
                f"Practical applications for {state.content_spec.target_audience}",
                f"Strategic implementation of {state.content_spec.topic}"
            ]
        
        return messages
    
    def _set_research_priorities(self, state: EnrichedContentState, instructions, template_config: dict) -> List[str]:
        """Set research priorities based on template requirements and instructions"""
        
        priorities = []
        
        # TEMPLATE ENFORCEMENT: Use template-specific research priorities
        if template_config.get('research_priorities'):
            priorities.extend(template_config['research_priorities'])
        
        # Extract from instructions
        if hasattr(instructions, 'specific_requirements'):
            requirements = instructions.specific_requirements
            if "market_data" in requirements.get("evidence_types", []):
                priorities.append("Market size and growth trends")
            if "financial_metrics" in requirements.get("evidence_types", []):
                priorities.append("Financial benchmarks and ROI data")
            if "case_studies" in requirements.get("evidence_types", []):
                priorities.append("Success stories and implementations")
        
        # Add template-specific priorities
        template_type = template_config.get('template_type', state.content_spec.template_type)
        
        if template_type == "business_proposal":
            priorities.extend([
                "Competitive landscape analysis",
                "Industry trend validation",
                "Target audience pain points",
                "Implementation cost analysis"
            ])
        elif template_type == "venture_capital_pitch":
            priorities.extend([
                "Market size validation",
                "Competitive differentiation",
                "Traction metrics benchmarks",
                "Exit strategy comparables"
            ])
        elif template_type == "technical_documentation":
            priorities.extend([
                "Implementation examples",
                "Technical best practices",
                "Common challenges and solutions",
                "Performance benchmarks"
            ])
        elif template_type == "api_documentation_template":
            priorities.extend([
                "API endpoint specifications",
                "Authentication and security patterns",
                "Integration examples and SDKs",
                "Error handling and troubleshooting"
            ])
        
        # DYNAMIC FALLBACK: Generate priorities based on content analysis
        if not priorities:
            priorities = self._generate_dynamic_research_priorities(state, instructions, template_config)
        
        return list(set(priorities))[:8]  # Remove duplicates and limit scope
    
    def _generate_dynamic_research_priorities(self, state: EnrichedContentState, instructions, template_config: dict) -> List[str]:
        """Generate dynamic research priorities based on content characteristics"""
        
        topic_keywords = state.content_spec.topic.lower().split()
        priorities = []
        
        # Topic-based research priorities
        if any(keyword in topic_keywords for keyword in ['ai', 'artificial', 'intelligence', 'machine', 'learning']):
            priorities.extend([
                "AI technology trends and developments",
                "Industry AI adoption rates",
                "AI implementation case studies",
                "AI regulatory and ethical considerations"
            ])
        
        elif any(keyword in topic_keywords for keyword in ['business', 'strategy', 'growth']):
            priorities.extend([
                "Market size and opportunity analysis",
                "Competitive landscape research",
                "Industry best practices",
                "Financial performance benchmarks"
            ])
        
        elif any(keyword in topic_keywords for keyword in ['health', 'medical', 'healthcare']):
            priorities.extend([
                "Clinical research and evidence",
                "Healthcare industry trends",
                "Regulatory compliance requirements",
                "Patient outcome studies"
            ])
        
        elif any(keyword in topic_keywords for keyword in ['tech', 'software', 'development']):
            priorities.extend([
                "Technical specifications and standards",
                "Implementation methodologies",
                "Performance benchmarks",
                "Security and compliance requirements"
            ])
        
        # Audience-based priorities
        audience_lower = state.content_spec.target_audience.lower()
        if "executive" in audience_lower:
            priorities.extend([
                "Executive decision criteria",
                "Strategic impact assessment"
            ])
        elif "investor" in audience_lower:
            priorities.extend([
                "Investment thesis validation",
                "Market opportunity sizing"
            ])
        elif "technical" in audience_lower:
            priorities.extend([
                "Technical implementation details",
                "Architecture and design patterns"
            ])
        
        # Default comprehensive priorities
        if not priorities:
            priorities = [
                f"Background research on {state.content_spec.topic}",
                f"Current trends in {state.content_spec.topic}",
                f"Best practices for {state.content_spec.topic}",
                f"Case studies and examples",
                f"Future outlook for {state.content_spec.topic}"
            ]
        
        return priorities
    
    def _analyze_audience(self, state: EnrichedContentState, template_config: dict) -> dict:
        """Analyze target audience with template insights"""
        
        # Build comprehensive audience analysis
        analysis = {
            "primary_audience": state.content_spec.target_audience,
            "expertise_level": state.content_spec.complexity_level,
            "decision_factors": self._identify_decision_factors(state, template_config),
            "communication_preferences": self._determine_comm_preferences(state, template_config)
        }
        
        # Merge template insights
        audience_insights = template_config.get('audience_insights', {})
        analysis.update(audience_insights)
        
        return analysis
    
    def _determine_positioning(self, state: EnrichedContentState, template_config: dict) -> str:
        """Determine competitive positioning with template context"""
        
        # Use template-defined positioning if available
        if template_config.get('competitive_positioning'):
            return template_config['competitive_positioning']
        
        template_type = template_config.get('template_type', state.content_spec.template_type)
        
        if template_type == "venture_capital_pitch":
            return "market_disruptor_with_proven_traction"
        elif template_type == "business_proposal":
            return "strategic_partner_for_growth"
        elif template_type == "api_documentation_template":
            return "developer_focused_excellence_provider"
        
        # DYNAMIC FALLBACK: Generate positioning based on characteristics
        return self._generate_dynamic_positioning(state, template_config)
    
    def _generate_dynamic_positioning(self, state: EnrichedContentState, template_config: dict) -> str:
        """Generate dynamic competitive positioning"""
        
        audience_lower = state.content_spec.target_audience.lower()
        topic_keywords = state.content_spec.topic.lower().split()
        
        # Audience-based positioning
        if "executive" in audience_lower:
            return "strategic_executive_partner"
        elif "investor" in audience_lower:
            return "high_growth_investment_opportunity"
        elif "technical" in audience_lower or "developer" in audience_lower:
            return "technical_excellence_provider"
        
        # Topic-based positioning
        if any(keyword in topic_keywords for keyword in ['ai', 'artificial', 'intelligence']):
            return "ai_innovation_thought_leader"
        elif any(keyword in topic_keywords for keyword in ['health', 'medical', 'healthcare']):
            return "healthcare_transformation_catalyst"
        elif any(keyword in topic_keywords for keyword in ['business', 'strategy']):
            return "business_strategy_optimizer"
        
        # Default balanced positioning
        return "value_driven_solution_provider"
    
    def _define_success_metrics(self, state: EnrichedContentState, template_config: dict) -> dict:
        """Define success metrics with template-specific targets"""
        
        # Start with template-defined metrics
        base_metrics = template_config.get('success_metrics', {})
        
        # Default metrics
        default_metrics = {
            "engagement_target": 0.75,
            "comprehension_target": 0.80,
            "action_target": 0.60,
            "platform_specific": self._get_platform_metrics(state.content_spec.platform, template_config)
        }
        
        # Merge template metrics with defaults
        return {**default_metrics, **base_metrics}
    
    def _estimate_sections(self, state: EnrichedContentState, template_config: dict) -> List[dict]:
        """Estimate content sections using template configuration"""
        
        # TEMPLATE ENFORCEMENT: Use template-defined sections if available
        if template_config.get('section_order'):
            sections = []
            section_word_counts = template_config.get('section_word_counts', {})
            
            for section_name in template_config['section_order']:
                word_count = section_word_counts.get(section_name, 300)
                sections.append({
                    "name": section_name, 
                    "estimated_words": word_count,
                    "template_defined": True
                })
            return sections
        
        # Template-specific default sections
        template_type = template_config.get('template_type', state.content_spec.template_type)
        
        if template_type == "business_proposal":
            return [
                {"name": "Executive Summary", "estimated_words": 200},
                {"name": "Problem & Opportunity", "estimated_words": 350},
                {"name": "Solution & Value Proposition", "estimated_words": 450},
                {"name": "Financial Analysis", "estimated_words": 350},
                {"name": "Implementation Plan", "estimated_words": 300},
                {"name": "Risk Assessment", "estimated_words": 200}
            ]
        elif template_type == "api_documentation_template":
            return [
                {"name": "API Overview", "estimated_words": 250},
                {"name": "Authentication", "estimated_words": 300},
                {"name": "Core Endpoints", "estimated_words": 600},
                {"name": "Request/Response Examples", "estimated_words": 500},
                {"name": "Error Handling", "estimated_words": 250},
                {"name": "Integration Guide", "estimated_words": 400}
            ]
        
        # DYNAMIC SECTION GENERATION: Create sections based on content characteristics
        return self._generate_dynamic_sections(state, template_config)
    
    def _generate_dynamic_sections(self, state: EnrichedContentState, template_config: dict) -> List[dict]:
        """Generate dynamic sections based on content characteristics"""
        
        topic_keywords = state.content_spec.topic.lower().split()
        audience_lower = state.content_spec.target_audience.lower()
        complexity = state.content_spec.complexity_level
        
        sections = []
        
        # Always start with an introduction/overview
        sections.append({"name": f"{state.content_spec.topic} Overview", "estimated_words": 300})
        
        # Add topic-specific sections
        if any(keyword in topic_keywords for keyword in ['ai', 'artificial', 'intelligence', 'machine', 'learning']):
            sections.extend([
                {"name": "AI Technology Fundamentals", "estimated_words": 400},
                {"name": "Implementation Strategies", "estimated_words": 500},
                {"name": "Real-World Applications", "estimated_words": 450},
                {"name": "Future Implications", "estimated_words": 350}
            ])
        
        elif any(keyword in topic_keywords for keyword in ['business', 'strategy', 'growth']):
            sections.extend([
                {"name": "Strategic Analysis", "estimated_words": 450},
                {"name": "Market Opportunities", "estimated_words": 400},
                {"name": "Implementation Framework", "estimated_words": 500},
                {"name": "Success Metrics", "estimated_words": 300}
            ])
        
        # Always end with conclusion
        sections.append({"name": "Key Takeaways and Conclusions", "estimated_words": 300})
        
        return sections
    
    def _identify_decision_factors(self, state: EnrichedContentState, template_config: dict) -> List[str]:
        """Identify what influences audience decisions with template insights"""
        
        # Use template-defined factors if available
        if template_config.get('decision_factors'):
            return template_config['decision_factors']
        
        template_type = template_config.get('template_type', state.content_spec.template_type)
        
        if template_type == "venture_capital_pitch":
            return ["Market size", "Traction metrics", "Team experience", "Competitive moat", "Exit potential"]
        elif template_type == "business_proposal":
            return ["ROI potential", "Implementation feasibility", "Strategic alignment", "Risk mitigation"]
        elif template_type == "api_documentation_template":
            return ["Documentation completeness", "Integration ease", "Support quality", "Performance reliability"]
        
        # DYNAMIC FALLBACK: Generate factors based on audience analysis
        return self._generate_dynamic_decision_factors(state, template_config)
    
    def _generate_dynamic_decision_factors(self, state: EnrichedContentState, template_config: dict) -> List[str]:
        """Generate dynamic decision factors based on audience characteristics"""
        
        audience_lower = state.content_spec.target_audience.lower()
        topic_keywords = state.content_spec.topic.lower().split()
        
        # Audience-based factors
        if "investor" in audience_lower:
            return ["ROI potential", "Market size", "Competitive advantage", "Team credibility", "Exit strategy"]
        elif "executive" in audience_lower:
            return ["Strategic alignment", "Business impact", "Implementation cost", "Risk assessment", "Timeline"]
        elif "technical" in audience_lower or "developer" in audience_lower:
            return ["Implementation feasibility", "Technical specifications", "Documentation quality", "Support availability"]
        elif "researcher" in audience_lower:
            return ["Methodological rigor", "Data validity", "Reproducibility", "Research novelty"]
        
        # Topic-based factors
        if any(keyword in topic_keywords for keyword in ['ai', 'artificial', 'intelligence']):
            return ["Innovation potential", "Technical feasibility", "Ethical considerations", "Market readiness"]
        elif any(keyword in topic_keywords for keyword in ['health', 'medical']):
            return ["Clinical efficacy", "Patient safety", "Regulatory compliance", "Cost effectiveness"]
        elif any(keyword in topic_keywords for keyword in ['business', 'strategy']):
            return ["Market opportunity", "Competitive advantage", "Implementation feasibility", "Financial impact"]
        
        # Default comprehensive factors
        return ["Credibility", "Relevance", "Actionability", "Value proposition", "Implementation ease"]
    
    def _determine_comm_preferences(self, state: EnrichedContentState, template_config: dict) -> dict:
        """Determine communication preferences with template guidance"""
        
        # Start with template preferences
        base_prefs = template_config.get('communication_preferences', {})
        
        # Template-specific preferences
        template_type = template_config.get('template_type', state.content_spec.template_type)
        
        if template_type == "venture_capital_pitch":
            template_prefs = {
                "formality_level": "high",
                "detail_preference": "comprehensive_with_executive_summary",
                "visual_preference": "data_rich_with_charts",
                "tone": "confident_and_ambitious"
            }
        elif template_type == "business_proposal":
            template_prefs = {
                "formality_level": "high",
                "detail_preference": "thorough_with_evidence",
                "visual_preference": "professional_and_clean",
                "tone": "authoritative_and_trustworthy"
            }
        elif template_type == "api_documentation_template":
            template_prefs = {
                "formality_level": "medium",
                "detail_preference": "comprehensive_with_examples",
                "visual_preference": "code_heavy_with_diagrams",
                "tone": "clear_and_developer_friendly"
            }
        else:
            # DYNAMIC PREFERENCES: Generate based on audience and complexity
            template_prefs = self._generate_dynamic_comm_preferences(state, template_config)
        
        # Merge template and base preferences
        return {**template_prefs, **base_prefs}
    
    def _generate_dynamic_comm_preferences(self, state: EnrichedContentState, template_config: dict) -> dict:
        """Generate dynamic communication preferences"""
        
        audience_lower = state.content_spec.target_audience.lower()
        complexity = state.content_spec.complexity_level
        
        # Audience-based preferences
        if "executive" in audience_lower:
            return {
                "formality_level": "high",
                "detail_preference": "executive_summary_focused",
                "visual_preference": "high_level_dashboards",
                "tone": "authoritative_and_strategic"
            }
        elif "technical" in audience_lower or "developer" in audience_lower:
            return {
                "formality_level": "medium",
                "detail_preference": "comprehensive_with_examples",
                "visual_preference": "code_and_diagrams",
                "tone": "precise_and_practical"
            }
        elif "researcher" in audience_lower or "academic" in audience_lower:
            return {
                "formality_level": "very_high",
                "detail_preference": "exhaustive_with_citations",
                "visual_preference": "data_visualization_heavy",
                "tone": "objective_and_scholarly"
            }
        elif "investor" in audience_lower:
            return {
                "formality_level": "high",
                "detail_preference": "metrics_focused",
                "visual_preference": "financial_charts_and_projections",
                "tone": "confident_and_data_driven"
            }
        else:
            # General audience preferences based on complexity
            formality = "high" if complexity > 7 else "medium" if complexity > 4 else "low"
            detail = "comprehensive" if complexity > 6 else "balanced" if complexity > 3 else "concise"
            
            return {
                "formality_level": formality,
                "detail_preference": detail,
                "visual_preference": "clear_and_accessible",
                "tone": "engaging_and_informative"
            }
    
    def _get_platform_metrics(self, platform: str, template_config: dict) -> dict:
        """Get platform-specific success metrics with template adjustments"""
        
        base_metrics = {
            "linkedin": {"engagement_rate": 0.05, "click_through": 0.02},
            "medium": {"read_time": 8, "highlight_rate": 0.15},
            "substack": {"open_rate": 0.45, "click_rate": 0.08},
            "web": {"bounce_rate": 0.40, "time_on_page": 180},
            "blog": {"engagement_rate": 0.06, "share_rate": 0.03},
            "documentation": {"completion_rate": 0.70, "return_rate": 0.25}
        }
        
        platform_metrics = base_metrics.get(platform, {"engagement": 0.05, "conversion": 0.02})
        
        # Apply template-specific metric adjustments
        template_type = template_config.get('template_type')
        if template_type == "venture_capital_pitch":
            # Higher engagement expected for VC content
            for key, value in platform_metrics.items():
                if isinstance(value, (int, float)):
                    platform_metrics[key] = value * 1.3
        elif template_type == "technical_documentation":
            # Lower engagement but higher retention
            platform_metrics["retention_rate"] = 0.70
            platform_metrics["implementation_success_rate"] = 0.60
        elif template_type == "business_proposal":
            # Business content metrics
            platform_metrics["decision_maker_engagement"] = 0.80
            platform_metrics["follow_up_rate"] = 0.35
        
        return platform_metrics
    
    def _require_valid_state(self, state: EnrichedContentState) -> None:
        """Validate state requirements"""
        if not isinstance(state, EnrichedContentState):
            raise AttributeError("Invalid state type provided to planner")
            
        # Basic validation - can be expanded
        if not hasattr(state, 'debug_info') or state.debug_info is None:
            state.debug_info = {}
    
    def _create_default_content_spec(self, state: EnrichedContentState, template_config: dict) -> ContentSpec:
        """Create default content specification with template awareness"""
        
        template_type = template_config.get('template_type', 'article')
        default_length = template_config.get('default_length', 1000)
        
        return ContentSpec(
            content_type=ContentType.ARTICLE,
            topic=getattr(state, 'topic', template_config.get('default_topic', "General Content")),
            target_audience=template_config.get('default_audience', "general"),
            tone=template_config.get('default_tone', "professional"),
            length=default_length,
            template_id=template_config.get('template_id', "default"),
            template_type=template_type,
            style_profile=template_config.get('style_profile', "default"),
            complexity_level=template_config.get('complexity_level', 5)
        )


# For backward compatibility
def create_planner_agent() -> EnhancedPlannerAgent:
    """Factory function to create planner agent"""
    return EnhancedPlannerAgent()