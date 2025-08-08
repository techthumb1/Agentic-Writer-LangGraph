# File: langgraph_app/agents/enhanced_seo_integrated.py
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    SEOOptimizationContext
)

class EnhancedSEOAgent:
    """Integrated SEO Agent using EnrichedContentState with Template Configuration Support"""
    
    def __init__(self):
        self.agent_type = AgentType.SEO
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute SEO optimization with content context and template configuration"""
        
        # TEMPLATE INJECTION: Extract template_config
        template_config = getattr(state, 'template_config', {})
        if not template_config and hasattr(state, 'content_spec'):
            template_config = state.content_spec.business_context.get('template_config', {})
        
        print(f"DEBUG seo template_config: {template_config}")
        
        # Get dynamic instructions
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "platform": state.content_spec.platform,
            "has_research_context": bool(state.research_findings),
            "content_length": len(state.draft_content.split()),
            "template_config_found": bool(template_config),
            "template_type": template_config.get('template_type', 'default')
        })
        
        # Create SEO optimization context with template awareness
        seo_context = self._create_seo_context(state, instructions, template_config)
        state.seo_context = seo_context
        
        # Apply SEO optimizations with template configuration
        optimized_content = self._apply_seo_optimizations(state, instructions, template_config)
        state.draft_content = optimized_content
        
        # Update phase
        state.update_phase(ContentPhase.PUBLISHING)
        
        # Log completion
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "keywords_optimized": len(seo_context.target_keywords),
            "confidence_score": seo_context.optimization_confidence,
            "optimization_opportunities": len(seo_context.content_optimization_opportunities),
            "template_seo_applied": True
        })
        
        return state
    
    def _create_seo_context(self, state: EnrichedContentState, instructions, template_config: dict) -> SEOOptimizationContext:
        """Create SEO optimization context with template configuration"""
        
        spec = state.content_spec
        research = state.research_findings
        planning = state.planning_output
        
        # Extract target keywords with template priority
        target_keywords = self._extract_target_keywords(spec, research, planning, template_config)
        
        # Determine search intent with template context
        search_intent = self._determine_search_intent(spec, planning, template_config)
        
        # Analyze competitors with template awareness
        competitor_analysis = self._analyze_competitors(spec, research, template_config)
        
        # Identify optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(state, template_config)
        
        return SEOOptimizationContext(
            target_keywords=target_keywords,
            search_intent=search_intent,
            competitor_analysis=competitor_analysis,
            content_optimization_opportunities=optimization_opportunities,
            meta_data_requirements=self._define_meta_requirements(spec, target_keywords, template_config),
            internal_linking_strategy=self._plan_internal_linking(spec, template_config),
            featured_snippet_opportunities=self._identify_snippet_opportunities(state, template_config),
            optimization_confidence=0.78
        )
    
    def _extract_target_keywords(self, spec, research, planning, template_config: dict) -> list:
        """Extract keywords with template configuration taking precedence"""
        
        keywords = []
        
        # TEMPLATE ENFORCEMENT: Use template-specific keywords first
        if template_config.get('seo_keywords'):
            keywords.extend(template_config['seo_keywords'])
            print(f"DEBUG: Added template SEO keywords: {template_config['seo_keywords']}")
        
        # Template-type specific keywords
        template_type = template_config.get('template_type', spec.template_type)
        
        if template_type == "venture_capital_pitch":
            template_keywords = [
                "venture capital funding",
                "startup investment opportunity", 
                "Series A funding",
                "startup pitch deck",
                "VC investment thesis",
                "startup traction metrics",
                "venture funding round"
            ]
            keywords.extend(template_keywords)
            print("DEBUG: Added VC pitch keywords")
            
        elif template_type == "business_proposal":
            template_keywords = [
                "business proposal template",
                "ROI analysis framework",
                "strategic implementation plan",
                "business case development",
                "investment proposal strategy",
                "business growth strategy"
            ]
            keywords.extend(template_keywords)
            print("DEBUG: Added business proposal keywords")
            
        elif template_type == "technical_documentation":
            template_keywords = [
                "technical documentation guide",
                "API implementation tutorial",
                "software architecture patterns",
                "technical specifications",
                "developer documentation",
                "implementation best practices"
            ]
            keywords.extend(template_keywords)
            print("DEBUG: Added technical doc keywords")
        
        # Primary keyword from topic
        keywords.append(spec.topic.lower())
        
        # Keywords from research trending topics
        if research and research.trending_topics:
            research_keywords = [topic.lower() for topic in research.trending_topics[:3]]
            keywords.extend(research_keywords)
        
        # Keywords from planning key messages
        if planning and planning.key_messages:
            for message in planning.key_messages:
                # Extract key terms (longer than 5 characters)
                words = message.lower().split()
                important_words = [word for word in words if len(word) > 5]
                keywords.extend(important_words[:2])
        
        # Industry and audience keywords
        industry = spec.business_context.get("industry", "business")
        keywords.extend([industry.lower(), spec.audience.lower().replace("_", " ")])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen and len(keyword) > 2:  # Filter out very short keywords
                unique_keywords.append(keyword)
                seen.add(keyword)
        
        return unique_keywords[:15]  # Limit to top 15 keywords
    
    def _determine_search_intent(self, spec, planning, template_config: dict) -> str:
        """Determine primary search intent with template context"""
        
        template_type = template_config.get('template_type', spec.template_type)
        
        # Template-specific search intents
        if template_type == "venture_capital_pitch":
            return "commercial_funding"  # Users looking for investment information
        elif template_type == "business_proposal":
            return "commercial_implementation"  # Users looking to implement solutions
        elif template_type == "technical_documentation":
            return "informational_implementation"  # Users seeking implementation guidance
        
        # Fallback to content analysis
        if "guide" in spec.topic.lower() or "how" in spec.topic.lower():
            return "informational"
        elif planning and "implementation" in str(planning.key_messages).lower():
            return "transactional"
        else:
            return "informational"
    
    def _analyze_competitors(self, spec, research, template_config: dict) -> dict:
        """Analyze competitor content with template awareness"""
        
        analysis = {
            "direct_competitors": [],
            "content_gaps": [],
            "opportunity_keywords": []
        }
        
        template_type = template_config.get('template_type', spec.template_type)
        
        if research and research.competitive_landscape:
            competitors = research.competitive_landscape.get("direct_competitors", [])
            analysis["direct_competitors"] = competitors
            
            # Identify content gaps
            if research.research_gaps:
                analysis["content_gaps"] = research.research_gaps
            
            # Opportunity keywords from differentiation
            differentiators = research.competitive_landscape.get("differentiation_opportunities", [])
            analysis["opportunity_keywords"] = [diff.lower() for diff in differentiators]
        
        # Template-specific competitive analysis
        if template_type == "venture_capital_pitch":
            analysis["vc_specific_gaps"] = [
                "Limited traction data transparency",
                "Weak market size validation", 
                "Unclear competitive moats"
            ]
            analysis["vc_opportunity_keywords"] = [
                "proven traction metrics",
                "defensible market position",
                "scalable business model"
            ]
        elif template_type == "business_proposal":
            analysis["business_specific_gaps"] = [
                "Insufficient ROI documentation",
                "Weak implementation roadmaps",
                "Limited risk assessment"
            ]
            analysis["business_opportunity_keywords"] = [
                "measurable ROI outcomes",
                "proven implementation success",
                "comprehensive risk mitigation"
            ]
        
        return analysis
    
    def _identify_optimization_opportunities(self, state: EnrichedContentState, template_config: dict) -> list:
        """Identify content optimization opportunities with template awareness"""
        
        opportunities = []
        content = state.draft_content
        spec = state.content_spec
        template_type = template_config.get('template_type', spec.template_type)
        
        # Template-specific optimization opportunities
        if template_type == "venture_capital_pitch":
            opportunities.extend([
                "Optimize for 'venture capital' keyword variations",
                "Add traction metrics for featured snippets",
                "Include funding stage terminology",
                "Optimize team section for investor searches",
                "Add exit strategy keywords"
            ])
        elif template_type == "business_proposal":
            opportunities.extend([
                "Optimize for 'ROI' and financial keywords", 
                "Add implementation timeline for project searches",
                "Include business case terminology",
                "Optimize for strategic planning searches",
                "Add risk management keywords"
            ])
        elif template_type == "technical_documentation":
            opportunities.extend([
                "Optimize for technical implementation searches",
                "Add code examples for developer queries",
                "Include API reference keywords",
                "Optimize for troubleshooting searches",
                "Add best practices terminology"
            ])
        
        # Check title optimization
        primary_keyword = template_config.get('seo_keywords', [spec.topic.lower()])[0] if template_config.get('seo_keywords') else spec.topic.lower()
        if primary_keyword not in content[:100].lower():
            opportunities.append(f"Add primary keyword '{primary_keyword}' to title/introduction")
        
        # Check header structure
        import re
        headers = re.findall(r'^#+\s+(.+)', content, re.MULTILINE)
        if len(headers) < 3:
            opportunities.append("Add more subheadings for better content structure")
        
        # Check content length for template
        word_count = len(content.split())
        optimal_length = template_config.get('optimal_word_count', 2000)
        
        if word_count < optimal_length * 0.8:
            opportunities.append(f"Expand content to reach optimal length ({optimal_length} words)")
        elif word_count > optimal_length * 1.2:
            opportunities.append(f"Consider condensing content for better readability")
        
        return opportunities
    
    def _apply_seo_optimizations(self, state: EnrichedContentState, instructions, template_config: dict) -> str:
        """Apply SEO optimizations to content with template configuration"""
        
        content = state.draft_content
        seo_context = state.seo_context
        template_type = template_config.get('template_type', state.content_spec.template_type)
        
        # Apply template-specific SEO optimizations
        content = self._apply_template_seo_optimizations(content, template_config)
            
        # Optimize title and headers
        content = self._optimize_title_and_headers(content, seo_context, template_config)
        
        # Optimize keyword density with template awareness
        content = self._optimize_keyword_integration(content, seo_context, template_config)
        
        # Add semantic keywords
        content = self._add_semantic_keywords(content, seo_context, template_config)
        
        # Optimize for featured snippets
        content = self._optimize_for_snippets(content, seo_context, template_config)
        
        # Add internal linking suggestions
        content = self._add_internal_linking(content, seo_context, template_config)
        
        return content
    
    def _apply_template_seo_optimizations(self, content: str, template_config: dict) -> str:
        # Use template-defined SEO modifications if available
        if template_config.get('seo_content_modifications'):
            modifications = template_config['seo_content_modifications']

            for modification in modifications:
                if modification.get('type') == 'keyword_emphasis':
                    keyword = modification.get('keyword')
                    if keyword and keyword.lower() in content.lower():
                        import re
                        pattern = r'\b(' + re.escape(keyword) + r')\b'
                        content = re.sub(pattern, f'**{keyword}**', content, flags=re.IGNORECASE, count=1)

                elif modification.get('type') == 'section_addition':
                    section_title = modification.get('section_title')
                    section_content = modification.get('section_content', '')
                    if section_title and section_title not in content:
                        content += f"\n\n## {section_title}\n\n{section_content}"

        return content

    def _optimize_title_and_headers(self, content: str, seo_context: SEOOptimizationContext, template_config: dict) -> str:
        """Optimize title and headers with template keywords"""
        
        primary_keyword = seo_context.target_keywords[0] if seo_context.target_keywords else "analysis"
        
        # Optimize main title
        import re
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        if title_match and primary_keyword.lower() not in title_match.group(1).lower():
            optimized_title = f"# {primary_keyword.title()}: {title_match.group(1)}"
            content = content.replace(title_match.group(0), optimized_title, 1)
        
        # Optimize headers with secondary keywords
        headers = re.findall(r'^##\s+(.+)', content, re.MULTILINE)
        secondary_keywords = seo_context.target_keywords[1:4] if len(seo_context.target_keywords) > 1 else []
        
        for i, header in enumerate(headers[:len(secondary_keywords)]):
            keyword = secondary_keywords[i]
            if keyword.lower() not in header.lower():
                optimized_header = f"## {keyword.title()} in {header}"
                content = content.replace(f"## {header}", optimized_header, 1)
        
        return content
    
    def _optimize_keyword_integration(self, content: str, seo_context: SEOOptimizationContext, template_config: dict) -> str:
        """Optimize keyword integration with natural placement"""
        
        target_keywords = seo_context.target_keywords
        template_type = template_config.get('template_type')
        
        # Calculate target keyword density (1-3% for primary keyword)
        word_count = len(content.split())
        primary_keyword = target_keywords[0] if target_keywords else ""
        
        if primary_keyword:
            current_occurrences = content.lower().count(primary_keyword.lower())
            target_occurrences = max(2, int(word_count * 0.02))  # 2% density
            
            if current_occurrences < target_occurrences:
                # Add keyword naturally in template-appropriate contexts
                additions_needed = target_occurrences - current_occurrences
                
                if template_type == "venture_capital_pitch":
                    keyword_phrases = [
                        f"This {primary_keyword} opportunity represents",
                        f"The {primary_keyword} market shows",
                        f"Our {primary_keyword} solution delivers"
                    ]
                elif template_type == "business_proposal":
                    keyword_phrases = [
                        f"The {primary_keyword} implementation will",
                        f"This {primary_keyword} strategy ensures",
                        f"The {primary_keyword} approach provides"
                    ]
                else:
                    keyword_phrases = [
                        f"The {primary_keyword} analysis reveals",
                        f"This {primary_keyword} framework enables",
                        f"The {primary_keyword} methodology ensures"
                    ]
                
                # Add phrases naturally to content
                for i, phrase in enumerate(keyword_phrases[:additions_needed]):
                    if phrase.lower() not in content.lower():
                        # Find appropriate insertion point
                        paragraphs = content.split('\n\n')
                        if len(paragraphs) > i + 2:
                            paragraphs[i + 2] = f"{phrase} enhanced value. " + paragraphs[i + 2]
                            content = '\n\n'.join(paragraphs)
        
        return content
    
    def _add_semantic_keywords(self, content: str, seo_context: SEOOptimizationContext, template_config: dict) -> str:
        """Add semantic keywords related to main topics"""
        
        template_type = template_config.get('template_type')
        primary_keyword = seo_context.target_keywords[0] if seo_context.target_keywords else ""
        
        # Template-specific semantic keywords
        semantic_keywords = []
        
        if template_type == "venture_capital_pitch":
            semantic_keywords = [
                "investment thesis", "market validation", "scalable business model",
                "competitive advantage", "traction metrics", "funding requirements"
            ]
        elif template_type == "business_proposal":
            semantic_keywords = [
                "strategic initiative", "business value", "implementation roadmap",
                "risk mitigation", "performance metrics", "stakeholder alignment"
            ]
        elif template_type == "technical_documentation":
            semantic_keywords = [
                "technical architecture", "implementation guide", "best practices",
                "performance optimization", "security considerations", "scalability"
            ]
        
        # Add semantic keywords naturally
        for keyword in semantic_keywords[:3]:  # Limit to 3 semantic keywords
            if keyword.lower() not in content.lower():
                # Find strategic location to add semantic keyword
                if "## " in content:
                    sections = content.split("## ")
                    if len(sections) > 2:
                        # Add to second section
                        sections[2] = f"{keyword.title()} analysis shows that " + sections[2]
                        content = "## ".join(sections)
                        break
        
        return content
    
    def _optimize_for_snippets(self, content: str, seo_context: SEOOptimizationContext, template_config: dict) -> str:
        """Optimize content for featured snippets"""
        
        template_type = template_config.get('template_type')
        
        # Add FAQ-style content for snippet optimization
        if template_type == "venture_capital_pitch":
            snippet_content = """
