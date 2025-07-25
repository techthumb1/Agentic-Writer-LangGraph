# File: langgraph_app/agents/enhanced_publisher_integrated.py
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    PublishingContext
)
from datetime import datetime

class EnhancedPublisherAgent:
    """Integrated Publisher Agent - Executes comprehensive distribution and publishing strategy"""
    
    def __init__(self):
        self.agent_type = AgentType.PUBLISHER
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute publishing with comprehensive distribution strategy"""
        
        # Get dynamic instructions
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "platform": state.content_spec.platform,
            "content_ready": len(state.draft_content) > 0,
            "seo_optimized": bool(state.seo_context),
            "formatted": bool(state.formatting_requirements)
        })
        
        # Create publishing context
        publishing_context = self._create_publishing_context(state, instructions)
        state.publishing_context = publishing_context
        
        # Prepare final content for publication
        publication_ready_content = self._prepare_for_publication(state, instructions)
        state.final_content = publication_ready_content
        
        # Execute publishing strategy
        publication_results = self._execute_publishing_strategy(state, instructions)
        
        # Update phase to complete
        state.update_phase(ContentPhase.COMPLETE)
        
        # Log completion
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "distribution_channels": len(publishing_context.distribution_channels),
            "confidence_score": publishing_context.publishing_confidence,
            "publication_results": publication_results,
            "final_word_count": len(publication_ready_content.split())
        })
        
        return state
    
    def _create_publishing_context(self, state: EnrichedContentState, instructions) -> PublishingContext:
        """Create comprehensive publishing context"""
        
        spec = state.content_spec
        seo_context = state.seo_context
        formatting_requirements = state.formatting_requirements
        
        # Determine publication platform
        publication_platform = spec.platform
        
        # Plan distribution channels
        distribution_channels = self._plan_distribution_channels(spec, publication_platform)
        
        # Develop promotional strategy
        promotional_strategy = self._develop_promotional_strategy(state)
        
        # Set engagement expectations - FIXED: Added state parameter
        engagement_expectations = self._set_engagement_expectations(state, spec, publication_platform)
        
        return PublishingContext(
            publication_platform=publication_platform,
            scheduling_requirements=self._determine_scheduling(spec),
            distribution_channels=distribution_channels,
            promotional_strategy=promotional_strategy,
            engagement_expectations=engagement_expectations,
            analytics_tracking=self._setup_analytics_tracking(spec),
            follow_up_actions=self._plan_follow_up_actions(state),
            publishing_confidence=0.87
        )
    
    def _prepare_for_publication(self, state: EnrichedContentState, instructions) -> str:
        """Prepare final content for publication"""
        
        content = state.draft_content
        spec = state.content_spec
        publishing_context = state.publishing_context
        
        # Add publication metadata
        content = self._add_publication_metadata(content, state)
        
        # Apply final formatting
        content = self._apply_final_formatting(content, spec.platform)
        
        # Add tracking and analytics
        content = self._add_tracking_elements(content, publishing_context)
        
        # Add call-to-action
        content = self._add_publication_cta(content, spec, publishing_context)
        
        # Add social sharing elements
        content = self._add_social_sharing_elements(content, spec)
        
        return content
    
    def _execute_publishing_strategy(self, state: EnrichedContentState, instructions) -> dict:
        """Execute comprehensive publishing strategy"""
        
        publishing_context = state.publishing_context
        spec = state.content_spec
        
        results = {
            "primary_publication": {
                "platform": publishing_context.publication_platform,
                "status": "ready_for_publication",
                "url_slug": self._generate_url_slug(spec.topic),
                "estimated_reach": self._estimate_reach(state),
                "seo_score": self._calculate_seo_score(state),
                "readability_score": self._calculate_readability_score(state)
            },
            "distribution_channels": [],
            "promotional_campaigns": [],
            "analytics_setup": "configured",
            "performance_projections": self._generate_performance_projections(state)
        }
        
        # Simulate distribution channel results
        for channel in publishing_context.distribution_channels:
            channel_result = {
                "channel": channel,
                "status": "scheduled",
                "estimated_engagement": self._estimate_channel_engagement(channel, state),
                "optimal_timing": self._get_optimal_timing(channel),
                "content_adaptation": self._get_content_adaptation(channel, state)
            }
            results["distribution_channels"].append(channel_result)
        
        # Simulate promotional campaign setup
        for strategy in publishing_context.promotional_strategy:
            campaign_result = {
                "strategy": strategy,
                "status": "configured",
                "expected_impact": self._calculate_strategy_impact(strategy, state),
                "timeline": self._get_strategy_timeline(strategy),
                "success_metrics": self._define_strategy_metrics(strategy)
            }
            results["promotional_campaigns"].append(campaign_result)
        
        return results
    
    def _plan_distribution_channels(self, spec, primary_platform: str) -> list:
        """Plan intelligent multi-channel distribution strategy"""
        
        channels = [primary_platform]  # Primary publication platform
        
        # Add complementary channels based on audience and content type
        if spec.template_type == "business_proposal":
            if "investor" in spec.audience.lower():
                channels.extend([
                    "linkedin_professional",
                    "investment_newsletters", 
                    "industry_publications",
                    "email_direct_outreach"
                ])
            elif "enterprise" in spec.audience.lower():
                channels.extend([
                    "linkedin_company_page",
                    "company_blog",
                    "sales_enablement_portal",
                    "industry_forums"
                ])
        
        elif spec.template_type == "technical_documentation":
            channels.extend([
                "github_documentation",
                "developer_community_sites",
                "technical_forums",
                "api_documentation_portal",
                "developer_newsletters"
            ])
        
        # Industry-specific channels
        industry = spec.business_context.get("industry", "")
        if industry == "technology":
            channels.extend([
                "hacker_news",
                "reddit_programming",
                "dev_to",
                "tech_twitter",
                "medium_publications"
            ])
        elif industry == "finance":
            channels.extend([
                "financial_blogs",
                "fintech_newsletters",
                "industry_publications",
                "linkedin_finance_groups"
            ])
        elif industry == "healthcare":
            channels.extend([
                "healthcare_journals",
                "medical_forums",
                "healthtech_publications"
            ])
        
        # Audience sophistication-based channels
        if spec.complexity_level >= 8:
            channels.extend([
                "expert_communities",
                "academic_networks",
                "professional_associations"
            ])
        
        return list(set(channels))  # Remove duplicates
    
    def _develop_promotional_strategy(self, state: EnrichedContentState) -> list:
        """Develop comprehensive promotional strategy based on content and audience"""
        
        spec = state.content_spec
        planning = state.planning_output
        research = state.research_findings
        seo_context = state.seo_context
        
        strategies = []
        
        # Content-based promotion
        if research and research.primary_insights:
            strategies.extend([
                "Share key insights as social media teasers",
                "Create infographic of main findings",
                "Develop quote cards from expert insights",
                "Extract statistics for standalone posts"
            ])
        
        if research and research.statistical_evidence:
            strategies.append("Create data visualization content")
        
        # Audience-based promotion
        if "executive" in spec.audience.lower():
            strategies.extend([
                "Executive summary email campaign",
                "LinkedIn thought leadership posting",
                "Industry conference presentation",
                "C-suite networking events",
                "Board meeting inclusion"
            ])
        elif "technical" in spec.audience.lower():
            strategies.extend([
                "Developer community sharing",
                "Technical forum discussions",
                "Code repository examples",
                "Technical webinar presentation",
                "Open source community engagement"
            ])
        elif "investor" in spec.audience.lower():
            strategies.extend([
                "Investor newsletter inclusion",
                "Pitch deck integration",
                "Industry analyst briefings",
                "Venture capital network sharing"
            ])
        
        # Platform-specific promotion
        if spec.platform == "linkedin":
            strategies.extend([
                "Professional network engagement",
                "Industry group sharing",
                "Comment engagement strategy",
                "Connection outreach campaign",
                "LinkedIn article series"
            ])
        elif spec.platform == "medium":
            strategies.extend([
                "Publication submission strategy",
                "Cross-platform syndication",
                "Author network promotion",
                "Medium partner program",
                "Clap exchange networks"
            ])
        elif spec.platform == "substack":
            strategies.extend([
                "Subscriber growth campaign",
                "Newsletter cross-promotion",
                "Referral program activation",
                "Guest newsletter features"
            ])
        
        # SEO-driven promotion
        if seo_context and seo_context.target_keywords:
            strategies.extend([
                f"Target keyword: {seo_context.target_keywords[0]} content series",
                "SEO-optimized social media posts",
                "Backlink building campaign",
                "Content cluster development"
            ])
        
        # Innovation-level specific promotion
        if spec.innovation_level == "experimental":
            strategies.extend([
                "Innovation showcase events",
                "Early adopter community engagement",
                "Beta testing program promotion"
            ])
        
        return strategies
    
    def _set_engagement_expectations(self, state: EnrichedContentState, spec, platform: str) -> dict:
        """Set realistic engagement expectations based on multiple factors"""
        
        base_expectations = {
            "linkedin": {
                "views": 1200, "likes": 60, "comments": 8, "shares": 12,
                "click_through_rate": 0.025, "engagement_rate": 0.05
            },
            "medium": {
                "views": 800, "claps": 40, "responses": 6, "highlights": 15,
                "read_ratio": 0.65, "follow_rate": 0.02
            },
            "substack": {
                "opens": 450, "clicks": 45, "subscribers": 8, "forwards": 5,
                "open_rate": 0.42, "click_rate": 0.08
            },
            "company_blog": {
                "views": 950, "time_on_page": 210, "conversions": 12, "bounce_rate": 0.35
            },
            "github": {
                "views": 600, "stars": 15, "forks": 5, "issues": 3
            }
        }
        
        expectations = base_expectations.get(platform, {
            "views": 600, "engagements": 30, "conversion_rate": 0.02
        })
        
        # Adjust based on content quality and confidence
        quality_multiplier = 1.0
        if hasattr(state, 'overall_confidence') and state.overall_confidence:
            if state.overall_confidence > 0.85:
                quality_multiplier = 1.4
            elif state.overall_confidence > 0.75:
                quality_multiplier = 1.2
            elif state.overall_confidence < 0.65:
                quality_multiplier = 0.8
        
        # Adjust based on audience value
        audience_multiplier = 1.0
        if "executive" in spec.audience.lower() or "investor" in spec.audience.lower():
            audience_multiplier = 1.3  # Higher value audience
        elif "technical" in spec.audience.lower() and spec.complexity_level > 7:
            audience_multiplier = 1.2  # Specialized technical content
        
        # Adjust based on content type
        content_multiplier = 1.0
        if spec.template_type == "business_proposal":
            content_multiplier = 1.1  # Business content typically performs well
        elif spec.template_type == "technical_documentation":
            content_multiplier = 0.9  # More niche but targeted audience
        
        # Apply multipliers
        total_multiplier = quality_multiplier * audience_multiplier * content_multiplier
        
        for key, value in expectations.items():
            if isinstance(value, (int, float)):
                expectations[key] = int(value * total_multiplier)
        
        return expectations
    
    def _determine_scheduling(self, spec) -> dict:
        """Determine optimal scheduling strategy"""
        
        scheduling = {
            "optimal_time": "Tuesday 10:00 AM EST",  # Default business optimal
            "timezone": "EST",
            "frequency": "one_time",
            "follow_up_schedule": [],
            "seasonal_considerations": [],
            "audience_timezone_optimization": True
        }
        
        # Platform-specific scheduling
        platform = spec.platform
        if platform == "linkedin":
            scheduling.update({
                "optimal_time": "Tuesday-Thursday 8:00-10:00 AM EST",
                "secondary_time": "Wednesday 1:00-2:00 PM EST",
                "follow_up_schedule": [
                    "1 week follow-up engagement post",
                    "2 weeks industry insight post",
                    "1 month related content"
                ]
            })
        elif platform == "medium":
            scheduling.update({
                "optimal_time": "Sunday 7:00 PM EST",
                "secondary_time": "Wednesday 11:00 AM EST",
                "follow_up_schedule": ["1 week related article", "2 weeks deep dive"]
            })
        elif platform == "substack":
            scheduling.update({
                "optimal_time": "Tuesday 6:00 AM EST",
                "frequency": "weekly",
                "follow_up_schedule": ["Weekly newsletter series", "Monthly digest"]
            })
        elif platform == "github":
            scheduling.update({
                "optimal_time": "Monday 9:00 AM EST",
                "follow_up_schedule": ["Weekly documentation updates", "Monthly feature releases"]
            })
        
        # Audience-specific scheduling
        if "investor" in spec.audience.lower():
            scheduling["optimal_time"] = "Wednesday 9:00 AM EST"  # Business focus
        elif "technical" in spec.audience.lower():
            scheduling["optimal_time"] = "Thursday 2:00 PM EST"  # Developer-friendly
        elif "executive" in spec.audience.lower():
            scheduling["optimal_time"] = "Tuesday 8:00 AM EST"  # Executive schedule
        
        # Industry-specific considerations
        industry = spec.business_context.get("industry", "")
        if industry == "finance":
            scheduling["seasonal_considerations"] = ["Avoid earnings seasons", "Consider market hours"]
        elif industry == "technology":
            scheduling["seasonal_considerations"] = ["Align with tech conferences", "Avoid major releases"]
        
        return scheduling
    
    def _setup_analytics_tracking(self, spec) -> list:
        """Setup comprehensive analytics tracking requirements"""
        
        tracking = [
            "Google Analytics 4 integration",
            "Platform-native analytics",
            "Engagement rate tracking",
            "Conversion funnel tracking",
            "UTM parameter implementation",
            "Cross-platform attribution"
        ]
        
        # Template-specific tracking
        if spec.template_type == "business_proposal":
            tracking.extend([
                "Lead generation tracking",
                "Download/contact form tracking",
                "Investment inquiry tracking",
                "Pitch deck view tracking",
                "Executive engagement metrics"
            ])
        elif spec.template_type == "technical_documentation":
            tracking.extend([
                "Implementation success tracking",
                "Code example usage tracking",
                "Support ticket correlation",
                "Developer adoption metrics",
                "API usage correlation"
            ])
        
        # Platform-specific tracking
        if spec.platform == "linkedin":
            tracking.extend([
                "LinkedIn analytics integration",
                "Professional network growth",
                "Lead generation through LinkedIn",
                "Industry engagement metrics"
            ])
        elif spec.platform == "medium":
            tracking.extend([
                "Medium partner program metrics",
                "Publication performance",
                "Reader retention analysis"
            ])
        elif spec.platform == "github":
            tracking.extend([
                "Repository engagement metrics",
                "Documentation usage tracking",
                "Developer community growth"
            ])
        
        # Audience-specific tracking
        if "investor" in spec.audience.lower():
            tracking.extend([
                "Investor engagement tracking",
                "Due diligence document access",
                "Funding inquiry correlation"
            ])
        
        return tracking
    
    def _plan_follow_up_actions(self, state: EnrichedContentState) -> list:
        """Plan comprehensive follow-up actions based on content and strategy"""
        
        spec = state.content_spec
        planning = state.planning_output
        research = state.research_findings
        
        follow_ups = []
        
        # Content-based follow-ups
        if spec.template_type == "business_proposal":
            follow_ups.extend([
                "Schedule investor follow-up meetings within 48 hours",
                "Prepare detailed financial models for interested parties",
                "Create implementation timeline presentations",
                "Develop due diligence document package",
                "Plan investor update schedule"
            ])
        elif spec.template_type == "technical_documentation":
            follow_ups.extend([
                "Monitor implementation questions and feedback",
                "Update documentation based on user feedback",
                "Create video tutorials for complex sections",
                "Develop advanced implementation guides",
                "Plan developer community engagement"
            ])
        
        # Audience-based follow-ups
        if "investor" in spec.audience.lower():
            follow_ups.extend([
                "Prepare investor Q&A materials",
                "Schedule due diligence preparations",
                "Plan investor demo sessions",
                "Develop investment term sheets"
            ])
        elif "executive" in spec.audience.lower():
            follow_ups.extend([
                "Schedule executive briefing sessions",
                "Prepare board presentation materials",
                "Plan implementation workshops"
            ])
        elif "technical" in spec.audience.lower():
            follow_ups.extend([
                "Plan technical deep-dive sessions",
                "Prepare code review sessions",
                "Develop technical training materials"
            ])
        
        # Platform-based follow-ups
        if spec.platform == "linkedin":
            follow_ups.extend([
                "Engage with comments within 2 hours",
                "Share in relevant industry groups",
                "Connect with engaged commenters",
                "Plan follow-up thought leadership posts"
            ])
        
        # Research-driven follow-ups
        if research and research.research_gaps:
            follow_ups.extend([
                f"Address research gap: {gap}" for gap in research.research_gaps[:2]
            ])
        
        # Universal follow-ups
        follow_ups.extend([
            "Monitor and respond to comments within 24 hours",
            "Engage with shares and mentions across platforms",
            "Track performance metrics weekly for first month",
            "Plan content series based on performance data",
            "Develop repurposing strategy for high-performing content"
        ])
        
        return follow_ups
    
    def _add_publication_metadata(self, content: str, state: EnrichedContentState) -> str:
        """Add comprehensive publication metadata to content"""
        
        spec = state.content_spec
        seo_context = state.seo_context
        planning = state.planning_output
        
        # Collect keywords from various sources
        keywords = []
        if seo_context and seo_context.target_keywords:
            keywords.extend(seo_context.target_keywords[:5])
        if planning and planning.key_messages:
            keywords.extend([msg.lower().replace(' ', '_') for msg in planning.key_messages[:3]])
        
        # Generate comprehensive metadata
        metadata = f"""---
