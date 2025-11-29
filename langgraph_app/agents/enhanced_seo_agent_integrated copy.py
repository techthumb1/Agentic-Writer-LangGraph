# File: langgraph_app/agents/enhanced_seo_agent_integrated.py
# Replace the entire SEO agent with this corrected version:

import re
from typing import Dict, List
from venv import logger
from langgraph_app.core.state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    SEOOptimizationContext
)

ALLOWED_INTENTS = {"informational", "commercial", "transactional", "navigational"}

class EnhancedSEOAgent:
    """Integrated SEO Agent using EnrichedContentState with Template Configuration Support"""
    
    def __init__(self):
        self.agent_type = AgentType.SEO
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Optimize content for SEO"""
        template_config = state.template_config or {}
        instructions = state.get_agent_instructions(self.agent_type)
    
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "platform": state.content_spec.platform,
            "length": len(state.draft_content.split())
        })
    
        seo_context = self._create_seo_context(state, instructions, template_config)
        state.seo_optimization = seo_context  # Use correct attribute name
    
        optimized = self._apply_seo_optimizations(state, instructions, template_config)
        state.draft_content = optimized
    
        state.update_phase(ContentPhase.OPTIMIZATION)
    
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "keywords": len(seo_context.target_keywords),
            "confidence_score": seo_context.seo_score
        })
    
        return state

    def _safe_get_planning_data(self, state: EnrichedContentState, attribute: str, default=None):
        """Safely get planning data whether it's a dict or object"""
        if not state.planning_output:
            return default

        if isinstance(state.planning_output, dict):
            return state.planning_output.get(attribute, default)
        else:
            return getattr(state.planning_output, attribute, default)

    def _safe_get_research_data(self, state: EnrichedContentState, attribute: str, default=None):
        """Safely get research data whether it's a dict or object"""
        if not state.research_findings:
            return default

        if isinstance(state.research_findings, dict):
            return state.research_findings.get(attribute, default)
        else:
            return getattr(state.research_findings, attribute, default)

    def _normalize_user_intent(self, val: str) -> str:
        v = (val or "").strip().lower()
        if v in ALLOWED_INTENTS:
            return v
        # Accept a few common aliases explicitly (not a heuristic fallthrough)
        alias = {
            "info": "informational",
            "educational": "informational",
            "trans": "transactional",
            "comm": "commercial",
            "nav": "navigational",
        }
        if v in alias:
            return alias[v]
        raise ValueError(f"SEO intent override invalid: '{val}'. Allowed: {sorted(ALLOWED_INTENTS)}")


    def _extract_target_keywords(self, state, *args, **kwargs) -> List[str]:
        """
        Deterministic keyword extraction with tolerant signature.
        Priority:
          1) planning_output.target_keywords (list[str])
          2) template_config['keywords'] (list[str] or comma-separated str)
          3) content_spec.topic tokens (top 3–6 by length)
        """
        # 1) planning_output
        kw = None
        po = getattr(state, "planning_output", None)
        if po is not None:
            if isinstance(po, dict):
                kw = po.get("target_keywords")
            else:
                kw = getattr(po, "target_keywords", None)
        if isinstance(kw, list) and all(isinstance(x, str) for x in kw) and kw:
            return [k.strip() for k in kw if k and isinstance(k, str)]

        # 2) template_config
        tc = getattr(state, "template_config", {}) or {}
        if isinstance(tc, dict):
            raw = tc.get("keywords")
            if isinstance(raw, list):
                cand = [str(x).strip() for x in raw if str(x).strip()]
                if cand:
                    return cand
            elif isinstance(raw, str):
                cand = [s.strip() for s in raw.split(",") if s.strip()]
                if cand:
                    return cand

        # 3) topic-derived
        topic = getattr(getattr(state, "content_spec", None), "topic", "") or ""
        tokens = [t.strip() for t in re.split(r"[^\w\-]+", topic) if t.strip()]
        tokens = list(dict.fromkeys(tokens))  # stable dedupe
        tokens.sort(key=len, reverse=True)
        return tokens[:6] if tokens else []


    def _determine_search_intent(self, state) -> str:
        """Dynamic intent determination without hardcoded mappings"""

        # Check explicit overrides first
        po = getattr(state, "planning_output", None)
        if po:
            override = po.get("search_intent") if isinstance(po, dict) else getattr(po, "search_intent", None)
            if override and override in ALLOWED_INTENTS:
                return override

        # Analyze template characteristics dynamically
        tc = getattr(state, "template_config", {}) or {}
        template_type = str(tc.get("template_type") or "").strip().lower()

        # Dynamic classification
        if any(word in template_type for word in ['research', 'analysis', 'documentation', 'technical', 'guide']):
            return "informational"
        elif any(word in template_type for word in ['proposal', 'pitch', 'marketing', 'sales']):
            return "commercial"
        elif any(word in template_type for word in ['product', 'service', 'buy', 'purchase']):
            return "transactional"
        elif any(word in template_type for word in ['brand', 'about', 'company']):
            return "navigational"

        # Default: informational for unknown types
        logger.warning(f"Unknown template type '{template_type}' - defaulting to informational intent")
        return "informational"
    
    def _determine_search_intent(self, state) -> str:
        """
        Intent precedence:
          1) Explicit user/plan override (planning_output.search_intent or content_spec.search_intent)
          2) Explicit map by template_type
          3) Explicit map by style_profile id/name
        Raises on unknowns. No implicit fallbacks.
        """
        # 1) explicit override
        po = getattr(state, "planning_output", None)
        if po is not None:
            override = po["search_intent"] if isinstance(po, dict) else getattr(po, "search_intent", None)
            if override:
                return self._normalize_user_intent(override)
        cs = getattr(state, "content_spec", None)
        if cs is not None:
            override = cs.get("search_intent") if isinstance(cs, dict) else getattr(cs, "search_intent", None)
            if override:
                return self._normalize_user_intent(override)

        # 2) map by template_type (normalized from your folder list)
        tc = getattr(state, "template_config", {}) or {}
        template_type = str(tc.get("template_type") or "").strip().lower()

        INTENT_BY_TEMPLATE: Dict[str, str] = {
            "api_documentation": "informational",
            "blog_article": "informational",
            "business_proposal": "commercial",
            "data_driven_report": "informational",  # data_driven_template.yaml
            "email_newsletter": "informational",
            "market_analysis": "informational",     # market_analysis_template.yaml
            "press_release": "commercial",
            "research_paper": "informational",      # research_paper_template.yaml
            "social_media_campaign": "commercial",
            "strategic_brief": "commercial",        # strategic_brief_template.yaml
            "technical_documentation": "informational",
        }

        # 3) map by style_profile id/name (normalized from your folder list)
        sc = getattr(state, "style_config", {}) or {}
        style_id = str(sc.get("id") or sc.get("slug") or sc.get("name") or "").strip().lower()

        INTENT_BY_STYLE: Dict[str, str] = {
            # Commercial / persuasion
            "content_marketing": "commercial",
            "conversion_optimization": "transactional",
            "email_campaign": "commercial",
            "executive_summary": "commercial",
            "investor_presentation": "commercial",
            "grant_application": "commercial",
            "product_launch": "commercial",
            "roi_analysis": "commercial",
            "sales_enablement": "commercial",
            "startup_usecases": "commercial",
            "strategic_planning": "commercial",
            "venture_capital_pitch": "commercial",
            "board_presentation": "commercial",
            "influencer_collaboration": "commercial",
            # Navigational
            "brand_storytelling": "navigational",
            # Informational
            "academic_book_chapter": "informational",
            "academic_textbook": "informational",
            "advanced_masterclass": "informational",
            "ai_in_healthcare": "informational",
            "ai_news_brief": "informational",
            "api_documentation": "informational",
            "beginner_tutorial": "informational",
            "business_case_analysis": "informational",
            "certification_prep": "informational",
            "code_review_standards": "informational",
            "competitive_analysis": "informational",
            "conference_abstract": "informational",
            "corporate_training": "informational",
            "customer_success": "informational",
            "deployment_guide": "informational",
            "experimental_lab_log": "informational",
            "founder_storytelling": "informational",
            "future_of_llms": "informational",
            "implementation_guide": "informational",
            "integration_manual": "informational",
            "knowledge_base": "informational",
            "learning_pathway": "informational",
            "literature_review": "informational",
            "market_flash": "informational",
            "market_research_report": "informational",
            "merger_acquisition": "informational",
            "methodology_paper": "informational",
            "online_course": "informational",
            "peer_review_article": "informational",
            "performance_analysis": "informational",
            "phd_academic": "informational",
            "phd_dissertation": "informational",
            "phd_lit_review": "informational",
            "policy_watch": "informational",
            "popular_sci": "informational",
            "research_proposal": "informational",
            "scholarly_commentary": "informational",
            "security_protocol": "informational",
            "skill_assessment": "informational",
            "social_media_voice": "informational",
            "startup_trends_brief": "informational",
            "system_architecture": "informational",
            "technical_dive": "informational",
            "technical_specification": "informational",
            "technical_tutor": "informational",
            "thesis_defense": "informational",
            "thought_leadership": "informational",
            "troubleshooting_manual": "informational",
            "workshop_facilitator": "informational",
        }

        # Normalize known aliases from filenames
        alias = {
            "api_documentation_template": "api_documentation",
            "blog_article_generator": "blog_article",
            "data_driven_template": "data_driven_report",
            "market_analysis_template": "market_analysis",
            "research_paper_template": "research_paper",
            "strategic_brief_template": "strategic_brief",
            "social_media_campaign copy": "social_media_campaign",
        }

        tkey = alias.get(template_type, template_type)

        if tkey in INTENT_BY_TEMPLATE:
            return INTENT_BY_TEMPLATE[tkey]

        if style_id in INTENT_BY_STYLE:
            return INTENT_BY_STYLE[style_id]

        raise ValueError(
            f"SEO intent: unmapped template_type '{template_type}' (normalized='{tkey}') "
            f"and style_profile '{style_id}'. Add explicit mapping."
        )


