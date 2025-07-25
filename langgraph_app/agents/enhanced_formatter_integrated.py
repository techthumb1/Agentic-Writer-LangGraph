from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    FormattingRequirements
)

class EnhancedFormatterAgent:
    """Integrated Formatter Agent using EnrichedContentState"""
    
    def __init__(self):
        self.agent_type = AgentType.FORMATTER
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute formatting with platform-specific optimization"""
        
        # Get dynamic instructions
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "platform": state.content_spec.platform,
            "content_length": len(state.draft_content.split()),
            "target_formatting": instructions.specific_requirements.get("platform")
        })
        
        # Create formatting requirements
        formatting_requirements = self._create_formatting_requirements(state, instructions)
        state.formatting_requirements = formatting_requirements
        
        # Apply formatting
        formatted_content = self._apply_platform_formatting(state, instructions)
        state.draft_content = formatted_content
        
        # Update phase
        state.update_phase(ContentPhase.SEO_OPTIMIZATION)
        
        # Log completion
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "formatting_applied": len(formatting_requirements.formatting_elements),
            "confidence_score": formatting_requirements.formatting_confidence,
            "accessibility_features": len(formatting_requirements.accessibility_requirements)
        })
        
        return state
    
    def _create_formatting_requirements(self, state: EnrichedContentState, instructions) -> FormattingRequirements:
        """Create platform-specific formatting requirements"""
        
        spec = state.content_spec
        platform = spec.platform
        
        # Platform-specific specifications
        platform_specs = self._get_platform_specifications(platform)
        
        # Visual hierarchy based on content structure
        visual_hierarchy = self._determine_visual_hierarchy(state.draft_content, platform)
        
        # Formatting elements needed
        formatting_elements = self._identify_formatting_elements(state, platform)
        
        # Accessibility requirements
        accessibility_requirements = self._define_accessibility_requirements(platform)
        
        return FormattingRequirements(
            platform_specifications=platform_specs,
            visual_hierarchy=visual_hierarchy,
            formatting_elements=formatting_elements,
            accessibility_requirements=accessibility_requirements,
            seo_considerations=self._identify_seo_considerations(state),
            publication_metadata=self._generate_publication_metadata(state),
            formatting_confidence=0.88
        )
    
    def _apply_platform_formatting(self, state: EnrichedContentState, instructions) -> str:
        """Apply platform-specific formatting to content"""
        
        content = state.draft_content
        platform = state.content_spec.platform
        requirements = state.formatting_requirements
        
        # Apply platform-specific formatting
        if platform == "linkedin":
            content = self._format_for_linkedin(content, requirements)
        elif platform == "medium":
            content = self._format_for_medium(content, requirements)
        elif platform == "substack":
            content = self._format_for_substack(content, requirements)
        elif platform == "deck_presentation":
            content = self._format_for_presentation(content, requirements)
        else:
            content = self._format_for_web(content, requirements)
        
        # Apply universal improvements
        content = self._apply_visual_hierarchy(content, requirements.visual_hierarchy)
        content = self._add_accessibility_features(content, requirements.accessibility_requirements)
        
        return content
    
    def _get_platform_specifications(self, platform: str) -> dict:
        """Get platform-specific specifications"""
        
        specs = {
            "linkedin": {
                "max_length": 3000,
                "optimal_length": 1500,
                "supports_markdown": False,
                "supports_html": False,
                "image_specs": {"max_width": 1200, "aspect_ratio": "16:9"}
            },
            "medium": {
                "max_length": 10000,
                "optimal_length": 2000,
                "supports_markdown": True,
                "supports_html": True,
                "image_specs": {"max_width": 1000, "aspect_ratio": "3:2"}
            },
            "substack": {
                "max_length": 15000,
                "optimal_length": 2500,
                "supports_markdown": True,
                "supports_html": True,
                "image_specs": {"max_width": 1456, "aspect_ratio": "16:9"}
            },
            "deck_presentation": {
                "max_length": 100,  # per slide
                "optimal_length": 50,  # per slide
                "supports_markdown": False,
                "bullet_points": True,
                "slide_count": 12
            }
        }
        
        return specs.get(platform, {
            "max_length": 5000,
            "optimal_length": 1500,
            "supports_markdown": True,
            "supports_html": False
        })
    
    def _determine_visual_hierarchy(self, content: str, platform: str) -> list:
        """Determine visual hierarchy for content"""
        
        hierarchy = []
        
        # Extract existing headers
        import re
        headers = re.findall(r'^#+\s+(.+)', content, re.MULTILINE)
        # (rest of the method continues as intended)
    
    def _generate_implementation_section(self, spec, planning, research, target_words: int) -> str:
        """Generate implementation timeline section"""
        
        content = f"# Implementation Timeline & Next Steps\n\n"
        
        content += f"**Phase 1: Foundation (Months 1-2)**\n"
        content += f"- Stakeholder alignment and team formation\n"
        content += f"- Technical infrastructure assessment\n"
        content += f"- Baseline metrics establishment\n"
        content += f"- Initial pilot program design\n\n"
        
        content += f"**Phase 2: Pilot Implementation (Months 3-4)**\n"
        content += f"- Limited scope deployment\n"
        content += f"- User training and onboarding\n"
        content += f"- Performance monitoring and optimization\n"
        content += f"- Feedback collection and analysis\n\n"
        
        content += f"**Phase 3: Full Deployment (Months 5-6)**\n"
        content += f"- Organization-wide rollout\n"
        content += f"- Process integration and automation\n"
        content += f"- Performance validation and reporting\n"
        content += f"- Success metric achievement confirmation\n\n"
        
        content += f"**Immediate Next Steps:**\n"
        content += f"- Executive approval and budget allocation\n"
        content += f"- Project team assembly and kickoff\n"
        content += f"- Vendor selection and contract negotiation\n"
        content += f"- Detailed project planning and milestone definition\n\n"
        
        content += f"**Resource Requirements:**\n"
        content += f"- Project management: 1 FTE for 6 months\n"
        content += f"- Technical implementation: 2-3 FTE for 4 months\n"
        content += f"- Change management: 1 FTE for 3 months\n"
        content += f"- Executive sponsorship: 20% commitment for 6 months\n\n"
        
        content += f"**Success Assurance:**\n"
        content += f"- Weekly progress reviews and risk mitigation\n"
        content += f"- Quarterly executive steering committee\n"
        content += f"- Continuous stakeholder communication\n"
        content += f"- Post-implementation optimization and support"
        
        return content
    
    def _generate_generic_section(self, section_name: str, spec, planning, research, target_words: int) -> str:
        """Generate generic section with available context"""
        
        content = f"# {section_name}\n\n"
        
        # Use available context to generate relevant content
        if research and research.primary_insights:
            content += f"**Key Insights:**\n"
            for insight in research.primary_insights[:3]:
                content += f"- {insight.get('finding', 'Research finding')}\n"
            content += "\n"
        
        if planning and planning.key_messages:
            content += f"**Strategic Considerations:**\n"
            for message in planning.key_messages[:3]:
                content += f"- {message}\n"
            content += "\n"
        
        content += f"**Implementation Approach:**\n"
        content += f"- Systematic methodology aligned with {spec.audience} requirements\n"
        content += f"- {spec.innovation_level.title()} approach balancing innovation with reliability\n"
        content += f"- Measurable outcomes and continuous improvement\n\n"
        
        content += f"**Expected Outcomes:**\n"
        content += f"- Enhanced operational efficiency\n"
        content += f"- Improved strategic positioning\n"
        content += f"- Measurable business impact"
        
        return content
    
    def _generate_default_structure(self, spec, planning, research, context, instructions) -> list:
        """Generate default content structure when no planning available"""
        
        sections = []
        
        # Introduction
        intro = f"# {spec.topic}: Strategic Analysis and Recommendations\n\n"
        intro += f"This analysis provides comprehensive insights into {spec.topic} "
        intro += f"for {spec.audience} with actionable recommendations and implementation guidance."
        sections.append(intro)
        
        # Main content
        main = f"# Analysis and Recommendations\n\n"
        if research and research.primary_insights:
            main += f"**Research Findings:**\n"
            for insight in research.primary_insights[:4]:
                main += f"- {insight.get('finding', 'Key research finding')}\n"
            main += "\n"
        
        main += f"**Strategic Recommendations:**\n"
        main += f"- Implement {spec.innovation_level} approach to {spec.topic}\n"
        main += f"- Focus on {spec.audience}-specific value creation\n"
        main += f"- Establish measurable success metrics and monitoring\n"
        main += f"- Ensure scalable and sustainable implementation"
        sections.append(main)
        
        # Conclusion
        conclusion = f"# Conclusion and Next Steps\n\n"
        conclusion += f"The analysis demonstrates significant opportunity for {spec.audience} "
        conclusion += f"to leverage {spec.topic} for competitive advantage. "
        conclusion += f"Immediate next steps include stakeholder alignment, resource allocation, "
        conclusion += f"and implementation planning to capitalize on identified opportunities."
        sections.append(conclusion)
        
        return sections
    
    def _calculate_tone_adaptation(self, spec, planning, research) -> dict:
        """Calculate tone adaptation based on context"""
        
        base_tone = {
            "formal": 0.6,
            "conversational": 0.4,
            "technical": 0.3,
            "persuasive": 0.5,
            "authoritative": 0.7
        }
        
        # Adjust for audience
        if "executive" in spec.audience.lower() or "investor" in spec.audience.lower():
            base_tone["formal"] = 0.8
            base_tone["authoritative"] = 0.9
            base_tone["conversational"] = 0.2
        elif "technical" in spec.audience.lower():
            base_tone["technical"] = 0.8
            base_tone["formal"] = 0.7
        
        # Adjust for template type
        if spec.template_type == "business_proposal":
            base_tone["persuasive"] = 0.8
            base_tone["authoritative"] = 0.9
        
        # Adjust for innovation level
        if spec.innovation_level == "experimental":
            base_tone["conversational"] = 0.6
            base_tone["engaging"] = 0.8
        
        return base_tone
    
    def _define_voice_characteristics(self, spec, planning) -> list:
        """Define voice characteristics based on context"""
        
        characteristics = ["professional", "knowledgeable"]
        
        if spec.innovation_level == "experimental":
            characteristics.extend(["innovative", "forward_thinking"])
        elif spec.innovation_level == "conservative":
            characteristics.extend(["reliable", "proven"])
        
        if "investor" in spec.audience.lower():
            characteristics.extend(["strategic", "results_oriented"])
        elif "technical" in spec.audience.lower():
            characteristics.extend(["precise", "detail_oriented"])
        
        return characteristics
    
    def _determine_technical_depth(self, spec, research) -> str:
        """Determine appropriate technical depth"""
        
        if spec.complexity_level >= 8:
            return "expert_level"
        elif spec.complexity_level >= 6:
            return "advanced"
        elif spec.complexity_level >= 4:
            return "intermediate"
        else:
            return "accessible"
    
    def _select_innovation_techniques(self, spec, instructions) -> list:
        """Select innovation techniques based on level and instructions"""
        
        techniques = []
        
        if spec.innovation_level in ["innovative", "experimental"]:
            techniques.extend(["contrarian_perspective", "analogy_bridging"])
        
        if spec.complexity_level >= 7:
            techniques.extend(["assumption_archaeology", "emergence_patterns"])
        
        # Add from instructions
        innovation_directives = instructions.innovation_directives
        techniques.extend(innovation_directives[:2])
        
        return list(set(techniques))  # Remove duplicates
    
    def _generate_content_hooks(self, planning, research) -> list:
        """Generate content hooks from planning and research"""
        
        hooks = []
        
        if planning and planning.key_messages:
            hooks.append(f"Strategic insight: {planning.key_messages[0]}")
        
        if research and research.statistical_evidence:
            stat = research.statistical_evidence[0]
            hooks.append(f"Compelling data: {stat.get('statistic', 'Significant market trend')}")
        
        if research and research.trending_topics:
            hooks.append(f"Market trend: {research.trending_topics[0]}")
        
        return hooks[:3]  # Limit to top 3 hooks
    
    def _prioritize_sections(self, planning) -> dict:
        """Prioritize sections based on planning strategy"""
        
        if planning and "investor" in planning.content_strategy:
            return {
                "executive_summary": 10,
                "financial_analysis": 9,
                "market_opportunity": 8,
                "implementation": 7
            }
        elif planning and "technical" in planning.content_strategy:
            return {
                "technical_specifications": 10,
                "implementation": 9,
                "examples": 8,
                "overview": 7
            }
        
        return {
            "introduction": 8,
            "main_content": 10,
            "conclusion": 7
        }
    
    def _extract_sections(self, content: str) -> list:
        """Extract sections from generated content"""
        
        import re
        sections = re.findall(r'^#\s+(.+)', content, re.MULTILINE)
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