title: "{spec.topic}: Strategic Analysis for {spec.audience}"
description: "Comprehensive {spec.template_type} providing strategic insights and actionable recommendations for {spec.audience}"
author: "Expert Content Team"
date: "{datetime.now().strftime('%Y-%m-%d')}"
category: "{spec.template_type}"
tags: [{', '.join([f'"{tag}"' for tag in keywords[:8]])}]
platform: "{spec.platform}"
audience: "{spec.audience}"
complexity_level: {spec.complexity_level}
innovation_level: "{spec.innovation_level}"
industry: "{spec.business_context.get('industry', 'business')}"
reading_time: "{len(content.split()) // 200 + 1} min"
word_count: {len(content.split())}
template_type: "{spec.template_type}"
content_version: "1.0"
last_updated: "{datetime.now().isoformat()}"
seo_score: "{self._calculate_seo_score(state):.2f}"
confidence_score: "{state.overall_confidence:.2f}" if hasattr(state, 'overall_confidence') else "0.85"
---

"""
        
        return metadata + content
    
    def _apply_final_formatting(self, content: str, platform: str) -> str:
        """Apply final platform-specific formatting"""
        
        if platform == "linkedin":
            # Add LinkedIn-specific elements
            content = content.replace("---\n", "")  # Remove metadata for LinkedIn
            content = "💼 Professional Insight\n\n" + content  # Add professional framing
            
            # Optimize for LinkedIn's algorithm
            content = content.replace("\n\n", "\n\n➤ ")  # Add engagement elements
            
        elif platform == "medium":
            # Ensure proper Medium formatting
            if not content.startswith("# "):
                title_line = content.split('\n')[0]
                content = f"# {title_line}\n\n## Strategic Analysis and Recommendations\n\n{content}"
            
            # Add Medium-specific elements
            content += "\n\n---\n\n*👏 If this analysis provided value, please applaud and share with your network.*"
            
        elif platform == "substack":
            # Add newsletter-style elements
            content = "Welcome to this strategic analysis.\n\n" + content
            content += "\n\n---\n\n**Thank you for reading!** If you found this valuable, please share with your network and subscribe for weekly insights."
            content += "\n\n*Share this post*\n*Subscribe for more*\n*Leave a comment*"
            
        elif platform == "github":
            # Format for technical documentation
            content = f"# Documentation\n\n{content}"
            content += "\n\n## Contributing\n\nContributions are welcome! Please read our contributing guidelines."
            content += "\n\n## License\n\nThis project is licensed under the MIT License."
        
        return content
    
    def _add_tracking_elements(self, content: str, publishing_context: PublishingContext) -> str:
        """Add comprehensive tracking elements for analytics"""
        
        tracking_elements = f"""
