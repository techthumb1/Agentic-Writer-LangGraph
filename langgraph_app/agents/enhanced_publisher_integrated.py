# langgraph_app/agents/enhanced_publisher_integrated.py
"""
Enterprise Publisher Agent with LLM integration, distribution strategy, and quality assurance.
"""

import os
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from langgraph_app.core.state import EnrichedContentState, AgentType, ContentPhase
from langgraph_app.enhanced_model_registry import get_model_for_generation

logger = logging.getLogger(__name__)


# Tool definitions for Publisher agent
@tool
def validate_content_quality(text: str) -> Dict[str, Any]:
    """Validate content meets publication standards.
    
    Args:
        text: Content to validate
        
    Returns:
        Quality validation results
    """
    issues = []
    
    word_count = len(text.split())
    if word_count < 300:
        issues.append(f"Word count too low: {word_count} (minimum 300)")
    
    if text.count('#') < 2:
        issues.append("Insufficient section structure (need minimum 2 headers)")
    
    if not any(char in text for char in ['.', '!', '?']):
        issues.append("No sentence punctuation detected")
    
    # Check for placeholder content
    placeholders = ['[to be added]', '[tbd]', '[insert', '[add ', 'lorem ipsum']
    found_placeholders = [p for p in placeholders if p.lower() in text.lower()]
    if found_placeholders:
        issues.append(f"Contains placeholders: {', '.join(found_placeholders)}")
    
    quality_score = max(0, 1.0 - (len(issues) * 0.2))
    
    return {
        "quality_score": round(quality_score, 2),
        "word_count": word_count,
        "issues": issues,
        "ready_to_publish": len(issues) == 0
    }


@tool
def generate_distribution_plan(platform: str, content_type: str, audience: str) -> Dict[str, Any]:
    """Generate distribution strategy for content.
    
    Args:
        platform: Primary platform
        content_type: Type of content
        audience: Target audience
        
    Returns:
        Distribution recommendations
    """
    channels = {
        "linkedin": ["LinkedIn feed", "LinkedIn articles", "LinkedIn groups"],
        "medium": ["Medium publication", "Twitter thread", "Newsletter"],
        "web": ["Company blog", "Email newsletter", "Social media"],
        "github": ["GitHub repo", "Developer communities", "Technical forums"]
    }
    
    primary_channels = channels.get(platform.lower(), ["Web", "Email", "Social"])
    
    timing_recommendations = {
        "linkedin": {"best_days": ["Tuesday", "Wednesday", "Thursday"], "best_time": "8-10 AM"},
        "medium": {"best_days": ["Wednesday", "Thursday"], "best_time": "7-9 AM"},
        "web": {"best_days": ["Tuesday", "Wednesday"], "best_time": "10 AM - 2 PM"}
    }
    
    timing = timing_recommendations.get(platform.lower(), {
        "best_days": ["Tuesday", "Wednesday"],
        "best_time": "9 AM - 12 PM"
    })
    
    return {
        "primary_channels": primary_channels,
        "secondary_channels": ["Email", "Social media", "Slack communities"],
        "timing_recommendation": timing,
        "estimated_reach": "1000-5000" if platform == "linkedin" else "500-2000"
    }


@tool
def calculate_engagement_score(
    word_count: int,
    header_count: int,
    platform: str,
    content_type: str
) -> Dict[str, float]:
    """Calculate expected engagement metrics.
    
    Args:
        word_count: Total words
        header_count: Number of headers
        platform: Target platform
        content_type: Type of content
        
    Returns:
        Engagement predictions
    """
    # Base engagement by platform
    platform_base = {
        "linkedin": 0.75,
        "medium": 0.65,
        "web": 0.60,
        "github": 0.55
    }
    
    base_score = platform_base.get(platform.lower(), 0.60)
    
    # Adjust for length
    if 1000 <= word_count <= 2000:
        length_multiplier = 1.2
    elif 500 <= word_count < 1000:
        length_multiplier = 1.0
    else:
        length_multiplier = 0.8
    
    # Adjust for structure
    structure_multiplier = 1.0 + (min(header_count, 10) * 0.05)
    
    final_score = min(1.0, base_score * length_multiplier * structure_multiplier)
    
    return {
        "overall_engagement_score": round(final_score, 2),
        "expected_read_rate": round(final_score * 0.7, 2),
        "expected_interaction_rate": round(final_score * 0.15, 2),
        "expected_share_rate": round(final_score * 0.05, 2)
    }
