# src/langgraph_app/graph/builder.py
"""
LangGraph workflow builder.
Constructs the state graph for multi-agent content generation.
"""

import logging
from typing import Callable, Literal

from langgraph.graph import StateGraph, END

from ..core.state import EnrichedContentState
from ..core.types import AgentType, ContentPhase
from .nodes import (
    run_planner,
    run_researcher,
    run_call_writer,
    run_writer,
    run_editor,
    #run_image_generator,
    run_formatter,
    run_seo_analyzer,
    run_publisher,
)

logger = logging.getLogger("writerzroom.graph.builder")


def should_run_seo(state: EnrichedContentState) -> Literal["run_seo", "skip_seo"]:
    """
    Conditional logic to determine if SEO agent should run.
    Based on template metadata strategy.
    """
    if not state.template_config:
        return "skip_seo"
    
    strategy = state.template_config.get("metadata", {}).get("strategy", "")
    distribution = state.template_config.get("distribution_channels", [])
    
    # Run SEO if strategy mentions it or if web distribution is required
    if "seo" in strategy.lower() or "web" in distribution:
        logger.info(f"SEO agent required based on strategy: {strategy}")
        return "run_seo"
    
    logger.info("SEO agent skipped")
    return "skip_seo"


def build_content_generation_graph() -> Callable:
    """
    Builds and compiles the LangGraph workflow for content generation.
    
    Returns:
        Compiled LangGraph runnable
    """
    logger.info("Building content generation graph...")
    
    workflow = StateGraph(EnrichedContentState)
    
    # Add all agent nodes
    workflow.add_node(AgentType.PLANNER.value, run_planner)
    workflow.add_node(AgentType.RESEARCHER.value, run_researcher)
    workflow.add_node(AgentType.CALL_WRITER.value, run_call_writer)
    workflow.add_node(AgentType.WRITER.value, run_writer)
    workflow.add_node(AgentType.EDITOR.value, run_editor)
    #workflow.add_node(AgentType.IMAGE.value, run_image_generator)
    workflow.add_node(AgentType.FORMATTER.value, run_formatter)
    workflow.add_node(AgentType.SEO.value, run_seo_analyzer)
    workflow.add_node(AgentType.PUBLISHER.value, run_publisher)
    
    # Define the deterministic flow
    workflow.set_entry_point(AgentType.PLANNER.value)
    
    # Linear edges
    workflow.add_edge(AgentType.PLANNER.value, AgentType.RESEARCHER.value)
    workflow.add_edge(AgentType.RESEARCHER.value, AgentType.CALL_WRITER.value)
    workflow.add_edge(AgentType.CALL_WRITER.value, AgentType.WRITER.value)
    workflow.add_edge(AgentType.WRITER.value, AgentType.EDITOR.value)
    workflow.add_edge(AgentType.EDITOR.value, AgentType.FORMATTER.value)
    #workflow.add_edge(AgentType.EDITOR.value, AgentType.IMAGE.value)
    #workflow.add_edge(AgentType.IMAGE.value, AgentType.FORMATTER.value)
    
    # Conditional edge for optional SEO
    workflow.add_conditional_edges(
        AgentType.FORMATTER.value,
        should_run_seo,
        {
            "run_seo": AgentType.SEO.value,
            "skip_seo": AgentType.PUBLISHER.value,
        },
    )
    
    # Final edges
    workflow.add_edge(AgentType.SEO.value, AgentType.PUBLISHER.value)
    workflow.add_edge(AgentType.PUBLISHER.value, END)
    
    logger.info("Content generation graph built successfully")
    return workflow.compile()