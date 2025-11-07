# langgraph_app/agents/enhanced_seo_agent_integrated.py
# FIXED: Removed duplicate function and cleaned up code for a single source of truth.

import re
from typing import Dict, List
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
        state.log_agent_execution(self.agent_type, { "status": "started" })

        seo_context = self._create_seo_context(state)
        state.seo_optimization = seo_context

        optimized_content = self._apply_seo_optimizations(state)
        state.draft_content = optimized_content
        state.update_phase(ContentPhase.OPTIMIZATION)

        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "keywords_targeted": len(seo_context.target_keywords),
            "seo_score": seo_context.seo_score
        })

        return state

    def _normalize_user_intent(self, val: str) -> str:
        v = (val or "").strip().lower()
        if v in ALLOWED_INTENTS:
            return v
        alias = {
            "info": "informational", "educational": "informational",
            "trans": "transactional", "comm": "commercial", "nav": "navigational",
        }
        if v in alias:
            return alias[v]
        raise ValueError(f"ENTERPRISE: SEO intent override invalid: '{val}'. Allowed: {sorted(ALLOWED_INTENTS)}")

    def _extract_target_keywords(self, state: EnrichedContentState) -> List[str]:
        """Deterministic keyword extraction from state."""
        # Priority 1: From planning_output
        planning = getattr(state, "planning_output", None)
        if planning:
            keywords = getattr(planning, "target_keywords", None)
            if keywords and isinstance(keywords, list):
                return [k.strip() for k in keywords if k and isinstance(k, str)]

        # Priority 2: From template_config
        template_cfg = getattr(state, "template_config", {}) or {}
        raw_keywords = template_cfg.get("keywords")
        if isinstance(raw_keywords, list):
            return [str(k).strip() for k in raw_keywords if str(k).strip()]
        if isinstance(raw_keywords, str):
            return [s.strip() for s in raw_keywords.split(',') if s.strip()]

        # Priority 3: Derived from topic
        topic = getattr(state.content_spec, "topic", "") or ""
        tokens = list(dict.fromkeys([t.strip() for t in re.split(r'\W+', topic) if len(t.strip()) > 3]))
        tokens.sort(key=len, reverse=True)
        if not tokens:
             raise RuntimeError("ENTERPRISE: SEO agent could not determine keywords from topic.")
        return tokens[:5]

    def _determine_search_intent(self, state: EnrichedContentState) -> str:
        """
        Deterministic intent mapping.
        Precedence: Override -> Template Map -> Style Map. Raises error if unmapped.
        """
        # 1. Explicit override from planning
        planning = getattr(state, "planning_output", None)
        if planning:
            override = getattr(planning, "search_intent", None)
            if override:
                return self._normalize_user_intent(override)

        template_cfg = getattr(state, "template_config", {}) or {}
        template_type = str(template_cfg.get("template_type", "")).strip().lower()

        style_cfg = getattr(state, "style_config", {}) or {}
        style_id = str(style_cfg.get("id", "")).strip().lower()

        INTENT_BY_TEMPLATE = {
            "api_documentation": "informational", "blog_article": "informational",
            "business_proposal": "commercial", "data_driven_report": "informational",
            "email_newsletter": "informational", "market_analysis": "informational",
            "press_release": "commercial", "research_paper": "informational",
            "social_media_campaign": "commercial", "strategic_brief": "commercial",
            "technical_documentation": "informational",
        }
        if template_type in INTENT_BY_TEMPLATE:
            return INTENT_BY_TEMPLATE[template_type]

        INTENT_BY_STYLE = {
            "content_marketing": "commercial", "conversion_optimization": "transactional",
            "executive_summary": "commercial", "investor_presentation": "commercial",
            "phd_academic": "informational", "technical_dive": "informational",
        }
        if style_id in INTENT_BY_STYLE:
            return INTENT_BY_STYLE[style_id]

        raise ValueError(f"ENTERPRISE: SEO intent unmapped for template_type '{template_type}' and style_profile '{style_id}'.")

    def _create_seo_context(self, state: EnrichedContentState) -> SEOOptimizationContext:
        """Create the full SEO context for the optimization step."""
        target_keywords = self._extract_target_keywords(state)
        primary_keyword = target_keywords[0]
        topic = state.content_spec.topic
        
        # Generate a compelling, keyword-rich title
        title_recommendations = [
            f"{primary_keyword.title()}: A Comprehensive Guide to {topic}",
            f"Understanding {topic}: The Role of {primary_keyword.title()}",
            f"How {primary_keyword.title()} Is Transforming {topic}"
        ]
        
        # Generate a meta description
        meta_description = f"Explore the critical role of {primary_keyword} in {topic}. This definitive guide covers key strategies, market analysis, and future trends."

        return SEOOptimizationContext(
            target_keywords=target_keywords,
            meta_description=meta_description,
            title_recommendations=title_recommendations,
            seo_score=0.85 # Base score, can be refined later
        )

    def _apply_seo_optimizations(self, state: EnrichedContentState) -> str:
        """Apply SEO optimizations to the draft content."""
        content = state.draft_content
        seo_context = state.seo_optimization
        
        if not seo_context or not seo_context.target_keywords:
            return content

        primary_keyword = seo_context.target_keywords[0]

        # 1. Optimize Title: Ensure primary keyword is in the main H1
        # This assumes markdown format with a single H1 at the start.
        content_lines = content.split('\n')
        if content_lines and content_lines[0].startswith('# '):
            if primary_keyword.lower() not in content_lines[0].lower():
                content_lines[0] = f'# {primary_keyword.title()}: {content_lines[0][2:]}'
                content = '\n'.join(content_lines)

        # 2. Keyword Integration: Ensure the primary keyword appears in the first paragraph.
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1 and primary_keyword.lower() not in paragraphs[0].lower():
            # Find the first sentence and prepend the keyword phrase
            first_paragraph_sentences = paragraphs[0].split('. ')
            first_paragraph_sentences[0] = f"In the context of {primary_keyword}, {first_paragraph_sentences[0].lower()}"
            paragraphs[0] = '. '.join(first_paragraph_sentences)
            content = '\n\n'.join(paragraphs)

        return content