# File: langgraph_app/agents/writer_integrated.py
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    WritingContext
)

class IntegratedWriterAgent:
    """Integrated Writer Agent using EnrichedContentState"""
    
    def __init__(self):
        self.agent_type = AgentType.WRITER
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute writing with full context from planning and research"""
        
        # Get dynamic instructions
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "has_planning_context": bool(state.planning_output),
            "has_research_context": bool(state.research_findings),
            "target_length": instructions.specific_requirements.get("target_length", 1200)
        })
        
        # Generate writing context
        writing_context = self._create_writing_context(state, instructions)
        state.writing_context = writing_context
        
        # Generate content using full context
        draft_content = self._generate_content_with_context(state, instructions)
        state.draft_content = draft_content
        
        # Update phase
        state.update_phase(ContentPhase.EDITING)
        
        # Log completion
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "content_length": len(draft_content.split()),
            "confidence_score": writing_context.writing_confidence,
            "sections_created": len(self._extract_sections(draft_content))
        })
        
        return state
    
    def _create_writing_context(self, state: EnrichedContentState, instructions) -> WritingContext:
        """Create rich writing context from all available information"""
        
        # Extract context from planning and research
        planning = state.planning_output
        research = state.research_findings
        spec = state.content_spec
        
        # Adapt tone based on audience and research findings
        tone_adaptation = self._calculate_tone_adaptation(spec, planning, research)
        
        # Select narrative approach based on strategy
        narrative_approach = planning.content_strategy if planning else "adaptive_narrative"
        
        # Determine technical depth from complexity and audience
        technical_depth = self._determine_technical_depth(spec, research)
        
        # Select innovation techniques based on level and context
        innovation_techniques = self._select_innovation_techniques(spec, instructions)
        
        return WritingContext(
            tone_adaptation=tone_adaptation,
            voice_characteristics=self._define_voice_characteristics(spec, planning),
            narrative_approach=narrative_approach,
            technical_depth=technical_depth,
            innovation_techniques=innovation_techniques,
            content_hooks=self._generate_content_hooks(planning, research),
            section_priorities=self._prioritize_sections(planning),
            writing_confidence=0.85
        )
    
    def _generate_content_with_context(self, state: EnrichedContentState, instructions) -> str:
        """Generate content using full contextual awareness"""
        
        planning = state.planning_output
        research = state.research_findings
        writing_context = state.writing_context
        spec = state.content_spec
        
        # Build content based on planned structure and research insights
        content_sections = []
        
        if planning and planning.estimated_sections:
            for section in planning.estimated_sections:
                section_content = self._generate_section(
                    section, spec, planning, research, writing_context, instructions
                )
                content_sections.append(section_content)
        else:
            # Fallback structure
            content_sections = self._generate_default_structure(
                spec, planning, research, writing_context, instructions
            )
        
        return "\n\n".join(content_sections)
    
    def _generate_section(self, section_config: dict, spec, planning, research, context, instructions) -> str:
        """Generate individual section with contextual awareness"""
        
        section_name = section_config.get("name", "Section")
        target_words = section_config.get("estimated_words", 200)
        
        # Section-specific content generation
        if "executive" in section_name.lower() or "summary" in section_name.lower():
            return self._generate_executive_summary(spec, planning, research, target_words)
        elif "problem" in section_name.lower() or "opportunity" in section_name.lower():
            return self._generate_problem_section(spec, planning, research, target_words)
        elif "solution" in section_name.lower() or "value" in section_name.lower():
            return self._generate_solution_section(spec, planning, research, target_words)
        elif "financial" in section_name.lower() or "roi" in section_name.lower():
            return self._generate_financial_section(spec, planning, research, target_words)
        elif "implementation" in section_name.lower() or "timeline" in section_name.lower():
            return self._generate_implementation_section(spec, planning, research, target_words)
        else:
            return self._generate_generic_section(section_name, spec, planning, research, target_words)
    
    def _generate_executive_summary(self, spec, planning, research, target_words: int) -> str:
        """Generate executive summary with strategic context"""
        
        content = f"# Executive Summary\n\n"
        
        # Problem statement from planning
        if planning and planning.key_messages:
            problem = planning.key_messages[0] if planning.key_messages else spec.topic
            content += f"**Strategic Opportunity:** {problem} presents a significant market opportunity "
        else:
            content += f"**Strategic Opportunity:** {spec.topic} represents a critical business imperative "
        
        # Market context from research
        if research and research.supporting_data.get("market_data"):
            market_info = research.supporting_data["market_data"]
            content += f"within a {market_info.get('market_size', 'substantial')} market growing at {market_info.get('growth_rate', 'significant')} annually.\n\n"
        else:
            content += f"in the rapidly evolving {spec.business_context.get('industry', 'technology')} sector.\n\n"
        
        # Solution overview
        content += f"**Proposed Solution:** Our {spec.innovation_level} approach leverages "
        if research and research.trending_topics:
            content += f"emerging trends in {', '.join(research.trending_topics[:2])} "
        content += f"to deliver measurable business impact for {spec.audience}.\n\n"
        
        # Financial summary from research
        if research and research.supporting_data.get("financial_metrics"):
            financial = research.supporting_data["financial_metrics"]
            content += f"**Financial Impact:** Expected ROI of {financial.get('roi_benchmarks', '25%')} "
            content += f"with implementation investment of {financial.get('implementation_cost', '$500K')} "
            content += f"and projected savings of {financial.get('cost_savings', '$1M')} annually.\n\n"
        
        # Call to action based on audience
        if "investor" in spec.audience.lower():
            content += "**Investment Opportunity:** This proposal outlines a compelling investment thesis with clear metrics for success and scalable growth potential."
        elif "executive" in spec.audience.lower():
            content += "**Strategic Recommendation:** Immediate implementation is recommended to capitalize on market timing and competitive advantages."
        else:
            content += "**Next Steps:** This proposal provides a comprehensive framework for strategic decision-making and implementation planning."
        
        return content
    
    def _generate_problem_section(self, spec, planning, research, target_words: int) -> str:
        """Generate problem/opportunity section with research backing"""
        
        content = f"# Problem Statement & Market Opportunity\n\n"
        
        # Industry context from research
        if research and research.industry_context:
            industry = research.industry_context
            content += f"**Industry Context:** The {industry.get('industry', spec.business_context.get('industry', 'technology'))} sector "
            content += f"faces significant challenges including {', '.join(industry.get('key_challenges', ['operational inefficiencies', 'competitive pressures']))}. "
            content += f"However, emerging opportunities in {', '.join(industry.get('opportunities', ['digital transformation', 'market expansion']))} "
            content += "create unprecedented potential for strategic advantage.\n\n"
        
        # Market analysis from research
        if research and research.supporting_data.get("market_data"):
            market = research.supporting_data["market_data"]
            content += f"**Market Analysis:** Current market dynamics reveal a {market.get('market_size', 'substantial')} opportunity "
            content += f"with {market.get('growth_rate', 'strong')} growth trajectory. Key trends driving this growth include:\n"
            for trend in market.get("key_trends", ["Digital transformation", "Efficiency optimization"]):
                content += f"- {trend}\n"
            content += "\n"
        
        # Competitive landscape from research
        if research and research.competitive_landscape:
            competitive = research.competitive_landscape
            content += f"**Competitive Landscape:** Analysis reveals {len(competitive.get('direct_competitors', []))} direct competitors "
            content += f"and {len(competitive.get('indirect_competitors', []))} alternative solutions. "
            content += f"Key differentiation opportunities include {', '.join(competitive.get('differentiation_opportunities', ['innovation', 'efficiency']))}.\n\n"
        
        # Target audience pain points from planning
        if planning and planning.audience_insights:
            insights = planning.audience_insights
            content += f"**Target Audience Analysis:** {insights.get('primary_audience', spec.audience)} "
            content += f"prioritizes {', '.join(insights.get('decision_factors', ['ROI', 'reliability', 'scalability']))} "
            content += f"when evaluating solutions. Current pain points include operational inefficiencies, "
            content += "resource constraints, and competitive pressure to innovate.\n\n"
        
        # Quantified opportunity
        content += f"**Quantified Opportunity:** Based on market analysis and industry benchmarks, "
        content += f"addressing these challenges represents a measurable opportunity for "
        if research and research.supporting_data.get("financial_metrics"):
            financial = research.supporting_data["financial_metrics"]
            content += f"{financial.get('cost_savings', 'significant cost savings')} annually "
            content += f"with {financial.get('roi_benchmarks', 'strong ROI potential')}."
        else:
            content += "substantial operational improvement and competitive advantage."
        
        return content
    
    def _generate_solution_section(self, spec, planning, research, target_words: int) -> str:
        """Generate solution section with strategic positioning"""
        
        content = f"# Proposed Solution & Value Proposition\n\n"
        
        # Strategic approach from planning
        if planning:
            content += f"**Strategic Approach:** Our {planning.content_strategy} leverages "
            content += f"{spec.innovation_level} methodology to deliver {planning.competitive_positioning} "
            content += f"in the {spec.business_context.get('industry', 'technology')} market.\n\n"
        
        # Core solution description
        content += f"**Core Solution:** The proposed {spec.topic} solution addresses identified market needs through:\n"
        
        # Key messages from planning
        if planning and planning.key_messages:
            for message in planning.key_messages[:4]:
                content += f"- {message}\n"
        else:
            content += f"- Innovative approach to {spec.topic}\n"
            content += f"- Scalable implementation methodology\n"
            content += f"- Measurable business impact\n"
        content += "\n"
        
        # Technical implementation
        content += f"**Technical Implementation:** Solution design incorporates {spec.complexity_level}/10 "
        content += f"technical sophistication appropriate for {spec.audience}. "
        
        if research and research.trending_topics:
            content += f"Implementation leverages current trends in {', '.join(research.trending_topics[:2])} "
            content += "to ensure competitive advantage and future-proofing.\n\n"
        
        # Competitive advantages from research
        if research and research.competitive_landscape:
            advantages = research.competitive_landscape.get("differentiation_opportunities", [])
            content += f"**Competitive Advantages:**\n"
            for advantage in advantages[:3]:
                content += f"- {advantage.title()}\n"
            content += "\n"
        
        # Value proposition
        content += f"**Value Proposition:** This solution delivers measurable value through:\n"
        if research and research.supporting_data.get("case_studies"):
            case_study = research.supporting_data["case_studies"][0]
            content += f"- Proven results: {case_study.get('result', '20% improvement')} achieved by {case_study.get('company', 'leading companies')}\n"
            content += f"- Rapid implementation: {case_study.get('timeline', '6 months')} typical deployment\n"
        
        if research and research.supporting_data.get("financial_metrics"):
            financial = research.supporting_data["financial_metrics"]
            content += f"- Financial impact: {financial.get('roi_benchmarks', '25% ROI')} with {financial.get('cost_savings', 'significant savings')}\n"
        
        content += f"- Strategic alignment with {spec.audience} priorities and business objectives"
        
        return content
    
    def _generate_financial_section(self, spec, planning, research, target_words: int) -> str:
        """Generate financial analysis section"""
        
        content = f"# Financial Projections & ROI Analysis\n\n"
        
        if research and research.supporting_data.get("financial_metrics"):
            financial = research.supporting_data["financial_metrics"]
            
            content += f"**Investment Requirements:**\n"
            content += f"- Initial implementation: {financial.get('implementation_cost', '$500K')}\n"
            content += f"- Ongoing operational costs: 20% of initial investment annually\n"
            content += f"- Total 3-year investment: Estimated $750K including optimization\n\n"
            
            content += f"**Revenue Impact:**\n"
            content += f"- Annual cost savings: {financial.get('cost_savings', '$1M')}\n"
            content += f"- Revenue enhancement: 15% improvement in operational efficiency\n"
            content += f"- ROI timeline: {financial.get('roi_benchmarks', '25%')} return within 18 months\n\n"
            
            content += f"**Financial Projections (3-Year):**\n"
            content += f"- Year 1: Break-even with initial cost savings\n"
            content += f"- Year 2: {financial.get('cost_savings', '$1M')} net positive impact\n"
            content += f"- Year 3: Cumulative ROI exceeding 200%\n\n"
        else:
            content += f"**Investment Framework:**\n"
            content += f"- Implementation investment aligned with {spec.audience} budget expectations\n"
            content += f"- Phased approach to minimize risk and maximize early wins\n"
            content += f"- Measurable milestones for ROI validation\n\n"
        
        content += f"**Risk Assessment:**\n"
        content += f"- Implementation risk: Low (proven methodology)\n"
        content += f"- Market risk: Minimal (validated demand)\n"
        content += f"- Technology risk: Controlled (established platforms)\n\n"
        
        content += f"**Success Metrics:**\n"
        if planning and planning.success_metrics:
            for metric, target in planning.success_metrics.items():
                if isinstance(target, (int, float)):
                    content += f"- {metric.replace('_', ' ').title()}: {target * 100:.0f}%\n"
        content += f"- Quarterly business review and optimization cycles\n"
        content += f"- Continuous monitoring and performance adjustment"
        
        return content
    
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