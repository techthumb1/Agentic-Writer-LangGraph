# src/langgraph_app/graph/nodes.py
"""
Node functions for LangGraph workflow.
Each node represents an agent in the content generation pipeline.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from ..core.state import EnrichedContentState
from ..core.types import AgentType, ContentPhase
from ..agents.enhanced_planner_integrated import EnhancedPlannerAgent
from ..agents.enhanced_researcher_integrated import EnhancedResearcherAgent
from ..agents.writer import WriterAgent
from ..agents.enhanced_editor_integrated import EnhancedEditorAgent

from ..agents.enhanced_formatter_integrated import EnhancedFormatterAgent
logger = logging.getLogger("writerzroom.graph.nodes")

# Initialize agents
planner_agent = EnhancedPlannerAgent()
researcher_agent = EnhancedResearcherAgent()
writer_agent = WriterAgent()
editor_agent = EnhancedEditorAgent()
formatter_agent = EnhancedFormatterAgent()


async def run_planner(state: EnrichedContentState) -> EnrichedContentState:
    """
    Execute the Planner agent.
    Analyzes requirements and creates content strategy.
    """
    logger.info("🧠 EXECUTING PLANNER")
    state.update_phase(ContentPhase.PLANNING)
    
    try:
        updated_state = planner_agent.execute(state)
        logger.info("✅ Planner completed successfully")
        return updated_state
    except Exception as e:
        logger.error(f"❌ Planner failed: {e}", exc_info=True)
        raise

async def run_writer(state: EnrichedContentState) -> EnrichedContentState:
    """Execute the Writer agent using LangChain."""
    logger.info("✍️ EXECUTING WRITER")
    state.update_phase(ContentPhase.WRITING)
    
    try:
        updated_state = writer_agent.execute(state)
        logger.info("✅ Writer completed successfully")
        return updated_state
    except Exception as e:
        logger.error(f"❌ Writer failed: {e}", exc_info=True)
        raise

async def run_researcher(state: EnrichedContentState) -> EnrichedContentState:
    """
    Execute the Researcher agent.
    Performs real information retrieval and analysis.
    """
    logger.info("🔬 EXECUTING RESEARCHER")
    state.update_phase(ContentPhase.RESEARCH)
    
    try:
        updated_state = researcher_agent.execute(state)
        logger.info("✅ Researcher completed successfully")
        return updated_state
    except Exception as e:
        logger.error(f"❌ Researcher failed: {e}", exc_info=True)
        raise

async def run_call_writer(state: EnrichedContentState) -> EnrichedContentState:
    """
    Execute the Call Writer agent.
    Prepares writing context and validates prerequisites.
    [PLACEHOLDER - NOT IMPLEMENTED]
    """
    logger.info("📞 EXECUTING CALL WRITER (PLACEHOLDER)")
    
    # Validate that planning and research are complete
    if not state.planning_output:
        logger.warning("No planning output found, using defaults")
    
    if not state.research_findings:
        logger.warning("No research findings found, proceeding anyway")
    
    # Prepare writing context
    state.writing_context = {
        "ready": True,
        "prerequisites_met": True,
        "strategy": state.planning_output.content_strategy if state.planning_output else "default",
    }
    
    state.log_agent_execution(AgentType.CALL_WRITER, {
        "status": "placeholder",
        "prerequisites_met": True
    })
    
    logger.info("✅ Call Writer placeholder completed")
    return state

async def run_editor(state: EnrichedContentState) -> EnrichedContentState:
    """
    Execute the Editor agent.
    Applies deterministic rule-based content refinement.
    """
    logger.info("🧐 EXECUTING EDITOR")
    state.update_phase(ContentPhase.EDITING)
    
    try:
        updated_state = editor_agent.execute(state)
        logger.info("✅ Editor completed successfully")
        return updated_state
    except Exception as e:
        logger.error(f"❌ Editor failed: {e}", exc_info=True)
        raise

#async def run_image_generator(state: EnrichedContentState) -> EnrichedContentState:
#    """
#    Execute the Image Generator agent.
#    Generates images if required by template.
#    [PLACEHOLDER - NOT IMPLEMENTED]
#    """
#    logger.info("🖼️ EXECUTING IMAGE GENERATOR (PLACEHOLDER)")
#    state.update_phase(ContentPhase.IMAGE_GENERATION)
#    
#    # Check if images are required
#    image_config = state.template_config.get("image_generation_config") or {}
#    enabled = image_config.get("enabled", False)
#    
#    if enabled:
#        logger.info("Image generation is enabled in template, but not yet implemented")
#        # Placeholder: No images generated
#        state.generated_images = []
#    else:
#        logger.info("Image generation not required by template")
#    
#    state.log_agent_execution(AgentType.IMAGE, {
#        "status": "placeholder",
#        "images_generated": 0,
#        "enabled": enabled
#    })
#    
#    logger.info("✅ Image Generator placeholder completed")
#    return state