<!-- Analytics Tracking Configuration -->
<!-- Platform: {publishing_context.publication_platform} -->
<!-- Distribution Channels: {', '.join(publishing_context.distribution_channels)} -->
<!-- Expected Engagement: {publishing_context.engagement_expectations} -->
<!-- UTM Parameters: utm_source={publishing_context.publication_platform}&utm_medium=content&utm_campaign=strategic_analysis -->
<!-- Conversion Goals: engagement, leads, subscriptions -->
<!-- A/B Testing: enabled for headlines and CTAs -->

"""
        
        return content + tracking_elements
    
    def _add_publication_cta(self, content: str, spec, publishing_context: PublishingContext) -> str:
        """Add comprehensive and targeted call-to-action for publication"""
        
        cta = "\n\n---\n\n"
        
        # Primary CTA based on audience
        if "investor" in spec.audience.lower():
            cta += "**Ready to discuss this investment opportunity?** Contact us to schedule a detailed presentation and explore partnership possibilities."
            cta += "\n\n📧 **Next Steps:**"
            cta += "\n• Schedule a strategy session"
            cta += "\n• Review detailed financial projections"
            cta += "\n• Access due diligence materials"
            
        elif "executive" in spec.audience.lower():
            cta += "**Interested in strategic implementation?** Let's discuss how this approach can be tailored for your organization's specific needs."
            cta += "\n\n🎯 **Executive Actions:**"
            cta += "\n• Schedule executive briefing"
            cta += "\n• Request implementation roadmap"
            cta += "\n• Arrange team consultation"
            
        elif "technical" in spec.audience.lower():
            cta += "**Questions about technical implementation?** Join the discussion in the comments or reach out for detailed technical consultation."
            cta += "\n\n⚡ **Developer Resources:**"
            cta += "\n• Access implementation guides"
            cta += "\n• Join technical community"
            cta += "\n• Request code reviews"
            
        else:
            cta += "**Found this analysis valuable?** Share your thoughts in the comments and connect for more strategic insights."
            cta += "\n\n🚀 **What's Next:**"
            cta += "\n• Share with your network"
            cta += "\n• Subscribe for updates"
            cta += "\n• Join the conversation"
        
        # Platform-specific CTA additions
        if spec.platform == "linkedin":
            cta += "\n\n🔗 **LinkedIn Actions:**"
            cta += "\n• Connect for more insights"
            cta += "\n• Share in your professional network"
            cta += "\n• Comment with your experience"
            
        elif spec.platform == "medium":
            cta += "\n\n📝 **Medium Engagement:**"
            cta += "\n• 👏 Clap if this resonated"
            cta += "\n• 📧 Follow for weekly analysis"
            cta += "\n• 💬 Respond with your thoughts"
            
        elif spec.platform == "substack":
            cta += "\n\n📬 **Newsletter Actions:**"
            cta += "\n• Subscribe for weekly insights"
            cta += "\n• Forward to colleagues"
            cta += "\n• Reply with feedback"
        
        # Secondary engagement CTAs
        cta += "\n\n**Engagement Options:**"
        cta += f"\n• **Questions?** Comment below or reach out directly"
        cta += f"\n• **Collaboration?** Let's explore partnership opportunities"
        cta += f"\n• **Custom Analysis?** Request tailored strategic assessment"
        
        return content + cta
    
    def _add_social_sharing_elements(self, content: str, spec) -> str:
        """Add social sharing optimization elements"""
        
        # Extract key quotes for social sharing
        sharing_elements = f"""
