# File: langgraph_app/agents/enhanced_seo_integrated.py
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    SEOOptimizationContext
)

class EnhancedSEOAgent:
    """Integrated SEO Agent using EnrichedContentState"""
    
    def __init__(self):
        self.agent_type = AgentType.SEO
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute SEO optimization with content context"""
        
        # Get dynamic instructions
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "platform": state.content_spec.platform,
            "has_research_context": bool(state.research_findings),
            "content_length": len(state.draft_content.split())
        })
        
        # Create SEO optimization context
        seo_context = self._create_seo_context(state, instructions)
        state.seo_context = seo_context
        
        # Apply SEO optimizations
        optimized_content = self._apply_seo_optimizations(state, instructions)
        state.draft_content = optimized_content
        
        # Update phase
        state.update_phase(ContentPhase.PUBLISHING)
        
        # Log completion
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "keywords_optimized": len(seo_context.target_keywords),
            "confidence_score": seo_context.optimization_confidence,
            "optimization_opportunities": len(seo_context.content_optimization_opportunities)
        })
        
        return state
    
    def _create_seo_context(self, state: EnrichedContentState, instructions) -> SEOOptimizationContext:
        """Create SEO optimization context"""
        
        spec = state.content_spec
        research = state.research_findings
        planning = state.planning_output
        
        # Extract target keywords
        target_keywords = self._extract_target_keywords(spec, research, planning)
        
        # Determine search intent
        search_intent = self._determine_search_intent(spec, planning)
        
        # Analyze competitors (simplified)
        competitor_analysis = self._analyze_competitors(spec, research)
        
        # Identify optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(state)
        
        return SEOOptimizationContext(
            target_keywords=target_keywords,
            search_intent=search_intent,
            competitor_analysis=competitor_analysis,
            content_optimization_opportunities=optimization_opportunities,
            meta_data_requirements=self._define_meta_requirements(spec, target_keywords),
            internal_linking_strategy=self._plan_internal_linking(spec),
            featured_snippet_opportunities=self._identify_snippet_opportunities(state),
            optimization_confidence=0.78
        )
    
    def _apply_seo_optimizations(self, state: EnrichedContentState, instructions) -> str:
        """Apply SEO optimizations to content"""
        
        content = state.draft_content
        seo_context = state.seo_context
        
        # Optimize title and headers
        content = self._optimize_title_and_headers(content, seo_context)
        
        # Optimize keyword density
        content = self._optimize_keyword_integration(content, seo_context)
        
        # Add semantic keywords
        content = self._add_semantic_keywords(content, seo_context)
        
        # Optimize for featured snippets
        content = self._optimize_for_snippets(content, seo_context)
        
        # Add internal linking suggestions
        content = self._add_internal_linking(content, seo_context)
        
        return content
    
    def _extract_target_keywords(self, spec, research, planning) -> list:
        """Extract target keywords from context"""
        
        keywords = []
        
        # Primary keyword from topic
        keywords.append(spec.topic.lower())
        
        # Keywords from research trending topics
        if research and research.trending_topics:
            keywords.extend([topic.lower() for topic in research.trending_topics[:3]])
        
        # Keywords from planning key messages
        if planning and planning.key_messages:
            for message in planning.key_messages:
                # Extract key terms
                words = message.lower().split()
                important_words = [word for word in words if len(word) > 5]
                keywords.extend(important_words[:2])
        
        # Industry and audience keywords
        keywords.append(spec.business_context.get("industry", "business").lower())
        keywords.append(spec.audience.lower().replace("_", " "))
        
        # Template-specific keywords
        if spec.template_type == "business_proposal":
            keywords.extend(["roi", "implementation", "strategy", "investment"])
        elif spec.template_type == "technical_documentation":
            keywords.extend(["implementation", "guide", "technical", "documentation"])
        
        return list(set(keywords))[:10]  # Limit and deduplicate
    
    def _determine_search_intent(self, spec, planning) -> str:
        """Determine primary search intent"""
        
        if spec.template_type == "business_proposal":
            return "commercial"  # Users looking to invest/buy
        elif "guide" in spec.topic.lower() or "how" in spec.topic.lower():
            return "informational"  # Users seeking information
        elif planning and "implementation" in str(planning.key_messages).lower():
            return "transactional"  # Users ready to act
        else:
            return "informational"
    
    def _analyze_competitors(self, spec, research) -> dict:
        """Analyze competitor content (simplified)"""
        
        analysis = {
            "direct_competitors": [],
            "content_gaps": [],
            "opportunity_keywords": []
        }
        
        if research and research.competitive_landscape:
            competitors = research.competitive_landscape.get("direct_competitors", [])
            analysis["direct_competitors"] = competitors
            
            # Identify content gaps
            if research.research_gaps:
                analysis["content_gaps"] = research.research_gaps
            
            # Opportunity keywords from differentiation
            differentiators = research.competitive_landscape.get("differentiation_opportunities", [])
            analysis["opportunity_keywords"] = [diff.lower() for diff in differentiators]
        
        return analysis
    
    def _identify_optimization_opportunities(self, state: EnrichedContentState) -> list:
        """Identify content optimization opportunities"""
        
        opportunities = []
        content = state.draft_content
        spec = state.content_spec
        
        # Check title optimization
        if not any(keyword in content[:100].lower() for keyword in [spec.topic.lower()]):
            opportunities.append("Optimize title with primary keyword")
        
        # Check header structure
        import re
        headers = re.findall(r'^#+\s+(.+)', content, re.MULTILINE)
        # (The following lines appear to be misplaced and should be part of another function, not here.)
        # Remove the accidentally inserted lines that do not belong to this function.
    
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
        return sections
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