## Frequently Asked Questions

**What is the investment opportunity?**
This venture capital opportunity presents a scalable business model with proven traction metrics and clear path to profitability.

**What are the key traction metrics?**
The company demonstrates strong month-over-month growth with validated product-market fit and increasing customer acquisition.

**What is the funding requirement?**
The funding round seeks strategic investment to accelerate growth and market expansion initiatives.
"""
        elif template_type == "business_proposal":
            snippet_content = """
## Key Implementation Questions

**What is the expected ROI?**
The proposed implementation delivers measurable return on investment through operational efficiency and strategic value creation.

**What is the implementation timeline?**
The strategic implementation follows a phased approach with clear milestones and measurable outcomes.

**What are the success metrics?**
Success is measured through performance indicators including cost reduction, efficiency gains, and strategic objective achievement.
"""
        elif template_type == "technical_documentation":
            snippet_content = """
## Quick Reference

**How to implement this solution?**
The implementation follows industry best practices with clear technical specifications and step-by-step guidance.

**What are the system requirements?**
The solution requires standard enterprise infrastructure with documented performance and security specifications.

**What support is available?**
Comprehensive documentation, code examples, and technical support ensure successful implementation.
"""
        else:
            snippet_content = ""
        
        if snippet_content and "## Frequently Asked Questions" not in content:
            content += snippet_content
        
        return content
    
    def _add_internal_linking(self, content: str, seo_context: SEOOptimizationContext, template_config: dict) -> str:
        """Add internal linking suggestions with template awareness"""
        
        template_type = template_config.get('template_type')
        
        linking_suggestions = []
        
        if template_type == "venture_capital_pitch":
            linking_suggestions = [
                "Related: [Venture Capital Due Diligence Guide](#)",
                "See also: [Startup Traction Metrics Framework](#)",
                "More info: [Investment Term Sheet Template](#)"
            ]
        elif template_type == "business_proposal":
            linking_suggestions = [
                "Related: [ROI Calculation Framework](#)",
                "See also: [Implementation Best Practices](#)",
                "More info: [Strategic Planning Template](#)"
            ]
        elif template_type == "technical_documentation":
            linking_suggestions = [
                "Related: [API Documentation](#)",
                "See also: [Implementation Examples](#)",
                "More info: [Troubleshooting Guide](#)"
            ]
        
        # Add linking suggestions at the end
        if linking_suggestions:
            content += "\n\n## Related Resources\n\n"
            for suggestion in linking_suggestions:
                content += f"- {suggestion}\n"
        
        return content
    
    def _define_meta_requirements(self, spec, target_keywords: list, template_config: dict) -> dict:
        """Define meta data requirements with template awareness"""
        
        template_type = template_config.get('template_type', spec.template_type)
        primary_keyword = target_keywords[0] if target_keywords else spec.topic
        
        meta_requirements = {
            "title": template_config.get('seo_title', f"{primary_keyword.title()} - Comprehensive Analysis"),
            "description": template_config.get('seo_description', f"Expert analysis of {primary_keyword} with actionable insights"),
            "keywords": ", ".join(target_keywords[:10]),
            "og_title": f"{primary_keyword.title()} Strategic Analysis",
            "og_description": f"Professional insights and analysis for {spec.audience}",
            "canonical_url": f"/{primary_keyword.lower().replace(' ', '-')}-analysis"
        }
        
        # Template-specific meta requirements
        if template_type == "venture_capital_pitch":
            meta_requirements.update({
                "article_type": "investment_analysis",
                "target_audience": "investors, venture_capitalists, startup_founders",
                "content_category": "venture_capital",
                "investment_stage": template_config.get('funding_stage', 'Series A')
            })
        elif template_type == "business_proposal":
            meta_requirements.update({
                "article_type": "business_strategy",
                "target_audience": "business_executives, decision_makers, consultants", 
                "content_category": "business_strategy",
                "proposal_type": "strategic_implementation"
            })
        elif template_type == "technical_documentation":
            meta_requirements.update({
                "article_type": "technical_guide",
                "target_audience": "developers, technical_teams, engineers",
                "content_category": "technical_documentation",
                "difficulty_level": "intermediate_to_advanced"
            })
        
        return meta_requirements
    
    def _plan_internal_linking(self, spec, template_config: dict) -> list:
        """Plan internal linking strategy with template awareness"""
        
        template_type = template_config.get('template_type', spec.template_type)
        
        if template_type == "venture_capital_pitch":
            return [
                "Link to market research methodologies",
                "Connect to traction metrics frameworks",
                "Reference investment thesis templates",
                "Link to due diligence checklists",
                "Connect to exit strategy analysis"
            ]
        elif template_type == "business_proposal":
            return [
                "Link to ROI calculation tools",
                "Connect to implementation frameworks",
                "Reference strategic planning guides",
                "Link to risk assessment templates",
                "Connect to performance measurement systems"
            ]
        elif template_type == "technical_documentation":
            return [
                "Link to API documentation",
                "Connect to code repositories",
                "Reference architecture patterns", 
                "Link to troubleshooting guides",
                "Connect to best practices documents"
            ]
        
        return ["Link to related analyses", "Connect to methodology guides"]
    
    def _identify_snippet_opportunities(self, state: EnrichedContentState, template_config: dict) -> list:
        """Identify featured snippet opportunities with template awareness"""
        
        template_type = template_config.get('template_type', state.content_spec.template_type)
        
        if template_type == "venture_capital_pitch":
            return [
                "Investment opportunity definition",
                "Traction metrics explanation",
                "Market size calculation methods",
                "Funding requirements breakdown",
                "Investment timeline overview"
            ]
        elif template_type == "business_proposal":
            return [
                "ROI calculation methodology",
                "Implementation timeline steps",
                "Risk mitigation strategies",
                "Success metrics definition",
                "Business case components"
            ]
        elif template_type == "technical_documentation":
            return [
                "Implementation step-by-step guide",
                "System requirements list",
                "Configuration examples",
                "Troubleshooting procedures",
                "Best practices checklist"
            ]
        
        return [
            "Key concept definitions",
            "Step-by-step procedures",
            "Best practices lists"
        ]
    
EnhancedSeoAgent = EnhancedSEOAgent

__all__ = ['EnhancedSEOAgent', 'EnhancedSeoAgent']