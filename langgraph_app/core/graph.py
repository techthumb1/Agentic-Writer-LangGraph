# graph.py — FINAL FIXED VERSION
# Uses ONLY real nodes; removes all placeholder logic.

from langgraph.graph import StateGraph, END
from langgraph_app.core.types import AgentType
from .state import EnrichedContentState
from graph.nodes import (
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


def build_content_graph() -> StateGraph:
    """
    Final WriterzRoom MAS execution graph.
    Correct sequence:
        planner → researcher → call_writer → writer → editor → image → formatter → seo → publisher
    No fallbacks. No placeholders.
    """

    workflow = StateGraph(EnrichedContentState)

    # Nodes — REAL agents only
    workflow.add_node(AgentType.PLANNER.value, run_planner)
    workflow.add_node(AgentType.RESEARCHER.value, run_researcher)
    workflow.add_node(AgentType.CALL_WRITER.value, run_call_writer)
    workflow.add_node(AgentType.WRITER.value, run_writer)
    workflow.add_node(AgentType.EDITOR.value, run_editor)
    #workflow.add_node(AgentType.IMAGE.value, run_image_generator)
    workflow.add_node(AgentType.FORMATTER.value, run_formatter)
    workflow.add_node(AgentType.SEO.value, run_seo_analyzer)
    workflow.add_node(AgentType.PUBLISHER.value, run_publisher)

    # Workflow edges — EXACT pipeline
    workflow.set_entry_point(AgentType.PLANNER.value)

    workflow.add_edge(AgentType.PLANNER.value, AgentType.RESEARCHER.value)
    workflow.add_edge(AgentType.RESEARCHER.value, AgentType.CALL_WRITER.value)
    workflow.add_edge(AgentType.CALL_WRITER.value, AgentType.WRITER.value)
    workflow.add_edge(AgentType.WRITER.value, AgentType.EDITOR.value)
    #workflow.add_edge(AgentType.EDITOR.value, AgentType.IMAGE.value)
    #workflow.add_edge(AgentType.IMAGE.value, AgentType.FORMATTER.value)
    workflow.add_edge(AgentType.FORMATTER.value, AgentType.SEO.value)
    workflow.add_edge(AgentType.SEO.value, AgentType.PUBLISHER.value)
    workflow.add_edge(AgentType.PUBLISHER.value, END)

    return workflow
