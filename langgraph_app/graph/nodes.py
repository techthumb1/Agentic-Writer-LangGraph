# src/langgraph_app/graph/nodes.py
"""
Node functions for LangGraph workflow.
Each node represents an agent in the content generation pipeline.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from langgraph_app.core.state import EnrichedContentState
from langgraph_app.core.types import AgentType, ContentPhase

# Correct agent paths
from langgraph_app.agents.enhanced_planner_integrated import EnhancedPlannerAgent
from langgraph_app.agents.enhanced_researcher_integrated import EnhancedResearcherAgent
from langgraph_app.agents.enhanced_call_writer_integrated import EnhancedCallWriterAgent
from langgraph_app.agents.writer import WriterAgent
from langgraph_app.agents.enhanced_editor_integrated import EnhancedEditorAgent
from langgraph_app.agents.enhanced_formatter_integrated import EnhancedFormatterAgent
from langgraph_app.agents.enhanced_seo_agent_integrated import EnhancedSEOAgent
from langgraph_app.agents.enhanced_publisher_integrated import EnhancedPublisherAgent

logger = logging.getLogger("writerzroom.graph.nodes")

# Instantiate agents
planner_agent = EnhancedPlannerAgent()
researcher_agent = EnhancedResearcherAgent()
call_writer_agent = EnhancedCallWriterAgent()
writer_agent = WriterAgent()
editor_agent = EnhancedEditorAgent()
formatter_agent = EnhancedFormatterAgent()
seo_agent = EnhancedSEOAgent()
publisher_agent = EnhancedPublisherAgent()


# ---------------------------------------------------------
# PLANNER
# ---------------------------------------------------------
async def run_planner(state: EnrichedContentState) -> EnrichedContentState:
    logger.info("🧠 EXECUTING PLANNER")
    state.update_phase(ContentPhase.PLANNING)

    updated_state = planner_agent.execute(state)
    logger.info("✅ Planner completed")

    return updated_state


# ---------------------------------------------------------
# RESEARCHER
# ---------------------------------------------------------
def run_researcher(state: EnrichedContentState) -> EnrichedContentState:
    logger.info("🔬 EXECUTING RESEARCHER")
    state.update_phase(ContentPhase.RESEARCH)

    updated_state = researcher_agent.execute(state)
    logger.info("✅ Researcher completed")

    return updated_state


# ---------------------------------------------------------
# CALL WRITER
# ---------------------------------------------------------
async def run_call_writer(state: EnrichedContentState) -> EnrichedContentState:
    logger.info("📞 EXECUTING CALL WRITER")
    state.update_phase(ContentPhase.WRITING)

    if not state.planning_output or not state.research_findings:
        raise RuntimeError("ENTERPRISE: Call Writer requires both planning_output and research_findings.")

    updated_state = await call_writer_agent.execute(state)
    logger.info("✅ Call Writer completed")

    return updated_state


# ---------------------------------------------------------
# WRITER
# ---------------------------------------------------------
def run_writer(state: EnrichedContentState) -> EnrichedContentState:
    logger.info("✍️ EXECUTING WRITER")
    state.update_phase(ContentPhase.WRITING)

    # Force new generation mode
    state.content_to_edit = None

    updated_state = writer_agent.execute(state)
    logger.info("✅ Writer completed")

    return updated_state


# ---------------------------------------------------------
# EDITOR
# ---------------------------------------------------------
def run_editor(state: EnrichedContentState) -> EnrichedContentState:
    logger.info("🧐 EXECUTING EDITOR")
    state.update_phase(ContentPhase.EDITING)

    updated_state = editor_agent.execute(state)
    logger.info("✅ Editor completed")

    return updated_state


# ---------------------------------------------------------
# FORMATTER
# ---------------------------------------------------------
async def run_formatter(state: EnrichedContentState) -> EnrichedContentState:
    logger.info("🎨 EXECUTING FORMATTER")
    state.update_phase(ContentPhase.FORMATTING)

    updated_state = formatter_agent.execute(state)
    logger.info("✅ Formatter completed")

    return updated_state


# ---------------------------------------------------------
# SEO ANALYZER
# ---------------------------------------------------------
def run_seo_analyzer(state: EnrichedContentState) -> EnrichedContentState:
    logger.info("📈 EXECUTING SEO AGENT")
    state.update_phase(ContentPhase.SEO_ANALYSIS)

    updated_state = seo_agent.execute(state)
    logger.info("✅ SEO completed")

    return updated_state


# ---------------------------------------------------------
# QUALITY GATE
# ---------------------------------------------------------
async def quality_gate(state: EnrichedContentState) -> EnrichedContentState:
    issues = []

    readability_score = getattr(
        getattr(state, "seo_analysis", None), 
        "readability_score", 
        0
    )

    if readability_score < 0.5:
        issues.append("Readability below threshold")

    research_sources = getattr(state, "research_sources", [])
    if len(research_sources) < 3:
        issues.append("Insufficient citations")

    if "by 2026" in (state.final_content or ""):
        issues.append("Temporal mismatch")

    if issues:
        raise ValueError("Quality gate failed: " + "; ".join(issues))

    return state


# ---------------------------------------------------------
# PUBLISHER
# ---------------------------------------------------------
async def run_publisher(state: EnrichedContentState) -> EnrichedContentState:
    logger.info("🚀 EXECUTING PUBLISHER")
    state.update_phase(ContentPhase.PUBLISHING)

    updated_state = publisher_agent.execute(state)
    logger.info("✅ Publisher completed")

    return updated_state