<!-- Social Sharing Optimization -->
<!-- Key Quotes for Social Media: -->
<!-- Quote 1: "Strategic insights for {spec.audience} in {spec.business_context.get('industry', 'business')}" -->
<!-- Quote 2: "Implementation guidance for {spec.topic}" -->
<!-- Quote 3: "Proven methodologies with measurable results" -->

<!-- Hashtag Suggestions: -->
<!-- #{spec.topic.replace(' ', '')} #{spec.audience.replace(' ', '')} #Strategy #Implementation -->

<!-- Social Media Adaptations Ready -->
"""
        
        return content + sharing_elements
    
    def _generate_url_slug(self, topic: str) -> str:
        """Generate SEO-friendly URL slug"""
        import re
        slug = topic.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug.strip('-')
        return slug
    
    def _estimate_reach(self, state: EnrichedContentState) -> dict:
        """Estimate content reach based on quality, targeting, and platform"""
        
        spec = state.content_spec
        base_reach = 1500  # Increased base estimate
        
        # Adjust for content quality and confidence
        if hasattr(state, 'overall_confidence') and state.overall_confidence:
            if state.overall_confidence > 0.85:
                base_reach *= 2.0
            elif state.overall_confidence > 0.75:
                base_reach *= 1.5
            elif state.overall_confidence < 0.65:
                base_reach *= 0.7
        
        # Adjust for audience specificity and value
        if "executive" in spec.audience.lower() or "investor" in spec.audience.lower():
            base_reach *= 0.6  # Smaller but much higher-value audience
        elif "technical" in spec.audience.lower() and spec.complexity_level > 7:
            base_reach *= 0.8  # Specialized but engaged audience
        
        # Adjust for platform reach potential
        platform_multipliers = {
            "linkedin": 1.4,  # Professional network effect
            "medium": 1.0,    # Standard reach
            "substack": 0.7,  # Subscriber-based, lower but more engaged
            "company_blog": 1.1,  # Company amplification
            "github": 0.9     # Developer-focused, niche but engaged
        }
        
        multiplier = platform_multipliers.get(spec.platform, 1.0)
        estimated_reach = int(base_reach * multiplier)
        
        return {
            "estimated_views": estimated_reach,
            "estimated_engagements": int(estimated_reach * 0.08),  # Higher engagement rate
            "estimated_shares": int(estimated_reach * 0.02),
            "estimated_conversions": int(estimated_reach * 0.012),  # Improved conversion
            "estimated_qualified_leads": int(estimated_reach * 0.005)
        }
    
    def _calculate_seo_score(self, state: EnrichedContentState) -> float:
        """Calculate SEO optimization score"""
        
        score = 0.7  # Base score
        
        if state.seo_context:
            score += 0.2  # SEO optimization applied
            
            if len(state.seo_context.target_keywords) >= 3:
                score += 0.05
            
            if state.seo_context.meta_data_requirements:
                score += 0.05
        
        if state.formatting_requirements:
            score += 0.1  # Proper formatting
        
        # Content quality indicators
        content = state.draft_content
        if len(content.split()) > 1000:  # Substantial content
            score += 0.05
        
        if content.count('#') >= 3:  # Good header structure
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_readability_score(self, state: EnrichedContentState) -> float:
        """Calculate content readability score"""
        
        content = state.draft_content
        spec = state.content_spec
        
        # Simple readability heuristics
        words = content.split()
        sentences = content.count('.') + content.count('!') + content.count('?')
        
        if sentences == 0:
            return 0.5
        
        avg_words_per_sentence = len(words) / sentences
        
        # Adjust for target audience complexity
        target_complexity = spec.complexity_level
        
        if target_complexity >= 8:  # Expert audience
            optimal_range = (15, 25)
        elif target_complexity >= 6:  # Advanced audience
            optimal_range = (12, 20)
        else:  # General audience
            optimal_range = (8, 15)
        
        # Score based on how close to optimal range
        if optimal_range[0] <= avg_words_per_sentence <= optimal_range[1]:
            readability_score = 0.9
        elif abs(avg_words_per_sentence - optimal_range[0]) <= 3 or abs(avg_words_per_sentence - optimal_range[1]) <= 3:
            readability_score = 0.7
        else:
            readability_score = 0.5
        
        return readability_score
    
    def _generate_performance_projections(self, state: EnrichedContentState) -> dict:
        """Generate comprehensive performance projections"""
        
        reach_data = self._estimate_reach(state)
        engagement_expectations = state.publishing_context.engagement_expectations if state.publishing_context else {}
        
        return {
            "week_1": {
                "views": reach_data["estimated_views"],
                "engagements": reach_data["estimated_engagements"],
                "conversions": reach_data["estimated_conversions"]
            },
            "month_1": {
                "cumulative_views": int(reach_data["estimated_views"] * 1.8),
                "cumulative_engagements": int(reach_data["estimated_engagements"] * 2.2),
                "cumulative_conversions": int(reach_data["estimated_conversions"] * 2.5)
            },
            "quarter_1": {
                "total_reach": int(reach_data["estimated_views"] * 3.5),
                "qualified_leads": reach_data["estimated_qualified_leads"] * 5,
                "estimated_pipeline_value": reach_data["estimated_qualified_leads"] * 50000  # $50k average deal size
            }
        }
    
    def _estimate_channel_engagement(self, channel: str, state: EnrichedContentState) -> dict:
        """Estimate engagement for specific distribution channel"""
        
        base_engagements = {
            "linkedin_professional": {"views": 1200, "likes": 80, "comments": 12, "shares": 15},
            "medium": {"views": 600, "claps": 35, "responses": 5, "highlights": 20},
            "email_newsletter": {"opens": 400, "clicks": 40, "forwards": 8, "replies": 3},
            "company_blog": {"views": 800, "time_on_page": 180, "conversions": 10, "bounce_rate": 0.3},
            "github_documentation": {"views": 500, "stars": 20, "forks": 8, "issues": 5},
            "hacker_news": {"points": 50, "comments": 25, "views": 2000},
            "reddit_programming": {"upvotes": 30, "comments": 15, "views": 1500}
        }
        
        return base_engagements.get(channel, {"views": 400, "engagements": 20, "conversions": 2})
    
    def _get_optimal_timing(self, channel: str) -> str:
        """Get optimal timing for specific channel"""
        
        timing_map = {
            "linkedin_professional": "Tuesday-Thursday 8:00-10:00 AM EST",
            "medium": "Sunday 7:00 PM EST",
            "email_newsletter": "Tuesday 9:00 AM EST",
            "hacker_news": "Monday 9:00 AM PST",
            "reddit_programming": "Monday-Wednesday 10:00 AM EST",
            "github_documentation": "Monday 9:00 AM EST"
        }
        
        return timing_map.get(channel, "Tuesday 10:00 AM EST")
    
    def _get_content_adaptation(self, channel: str, state: EnrichedContentState) -> str:
        """Get content adaptation requirements for channel"""
        
        adaptations = {
            "linkedin_professional": "Professional tone, industry insights, call-to-action for connections",
            "medium": "Narrative structure, personal insights, clap-worthy moments",
            "email_newsletter": "Scannable format, clear value proposition, forward-friendly",
            "hacker_news": "Technical focus, hacker mindset, discussion-worthy",
            "reddit_programming": "Community-friendly, technical depth, Reddit culture awareness",
            "github_documentation": "Technical accuracy, implementation focus, contributor-friendly"
        }
        
        return adaptations.get(channel, "Platform-optimized formatting and messaging")
    
    def _calculate_strategy_impact(self, strategy: str, state: EnrichedContentState) -> str:
        """Calculate expected impact of promotional strategy"""
        
        if "investor" in strategy.lower():
            return "high"  # High-value audience
        elif "executive" in strategy.lower():
            return "high"  # Decision makers
        elif "social media" in strategy.lower():
            return "medium"  # Broad reach
        elif "email" in strategy.lower():
            return "medium-high"  # Direct communication
        else:
            return "medium"
    
    def _get_strategy_timeline(self, strategy: str) -> str:
        """Get implementation timeline for strategy"""
        
        if "immediate" in strategy.lower():
            return "0-24 hours"
        elif "email" in strategy.lower():
            return "1-3 days"
        elif "social media" in strategy.lower():
            return "1-7 days"
        elif "conference" in strategy.lower():
            return "2-8 weeks"
        else:
            return "1-2 weeks"
    
    def _define_strategy_metrics(self, strategy: str) -> list:
        """Define success metrics for promotional strategy"""
        
        if "investor" in strategy.lower():
            return ["meeting requests", "due diligence inquiries", "investment interest"]
        elif "social media" in strategy.lower():
            return ["shares", "comments", "profile visits", "follower growth"]
        elif "email" in strategy.lower():
            return ["open rate", "click rate", "reply rate", "forward rate"]
        elif "technical" in strategy.lower():
            return ["implementation attempts", "questions asked", "community engagement"]
        else:
            return ["engagement rate", "conversion rate", "brand awareness"]