#    def _extract_target_keywords(self, state) -> list[str]:
#        """
#        Deterministic keyword extraction (no fallbacks beyond state fields).
#        Priority:
#          1) planning_output.target_keywords (list[str])
#          2) template_config['keywords'] (list[str] or comma-separated str)
#          3) content_spec.topic -> split, dedupe, keep 3–6 longest tokens
#        """
#        # 1) planning_output
#        kw = None
#        if getattr(state, "planning_output", None):
#            po = state.planning_output
#            if isinstance(po, dict):
#                kw = po.get("target_keywords")
#            else:
#                kw = getattr(po, "target_keywords", None)
#        if isinstance(kw, list) and all(isinstance(x, str) for x in kw) and kw:
#            return [k.strip() for k in kw if k and isinstance(k, str)]
#
#        # 2) template_config
#        tc = getattr(state, "template_config", {}) or {}
#        if isinstance(tc, dict):
#            raw = tc.get("keywords")
#            if isinstance(raw, list):
#                cand = [str(x).strip() for x in raw if str(x).strip()]
#                if cand:
#                    return cand
#            elif isinstance(raw, str):
#                cand = [s.strip() for s in raw.split(",") if s.strip()]
#                if cand:
#                    return cand
#
#        # 3) topic-derived
#        topic = getattr(getattr(state, "content_spec", None), "topic", "") or ""
#        tokens = [t.strip() for t in re.split(r"[^\w\-]+", topic) if t.strip()]
#        tokens = list(dict.fromkeys(tokens))  # stable dedupe
#        tokens.sort(key=len, reverse=True)
#        return tokens[:6] if tokens else []

    
    #def _determine_search_intent(self, state) -> str:
    #    """
    #    Deterministic intent by template_type and style_profile with explicit enterprise maps.
    #    Returns one of: 'informational' | 'commercial' | 'transactional' | 'navigational'
    #    Raises on unmapped types. No fallbacks.
    #    """
    #    # Extract template_type from template_config (YAML-first pipeline contract)
    #    tc = getattr(state, "template_config", {}) or {}
    #    template_type = str(tc.get("template_type") or "").strip().lower()

    #    # Extract style profile id/name (if present) — used only as an alternate explicit key
    #    sc = getattr(state, "style_config", {}) or {}
    #    style_id = str(sc.get("id") or sc.get("slug") or sc.get("name") or "").strip().lower()

    #    # --- Explicit map for content templates (from data/content_templates) ---
    #    INTENT_BY_TEMPLATE: Dict[str, str] = {
    #        # 12 templates you listed
    #        "api_documentation": "informational",
    #        "blog_article": "informational",
    #        "business_proposal": "commercial",
    #        "data_driven_report": "informational",  # filename was data_driven_template.yaml
    #        "email_newsletter": "informational",
    #        "market_analysis": "informational",
    #        "press_release": "commercial",
    #        "research_paper": "informational",
    #        "social_media_campaign": "commercial",
    #        "strategic_brief": "commercial",
    #        "technical_documentation": "informational",
    #        # If your YAML uses generator variants, normalize them in your loader to these keys
    #    }

    #    # --- Explicit map for style profiles (from data/style_profiles) ---
    #    INTENT_BY_STYLE: Dict[str, str] = {
    #        # Commercial / go-to-market / persuasion
    #        "content_marketing": "commercial",
    #        "conversion_optimization": "transactional",
    #        "email_campaign": "commercial",
    #        "executive_summary": "commercial",
    #        "investor_presentation": "commercial",
    #        "grant_application": "commercial",
    #        "product_launch": "commercial",
    #        "roi_analysis": "commercial",
    #        "sales_enablement": "commercial",
    #        "startup_usecases": "commercial",
    #        "strategic_planning": "commercial",
    #        "venture_capital_pitch": "commercial",
    #        "board_presentation": "commercial",
    #        "influencer_collaboration": "commercial",

    #        # Navigational (brand/site/identity oriented)
    #        "brand_storytelling": "navigational",

    #        # Informational (documentation, research, training, analysis)
    #        "academic_book_chapter": "informational",
    #        "academic_textbook": "informational",
    #        "advanced_masterclass": "informational",
    #        "ai_in_healthcare": "informational",
    #        "ai_news_brief": "informational",
    #        "api_documentation": "informational",
    #        "beginner_tutorial": "informational",
    #        "business_case_analysis": "informational",
    #        "certification_prep": "informational",
    #        "code_review_standards": "informational",
    #        "competitive_analysis": "informational",
    #        "conference_abstract": "informational",
    #        "corporate_training": "informational",
    #        "customer_success": "informational",
    #        "deployment_guide": "informational",
    #        "experimental_lab_log": "informational",
    #        "founder_storytelling": "informational",
    #        "future_of_llms": "informational",
    #        "implementation_guide": "informational",
    #        "integration_manual": "informational",
    #        "knowledge_base": "informational",
    #        "learning_pathway": "informational",
    #        "literature_review": "informational",
    #        "market_flash": "informational",
    #        "market_research_report": "informational",
    #        "merger_acquisition": "informational",
    #        "methodology_paper": "informational",
    #        "online_course": "informational",
    #        "peer_review_article": "informational",
    #        "performance_analysis": "informational",
    #        "phd_academic": "informational",
    #        "phd_dissertation": "informational",
    #        "phd_lit_review": "informational",
    #        "policy_watch": "informational",
    #        "popular_sci": "informational",
    #        "research_proposal": "informational",
    #        "scholarly_commentary": "informational",
    #        "security_protocol": "informational",
    #        "skill_assessment": "informational",
    #        "social_media_voice": "informational",
    #        "startup_trends_brief": "informational",
    #        "system_architecture": "informational",
    #        "technical_dive": "informational",
    #        "technical_specification": "informational",
    #        "technical_tutor": "informational",
    #        "thesis_defense": "informational",
    #        "thought_leadership": "informational",
    #        "troubleshooting_manual": "informational",
    #        "workshop_facilitator": "informational",
    #    }

    #    # Normalize known filename-style aliases to canonical keys above
    #    alias = {
    #        "api_documentation_template": "api_documentation",
    #        "blog_article_generator": "blog_article",
    #        "data_driven_template": "data_driven_report",
    #        "market_analysis_template": "market_analysis",
    #        "research_paper_template": "research_paper",
    #        "strategic_brief_template": "strategic_brief",
    #    }

    #    tkey = alias.get(template_type, template_type)
