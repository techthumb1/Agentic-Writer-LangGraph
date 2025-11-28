# langgraph_app/agents/enhanced_seo_agent_integrated.py
"""
Enterprise SEO Agent with LLM integration, tool use, and optimization loops.
"""

import os
import logging
import re
from typing import Dict, List, Any, Optional
from collections import Counter

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph_app.enhanced_model_registry import get_model
from langgraph_app.core.state import EnrichedContentState, AgentType, ContentPhase
from langgraph_app.core.types import SeoAnalysis, SEOOptimizationContext
from langgraph_app.enhanced_model_registry import get_model_for_generation

logger = logging.getLogger(__name__)

ALLOWED_INTENTS = {"informational", "commercial", "transactional", "navigational"}


# Tool definitions for SEO agent
@tool
def analyze_keyword_density(text: str, target_keywords: List[str]) -> Dict[str, Any]:
    """Analyze keyword density and distribution.
    
    Args:
        text: Content to analyze
        target_keywords: Keywords to check
        
    Returns:
        Keyword analysis with density percentages
    """
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    total_words = len(words)
    
    if total_words == 0:
        return {"densities": {}, "total_words": 0, "recommendations": ["Content is empty"]}
    
    densities = {}
    for keyword in target_keywords:
        kw_lower = keyword.lower()
        count = text_lower.count(kw_lower)
        density = (count / total_words) * 100
        densities[keyword] = {
            "count": count,
            "density": round(density, 2),
            "optimal": 1.0 <= density <= 3.0
        }
    
    recommendations = []
    for kw, data in densities.items():
        if data["density"] < 1.0:
            recommendations.append(f"Increase '{kw}' usage (current: {data['density']}%)")
        elif data["density"] > 3.0:
            recommendations.append(f"Reduce '{kw}' usage to avoid stuffing (current: {data['density']}%)")
    
    return {
        "densities": densities,
        "total_words": total_words,
        "recommendations": recommendations if recommendations else ["Keyword density optimal"]
    }


@tool
def generate_meta_tags(text: str, keywords: List[str], max_title_length: int = 60) -> Dict[str, str]:
    """Generate SEO meta tags from content.
    
    Args:
        text: Content to analyze
        keywords: Target keywords
        max_title_length: Maximum title length
        
    Returns:
        Meta title and description
    """
    # Extract first meaningful paragraph
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and not p.startswith('#')]
    first_para = paragraphs[0] if paragraphs else text[:200]
    
    # Generate title from first heading or first sentence
    headings = re.findall(r'^#+\s+(.+)$', text, re.M)
    if headings:
        title_base = headings[0]
    else:
        sentences = re.split(r'[.!?]', first_para)
        title_base = sentences[0].strip() if sentences else "Content"
    
    # Optimize title with keywords
    title = title_base[:max_title_length]
    if keywords and keywords[0].lower() not in title.lower():
        title = f"{keywords[0]}: {title}"[:max_title_length]
    
    # Generate description
    description = re.sub(r'[#*`]', '', first_para)[:160]
    
    return {
        "meta_title": title,
        "meta_description": description,
        "og_title": title,
        "og_description": description
    }


@tool
def check_readability_seo(text: str) -> Dict[str, Any]:
    """Check content readability for SEO.
    
    Args:
        text: Content to analyze
        
    Returns:
        Readability metrics and SEO impact
    """
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    
    word_count = len(words)
    sentence_count = max(1, len([s for s in sentences if s.strip()]))
    avg_sentence_length = word_count / sentence_count
    
    # Flesch Reading Ease
    syllables = sum(len(re.findall(r'[aeiouy]+', word)) for word in words)
    avg_syllables = syllables / max(word_count, 1)
    flesch = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables
    flesch_score = max(0, min(100, flesch))
    
    # SEO impact assessment
    if flesch_score >= 60:
        seo_impact = "positive"
        recommendation = "Good readability improves dwell time and engagement"
    elif flesch_score >= 50:
        seo_impact = "neutral"
        recommendation = "Moderate readability - consider simplification"
    else:
        seo_impact = "negative"
        recommendation = "Poor readability may hurt rankings - simplify content"
    
    return {
        "flesch_score": round(flesch_score, 1),
        "avg_sentence_length": round(avg_sentence_length, 1),
        "seo_impact": seo_impact,
        "recommendation": recommendation
    }