class EnhancedPublisherAgent:
    """
    Enterprise Publisher Agent with:
    - Publication finalization
    - Tool use (quality validation, distribution planning, engagement prediction)
    - Comprehensive metadata generation
    - Multi-platform distribution strategy
    """
    
    def __init__(self):
        self.agent_type = AgentType.PUBLISHER
        self.tools = [validate_content_quality, generate_distribution_plan, calculate_engagement_score]
    
    
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Finalize publication WITHOUT modifying the formatted content body."""

        logger.info("🚀 PUBLISHER: Starting enterprise publication")

        # 1. Get final content – prioritize formatter output (state.content)
        content = state.content

        # Fallback chain, just in case
        if (not content or not content.strip()) and state.formatted_content:
            if hasattr(state.formatted_content, "markdown"):
                content = state.formatted_content.markdown
            elif isinstance(state.formatted_content, str):
                content = state.formatted_content

        if (not content or not content.strip()) and state.edited_content:
            if hasattr(state.edited_content, "body"):
                content = state.edited_content.body
            elif isinstance(state.edited_content, str):
                content = state.edited_content

        if (not content or not content.strip()) and state.draft_content:
            if hasattr(state.draft_content, "body"):
                content = state.draft_content.body
            elif isinstance(state.draft_content, str):
                content = state.draft_content

        if not content or not content.strip():
            logger.error(
                f"No content found. content={bool(state.content)}, "
                f"formatted_content={type(state.formatted_content)}, "
                f"edited_content={type(state.edited_content)}"
            )
            raise RuntimeError("ENTERPRISE: Publisher requires content")

        word_count = len(content.split())
        header_count = content.count("#")
        logger.info(f"🚀 PUBLISHER: Pre-publication content words={word_count}, headers={header_count}")

        # 2. Extract context
        template_config = state.template_config or {}
        platform = (
            state.content_spec.platform
            if state.content_spec
            else template_config.get("platform", "web")
        )
        template_type = template_config.get("template_type", "content")

        # 3. DO NOT call any LLM that can rewrite/summarize the content.
        #    Treat formatter output as final body.
        final_content = content

        # 4. Build base publication metadata
        publication_metadata: Dict[str, Any] = {
            "platform": platform,
            "template_type": template_type,
            "word_count": word_count,
            "header_count": header_count,
        }

        # 5. Optional: add engagement predictions using the tool
        try:
            engagement = calculate_engagement_score.invoke({
                "word_count": word_count,
                "header_count": header_count,
                "platform": platform,
                "content_type": template_type,
            })
            publication_metadata["engagement_predictions"] = engagement
        except Exception as e:
            logger.warning(f"⚠️ Engagement score calculation failed: {e}")

        # 6. Validate quality using the quality tool
        quality_result = validate_content_quality.invoke({"text": final_content})

        if not quality_result["ready_to_publish"]:
            logger.warning(f"⚠️ Quality issues: {quality_result['issues']}")

        # 7. Set final content and publishing context on state
        state.final_content = final_content

        state.publishing_context = {
            "published_at": datetime.now().isoformat(),
            "publication_metadata": publication_metadata,
            "quality_validation": quality_result,
            "status": "published",
        }

        state.update_phase(ContentPhase.COMPLETED)

        state.log_agent_execution(
            self.agent_type,
            {
                "status": "completed",
                "platform": platform,
                "quality_score": quality_result["quality_score"],
                "word_count": quality_result["word_count"],
            },
        )

        logger.info(
            f"✅ PUBLISHER: Completed for platform={platform}, "
            f"final_word_count={quality_result['word_count']}"
        )

        return state
    
    def _llm_format_with_tools(
        self,
        content: str,
        platform: str,
        template_config: Dict,
        style_config: Dict,
        state: EnrichedContentState
    ) -> tuple[str, Dict]:
        """Skip LLM - just return formatted content."""
        
        # Simple AI tell removal
        cleaned = content
        ai_tells = ['delve into', 'leverage', 'utilize', 'in conclusion', 'paradigm shift']
        for tell in ai_tells:
            cleaned = re.sub(r'\b' + tell + r'\b', '', cleaned, flags=re.I)
        
        metadata = {
            "platform": platform,
            "confidence": 0.9,
            "ai_tells_removed": len(content) - len(cleaned)
        }
        
        return cleaned, metadata   
    
    def _build_publication_system_prompt(self, platform: str, template_config: Dict) -> str:
        """Build system prompt for publication."""
        
        template_type = template_config.get('template_type', 'content')
        
        prompt = f"""You are an expert content publisher preparing {template_type} for {platform}.

**Publication Objectives:**
- Ensure content meets professional quality standards
- Optimize for {platform} platform requirements
- Maximize reach and engagement potential
- Validate completeness and polish
- Prepare distribution strategy

**Quality Standards:**
- No placeholder content or TODOs
- Professional tone and formatting
- Complete sections and arguments
- Proper citations and sources
- Platform-optimized structure

**Critical Instructions:**
- Use available tools to validate and optimize
- Ensure content is truly publication-ready
- Never publish incomplete or placeholder content
- Focus on maximizing impact and reach
- Maintain brand and quality standards"""
        
        return prompt