#
    #    if tkey in INTENT_BY_TEMPLATE:
    #        return INTENT_BY_TEMPLATE[tkey]
#
    #    if style_id in INTENT_BY_STYLE:
    #        return INTENT_BY_STYLE[style_id]
#
    #    raise ValueError(
    #        f"SEO intent: unmapped template_type '{template_type}' (normalized='{tkey}') "
    #        f"and style_profile '{style_id}'. Add explicit mapping."
    #    )

    def _create_seo_context(self, state: EnrichedContentState, instructions, template_config: dict) -> SEOOptimizationContext:
        """Create SEO optimization context with template configuration"""
        
        spec = state.content_spec  # Direct attribute access
        research = state.research_findings
        planning = state.planning_output
        
        # Extract target keywords with template priority
        target_keywords = self._extract_target_keywords(state, spec, research, planning, template_config)
        
        # Determine search intent with template context
        search_intent = self._determine_search_intent(spec, planning, template_config)
        
        # Analyze competitors with template awareness
        competitor_analysis = self._analyze_competitors(spec, research, template_config)
        
        # Identify optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(state, template_config)
        
        return SEOOptimizationContext(
            target_keywords=target_keywords,
            meta_description="",
            title_recommendations=[],
            header_optimization={},
            internal_links=[],
            external_links=[],
            readability_improvements=optimization_opportunities,
            seo_score=0.78,
            competitor_analysis=competitor_analysis,
            search_intent=search_intent
        )

    
    def _analyze_competitors(self, spec, research, template_config: dict) -> dict:
        """Analyze competitor content with template awareness"""
        
        analysis = {
            "direct_competitors": [],
            "content_gaps": [],
            "opportunity_keywords": []
        }
        
        if research and hasattr(research, 'competitive_landscape'):
            competitive_landscape = getattr(research, 'competitive_landscape', {})
            if isinstance(competitive_landscape, dict):
                competitors = competitive_landscape.get("direct_competitors", [])
                analysis["direct_competitors"] = competitors
        
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
                "Include funding stage terminology"
            ])
        elif template_type == "business_proposal":
            opportunities.extend([
                "Optimize for 'ROI' and financial keywords", 
                "Add implementation timeline for project searches"
            ])
        
        # Check content structure
        if content.count('#') < 3:
            opportunities.append("Add more subheadings for better content structure")
        
        return opportunities
    
    def _apply_seo_optimizations(self, state: EnrichedContentState, instructions, template_config: dict) -> str:
        """Apply SEO optimizations to content with template configuration"""
        
        content = state.draft_content
        seo_context = state.seo_optimization
        
        # Optimize title and headers
        content = self._optimize_title_and_headers(content, seo_context, template_config)
        
        # Optimize keyword density
        content = self._optimize_keyword_integration(content, seo_context, template_config)
        
        return content
    
    def _optimize_title_and_headers(self, content: str, seo_context: SEOOptimizationContext, template_config: dict) -> str:
        """Optimize title and headers with template keywords"""
        
        if not seo_context.target_keywords:
            return content
            
        primary_keyword = seo_context.target_keywords[0]
        
        # Optimize main title
        import re
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        if title_match and primary_keyword.lower() not in title_match.group(1).lower():
            optimized_title = f"# {primary_keyword.title()}: {title_match.group(1)}"
            content = content.replace(title_match.group(0), optimized_title, 1)
        
        return content
    
    def _optimize_keyword_integration(self, content: str, seo_context: SEOOptimizationContext, template_config: dict) -> str:
        """Optimize keyword integration with natural placement"""
        
        if not seo_context.target_keywords:
            return content
            
        primary_keyword = seo_context.target_keywords[0]
        
        # Calculate target keyword density (2% for primary keyword)
        word_count = len(content.split())
        current_occurrences = content.lower().count(primary_keyword.lower())
        target_occurrences = max(2, int(word_count * 0.02))
        
        if current_occurrences < target_occurrences:
            # Add keyword naturally in template-appropriate contexts
            template_type = template_config.get('template_type')
            if template_type == "venture_capital_pitch":
                keyword_phrase = f"This {primary_keyword} opportunity represents enhanced value."
            elif template_type == "business_proposal":
                keyword_phrase = f"The {primary_keyword} implementation will deliver results."
            else:
                keyword_phrase = f"The {primary_keyword} analysis reveals key insights."
            
            # Add phrase naturally to content
            if keyword_phrase.lower() not in content.lower():
                paragraphs = content.split('\n\n')
                if len(paragraphs) > 2:
                    paragraphs[2] = keyword_phrase + " " + paragraphs[2]
                    content = '\n\n'.join(paragraphs)
        
        return content
    
EnhancedSeoAgent = EnhancedSEOAgent
__all__ = ['EnhancedSEOAgent', 'EnhancedSeoAgent']