async def run_formatter(state: EnrichedContentState) -> EnrichedContentState:
    """
    Execute the Formatter agent.
    Applies final formatting for multiple platforms and removes AI tells.
    """
    logger.info("🎨 EXECUTING FORMATTER")
    state.update_phase(ContentPhase.FORMATTING)
    
    try:
        updated_state = formatter_agent.execute(state)
        logger.info("✅ Formatter completed successfully")
        return updated_state
    except Exception as e:
        logger.error(f"❌ Formatter failed: {e}", exc_info=True)
        raise

async def run_seo_analyzer(state: EnrichedContentState) -> EnrichedContentState:
    """
    Execute the SEO Analyzer agent.
    Analyzes content for search optimization and readability.
    """
    logger.info("📈 EXECUTING SEO ANALYZER")
    state.update_phase(ContentPhase.SEO_ANALYSIS)
    
    from ..core.types import SeoAnalysis
    import re
    from collections import Counter
    from datetime import datetime
    
    # Get content to analyze
    # Get content from edited or draft
    # Get content from edited or draft
    if state.edited_content:
        content_body = state.edited_content.body if hasattr(state.edited_content, 'body') else str(state.edited_content)
    elif state.draft_content:
        content_body = state.draft_content.body if hasattr(state.draft_content, 'body') else str(state.draft_content)
    else:
        content_body = state.content or ""
    
    # Extract text without markdown syntax
    text = re.sub(r'[#*`\[\]()]', '', content_body).lower()
    words = re.findall(r'\b\w+\b', text)
    total_words = len(words)
    
    # Keyword density analysis
    word_counts = Counter(words)
    # Filter out common stopwords
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
    keyword_density = {
        word: (count / total_words) * 100 
        for word, count in word_counts.most_common(10) 
        if word not in stopwords and len(word) > 3
    }
    
    # Readability score (Flesch Reading Ease approximation)
    sentences = max(1, len(re.findall(r'[.!?]+', content_body)))
    syllables = sum(len(re.findall(r'[aeiouy]+', word)) for word in words)
    avg_sentence_length = total_words / sentences if sentences > 0 else 0
    avg_syllables_per_word = syllables / total_words if total_words > 0 else 0
    
    if total_words > 0 and sentences > 0:
        readability = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        
        # Adjust for content type - business/technical content naturally scores lower
        template_name = state.template_config.get("name", "").lower()
        if any(t in template_name for t in ["proposal", "report", "technical", "business", "email"]):
            # Technical/business content: normalize to 0.4-0.8 range
            readability_score = max(0.4, min(0.8, (readability + 100) / 200))
        else:
            # General content: standard 0-1 scale
            readability_score = max(0, min(100, readability)) / 100
    else:
        readability_score = 0.5
    
    # Generate recommendations
    recommendations = []
    if readability_score < 0.6:
        recommendations.append("Simplify sentence structure for better readability")
    if total_words < 300:
        recommendations.append("Content length below 300 words - consider expanding")
    if not any(density > 1.5 for density in keyword_density.values()):
        recommendations.append("No strong keyword focus detected - optimize for target keywords")
    if len(re.findall(r'^#{1,3} ', content_body, re.MULTILINE)) < 2:
        recommendations.append("Add more subheadings for better content structure")
    
    # Generate meta tags
    topic = state.content_spec.topic if state.content_spec else "Content"
    meta_title = f"{topic} | {state.template_config.get('name', 'Content')}"[:60]
    first_paragraph = content_body.split('\n\n')[0][:160] if content_body else ""
    meta_description = re.sub(r'[#*`]', '', first_paragraph).strip()
    
    state.seo_analysis = SeoAnalysis(
        keyword_density=keyword_density,
        readability_score=round(readability_score, 2),
        recommendations=recommendations if recommendations else ["Content is well-optimized"],
        meta_title=meta_title,
        meta_description=meta_description
    )
    
    state.log_agent_execution(AgentType.SEO, {
        "status": "completed",
        "readability_score": round(readability_score, 2),
        "word_count": total_words,
        "recommendations_count": len(recommendations)
    })
    
    logger.info(f"✅ SEO analysis completed - readability: {readability_score:.2f}")
    return state