class EnhancedSEOAgent:
    """
    Enterprise SEO Agent with:
    - LLM-driven optimization (GPT-4o / Claude Sonnet 4)
    - Tool use (keyword analysis, meta generation, readability)
    - Self-refinement loop for SEO score validation
    - Dynamic search intent determination
    """
    
    def __init__(self):
        self.agent_type = AgentType.SEO
        self.tools = [analyze_keyword_density, generate_meta_tags, check_readability_seo]
        
        # SEO thresholds
        self.min_seo_score = 0.7
        self.max_refinement_loops = 1
    
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute SEO optimization with LLM and tools."""
        
        logger.info("📈 SEO: Starting enterprise optimization")
        
        # Get content to optimize
        if state.formatted_content and hasattr(state.formatted_content, 'markdown'):
            content = state.formatted_content.markdown
        elif state.edited_content and hasattr(state.edited_content, 'body'):
            content = state.edited_content.body
        elif state.draft_content:
            content = state.draft_content.body if hasattr(state.draft_content, 'body') else state.draft_content
        else:
            content = state.content
        
        if not content or not content.strip():
            raise RuntimeError("ENTERPRISE: SEO requires content")
        
        # Get configs
        template_config = state.template_config or {}
        
        # Extract SEO context
        target_keywords = self._extract_target_keywords(state)
        search_intent = self._determine_search_intent(state)
        
        # Self-refinement loop
        seo_score = 0.0
        refinement_round = 0
        optimized_content = content
        
        while refinement_round < self.max_refinement_loops and seo_score < self.min_seo_score:
            refinement_round += 1
            logger.info(f"🔍 SEO refinement round {refinement_round}/{self.max_refinement_loops}")
            
            # Run LLM optimization with tools
            optimized_content, tool_results, seo_score = self._llm_optimize_with_tools(
                optimized_content,
                target_keywords,
                search_intent,
                template_config,
                state
            )
            
            if seo_score >= self.min_seo_score:
                logger.info(f"✅ SEO score acceptable: {seo_score:.2f}")
                break
            else:
                logger.info(f"⚠️ SEO score too low: {seo_score:.2f}, refining...")
        
        # Generate meta tags
        meta_result = generate_meta_tags.invoke({
            "text": optimized_content,
            "keywords": target_keywords,
            "max_title_length": 60
        })
        
        # Create SEO analysis
        keyword_analysis = analyze_keyword_density.invoke({
            "text": optimized_content,
            "target_keywords": target_keywords
        })
        
        state.seo_analysis = SeoAnalysis(
            keyword_density={kw: data["density"] for kw, data in keyword_analysis["densities"].items()},
            readability_score=seo_score,
            recommendations=keyword_analysis["recommendations"],
            meta_title=meta_result["meta_title"],
            meta_description=meta_result["meta_description"]
        )
        
        # Create SEO optimization context
        state.seo_optimization = SEOOptimizationContext(
            target_keywords=target_keywords,
            meta_description=meta_result["meta_description"],
            title_recommendations=[meta_result["meta_title"]],
            seo_score=seo_score
        )
        
        # Update content
        state.content = optimized_content
        state.update_phase(ContentPhase.OPTIMIZATION)
        
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "seo_score": seo_score,
            "refinement_rounds": refinement_round,
            "keywords_count": len(target_keywords)
        })
        
        logger.info(f"✅ SEO: Completed with score={seo_score:.2f}")
        
        return state
    
    def _llm_optimize_with_tools(
            self,
            content: str,
            keywords: List[str],
            intent: str,
            template_config: Dict,
            state: EnrichedContentState
        ) -> tuple[str, List[Dict], float]:
            """Use LLM with tools to optimize for SEO."""

            # Get model with proper settings
            model = get_model(
                agent_name="seo",
                settings={
                    "temperature": 1.0,
                    "max_tokens": 4000
                }
            )

            # Bind tools
            model_with_tools = model.bind_tools(self.tools)

            # Build SEO prompt
            system_prompt = self._build_seo_system_prompt(keywords, intent, template_config)

            user_prompt = f"""Optimize the following content for search engines.

    **Target Keywords:** {', '.join(keywords)}
    **Search Intent:** {intent}

    **Content to Optimize:**
    {content}

    **Instructions:**
    1. Use analyze_keyword_density to check current keyword usage
    2. Use check_readability_seo to assess SEO impact of readability
    3. Use generate_meta_tags to create optimized meta tags
    4. Adjust keyword placement naturally (1-3% density per keyword)
    5. Maintain content quality while improving discoverability
    6. Ensure headers include target keywords
    7. Add internal linking opportunities where natural

    Provide the SEO-optimized content with improvements applied."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Invoke with tools
            response = model_with_tools.invoke(messages)

            # Extract tool results
            tool_results = []
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    logger.info(f"🔧 Tool called: {tool_call['name']}")
                    tool_results.append({
                        "tool": tool_call['name'],
                        "result": tool_call.get('args', {})
                    })

            # Calculate SEO score
            seo_score = self._calculate_seo_score(tool_results, keywords)

            # Extract optimized content
            optimized = response.content if hasattr(response, 'content') else content

            return optimized, tool_results, seo_score    
    
    def _build_seo_system_prompt(
        self,
        keywords: List[str],
        intent: str,
        template_config: Dict
    ) -> str:
        """Build system prompt for SEO optimization."""
        
        template_type = template_config.get('template_type', 'content')
        
        prompt = f"""You are an expert SEO specialist optimizing {template_type} content.

**SEO Objectives:**
- Improve search engine rankings for target keywords
- Optimize for {intent} search intent
- Maintain natural, readable content (no keyword stuffing)
- Enhance SERP click-through rates with compelling meta tags
- Follow E-E-A-T principles (Experience, Expertise, Authority, Trust)

**Target Keywords:** {', '.join(keywords)}
**Search Intent:** {intent}

**Optimization Guidelines:**
1. Keyword placement: Title, H1, first paragraph, subheadings
2. Density: 1-3% per keyword (natural distribution)
3. Semantic variations: Use related terms and synonyms
4. Internal structure: Clear hierarchy with H2/H3 tags
5. Readability: Target Flesch score 60+ for wider audience
6. Meta optimization: Compelling titles/descriptions with keywords

**Critical Instructions:**
- Use available tools to analyze and validate optimizations
- Never sacrifice content quality for SEO tactics
- Maintain factual accuracy and authority
- Focus on user value - search engines reward helpful content
- Avoid over-optimization that triggers spam filters"""
        
        return prompt
    
    def _calculate_seo_score(self, tool_results: List[Dict], keywords: List[str]) -> float:
        """Calculate overall SEO score from tool results."""
        
        score = 0.5  # Base
        
        # Keyword density score
        density_results = [r for r in tool_results if r.get('tool') == 'analyze_keyword_density']
        if density_results:
            densities = density_results[0].get('result', {}).get('densities', {})
            optimal_count = sum(1 for data in densities.values() if data.get('optimal', False))
            density_score = optimal_count / max(len(keywords), 1)
            score += density_score * 0.3
        
        # Readability score
        readability_results = [r for r in tool_results if r.get('tool') == 'check_readability_seo']
        if readability_results:
            flesch = readability_results[0].get('result', {}).get('flesch_score', 50)
            if flesch >= 60:
                score += 0.2
            elif flesch >= 50:
                score += 0.1
        
        return min(1.0, score)
    
    def _extract_target_keywords(self, state: EnrichedContentState) -> List[str]:
        """Extract target keywords with priority order."""
        
        # 1. Planning output
        if state.planning_output:
            kw = getattr(state.planning_output, 'target_keywords', None)
            if isinstance(kw, list) and kw:
                return [k.strip() for k in kw if k]
        
        # 2. Template config
        template_config = state.template_config or {}
        if isinstance(template_config, dict):
            raw = template_config.get('keywords')
            if isinstance(raw, list) and raw:
                return [str(x).strip() for x in raw if x]
            elif isinstance(raw, str) and raw:
                return [s.strip() for s in raw.split(',') if s.strip()]
        
        # 3. Topic-derived
        if state.content_spec:
            topic = state.content_spec.topic or ""
            tokens = [t.strip() for t in re.split(r'[^\w\-]+', topic) if t.strip()]
            tokens = list(dict.fromkeys(tokens))  # Dedupe
            tokens.sort(key=len, reverse=True)
            return tokens[:6] if tokens else ["content"]
        
        return ["content"]
    
    def _determine_search_intent(self, state: EnrichedContentState) -> str:
        """Determine search intent dynamically."""
        
        # Check planning override
        if state.planning_output:
            override = getattr(state.planning_output, 'search_intent', None)
            if override and override in ALLOWED_INTENTS:
                return override
        
        # Analyze template type
        template_config = state.template_config or {}
        template_type = str(template_config.get('template_type', '')).lower()
        
        if any(w in template_type for w in ['research', 'analysis', 'documentation', 'guide']):
            return "informational"
        elif any(w in template_type for w in ['proposal', 'pitch', 'marketing', 'sales']):
            return "commercial"
        elif any(w in template_type for w in ['product', 'service', 'buy', 'purchase']):
            return "transactional"
        elif any(w in template_type for w in ['brand', 'about', 'company']):
            return "navigational"
        
        return "informational"  # Default