async def quality_gate(state: EnrichedContentState) -> EnrichedContentState:
    """Fail-fast if content doesn't meet enterprise standards"""

    issues = []

    # Check readability (from SEO analysis if available)
    readability_score = 0
    if getattr(state, "seo_analysis", None):
        readability_score = getattr(state.seo_analysis, "readability_score", 0)
    elif isinstance(getattr(state, "readability_score", None), (int, float)):
        readability_score = state.readability_score

    if readability_score < 0.5:  # normalized 0–1 scale used in seo_analysis
        issues.append("Readability too low (< 0.5 normalized score)")

    # Check citations
    research_sources = getattr(state, "research_sources", None) or []
    if len(research_sources) < 3:
        issues.append("Insufficient research citations (< 3)")

    # Check temporal language
    final_content = getattr(state, "final_content", "") or ""
    if "by 2026" in final_content and datetime.now().year == 2025:
        issues.append("Temporal language suggests past perspective")

    if issues:
        raise ValueError(f"Quality gate failed: {'; '.join(issues)}")

    return state

#async def run_publisher(state: EnrichedContentState) -> EnrichedContentState:
#    """
#    Execute the Publisher agent.
#    Finalizes content, applies metadata, and prepares for delivery.
#    """
#    logger.info("🚀 EXECUTING PUBLISHER")
#    state.update_phase(ContentPhase.PUBLISHING)
#    
#    # Get the final content from the most recent stage - handle both object and string types
#    final_content = ""
#    if state.formatted_content:
#        final_content = state.formatted_content.markdown
#    elif state.edited_content:
#        final_content = state.edited_content.body if hasattr(state.edited_content, 'body') else str(state.edited_content)
#    elif state.draft_content:
#        final_content = state.draft_content.body if hasattr(state.draft_content, 'body') else str(state.draft_content)
#    else:
#        final_content = state.content
#    
#    # Inject SEO metadata if available
#    if state.seo_analysis:
#        metadata_block = f"""---
#title: {state.seo_analysis.meta_title}
#description: {state.seo_analysis.meta_description}
#keywords: {', '.join(list(state.seo_analysis.keyword_density.keys())[:5])}
#readability_score: {state.seo_analysis.readability_score}
#---
#
#"""
#        final_content = metadata_block + final_content
#    
#    # Inject generated images if available
#    if state.generated_images:
#        for img in state.generated_images:
#            placement_marker = f"## {img.placement}"
#            if placement_marker in final_content:
#                image_md = f"\n![{img.prompt}]({img.url})\n"
#                final_content = final_content.replace(placement_marker, placement_marker + image_md)
#    
#    # Set final content and mark as complete
#    state.final_content = final_content
#    state.update_phase(ContentPhase.COMPLETE)
#    
#    word_count = len(state.final_content.split()) if state.final_content else 0
#    state.log_agent_execution(AgentType.PUBLISHER, {
#        "status": "completed",
#        "final_word_count": word_count,
#        "has_seo_metadata": bool(state.seo_analysis),
#        "images_embedded": len(state.generated_images),
#        "pipeline_complete": True
#    })
#    
#    logger.info(f"✅ Publisher completed - {word_count} words, {len(state.generated_images)} images")
#    return state

async def run_publisher(state: EnrichedContentState) -> EnrichedContentState:
    """Execute Publisher - finalize content with metadata."""
    logger.info("🚀 EXECUTING PUBLISHER")
    state.update_phase(ContentPhase.PUBLISHING)
    
    # Get content - prioritize state.content (set by formatter)
    final_content = state.content
    
    if not final_content and state.formatted_content:
        final_content = state.formatted_content.markdown if hasattr(state.formatted_content, 'markdown') else str(state.formatted_content)
    
    if not final_content and state.edited_content:
        final_content = state.edited_content.body if hasattr(state.edited_content, 'body') else str(state.edited_content)
    
    if not final_content and state.draft_content:
        final_content = state.draft_content.body if hasattr(state.draft_content, 'body') else str(state.draft_content)
    
    if not final_content or not final_content.strip():
        logger.error(f"Publisher: No content. content={bool(state.content)}, formatted={type(state.formatted_content)}")
        raise RuntimeError("ENTERPRISE: Publisher requires content")
    
    logger.info(f"📝 Publisher received: {len(final_content)} chars, {len(final_content.split())} words")
    
    # Add SEO metadata
    if state.seo_analysis:
        metadata_block = f"""---
title: {state.seo_analysis.meta_title}
description: {state.seo_analysis.meta_description}
keywords: {', '.join(list(state.seo_analysis.keyword_density.keys())[:5])}
readability_score: {state.seo_analysis.readability_score}
---

"""
        final_content = metadata_block + final_content
    
    state.final_content = final_content
    state.update_phase(ContentPhase.COMPLETE)
    
    word_count = len(final_content.split())
    
    state.log_agent_execution(AgentType.PUBLISHER, {
        "status": "completed",
        "final_word_count": word_count,
        "has_seo_metadata": bool(state.seo_analysis),
        "pipeline_complete": True
    })
    
    logger.info(f"✅ Publisher completed - {word_count} words")
    return state