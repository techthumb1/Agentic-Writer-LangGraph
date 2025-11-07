# src/langgraph_app/core/graph.py
"""
Defines the final, refactored StateGraph for the multi-agent content generation system.
This file orchestrates the flow of the EnrichedContentState between agent nodes.
"""
from __future__ import annotations

from langgraph.graph import StateGraph, END
from typing import Callable, Literal

from .state import EnrichedContentState
from .types import AgentType, ContentPhase

# Import real agents
from ..agents.planner import PlannerAgent

# Initialize agents
planner_agent = PlannerAgent()


# --- Agent Node Functions ---

async def run_planner(state: EnrichedContentState) -> EnrichedContentState:
    """Execute the Planner agent."""
    print("--- 🧠 EXECUTING PLANNER ---")
    return planner_agent.execute(state)


# --- Placeholder nodes for agents not yet refactored ---

async def run_researcher(state: EnrichedContentState) -> EnrichedContentState:
    """Placeholder for the Researcher agent."""
    print("--- 🔬 EXECUTING RESEARCHER (PLACEHOLDER) ---")
    state.update_phase(ContentPhase.RESEARCH)
    state.log_agent_execution(AgentType.RESEARCHER, {"status": "placeholder"})
    return state


async def run_call_writer(state: EnrichedContentState) -> EnrichedContentState:
    """Placeholder for the Call Writer agent."""
    print("--- 📞 EXECUTING CALL WRITER (PLACEHOLDER) ---")
    state.log_agent_execution(AgentType.CALL_WRITER, {"status": "placeholder"})
    return state


async def run_writer(state: EnrichedContentState) -> EnrichedContentState:
    """Placeholder for the Writer agent."""
    print("--- ✍️ EXECUTING WRITER (PLACEHOLDER) ---")
    state.update_phase(ContentPhase.WRITING)
    state.content = "Placeholder content from writer"
    state.log_agent_execution(AgentType.WRITER, {"status": "placeholder"})
    return state


async def run_editor(state: EnrichedContentState) -> EnrichedContentState:
    """Placeholder for the Editor agent."""
    print("--- 🧐 EXECUTING EDITOR (PLACEHOLDER) ---")
    state.log_agent_execution(AgentType.EDITOR, {"status": "placeholder"})
    return state


async def run_image_generator(state: EnrichedContentState) -> EnrichedContentState:
    """Placeholder for the Image Generator agent."""
    print("--- 🖼️ EXECUTING IMAGE GENERATOR (PLACEHOLDER) ---")
    state.log_agent_execution(AgentType.IMAGE, {"status": "placeholder"})
    return state


async def run_formatter(state: EnrichedContentState) -> EnrichedContentState:
    """Placeholder for the Formatter agent."""
    print("--- 🎨 EXECUTING FORMATTER (PLACEHOLDER) ---")
    state.log_agent_execution(AgentType.FORMATTER, {"status": "placeholder"})
    return state


async def run_seo_analyzer(state: EnrichedContentState) -> EnrichedContentState:
    """Placeholder for the SEO Analyzer agent."""
    print("--- 📈 EXECUTING SEO ANALYZER (PLACEHOLDER) ---")
    state.log_agent_execution(AgentType.SEO, {"status": "placeholder"})
    return state


async def run_publisher(state: EnrichedContentState) -> EnrichedContentState:
    """Placeholder for the Publisher agent."""
    print("--- 🚀 EXECUTING PUBLISHER (PLACEHOLDER) ---")
    state.final_content = state.content
    state.update_phase(ContentPhase.COMPLETE)
    state.log_agent_execution(AgentType.PUBLISHER, {"status": "placeholder"})
    return state


# --- Conditional Logic ---

def should_run_seo(state: EnrichedContentState) -> Literal["run_seo", "skip_seo"]:
    """Determines if the SEO agent should run."""
    print("--- 🧭 DECIDING ON SEO ---")
    if not state.template_config:
        return "skip_seo"
    
    strategy = state.template_config.get("metadata", {}).get("strategy", "")
    if "seo" in strategy.lower() or "web" in strategy.lower():
        print("Decision: SEO required.")
        return "run_seo"
    print("Decision: SEO not required.")
    return "skip_seo"


# --- Graph Builder ---

def build_graph() -> Callable[[EnrichedContentState], EnrichedContentState]:
    """Builds and compiles the deterministic, enterprise-grade LangGraph."""
    workflow = StateGraph(EnrichedContentState)

    # Add nodes using the AgentType enum for consistency
    workflow.add_node(AgentType.PLANNER.value, run_planner)
    workflow.add_node(AgentType.RESEARCHER.value, run_researcher)
    workflow.add_node(AgentType.CALL_WRITER.value, run_call_writer)
    workflow.add_node(AgentType.WRITER.value, run_writer)
    workflow.add_node(AgentType.EDITOR.value, run_editor)
    workflow.add_node(AgentType.IMAGE.value, run_image_generator)
    workflow.add_node(AgentType.FORMATTER.value, run_formatter)
    workflow.add_node(AgentType.SEO.value, run_seo_analyzer)
    workflow.add_node(AgentType.PUBLISHER.value, run_publisher)

    # Define the deterministic flow
    workflow.set_entry_point(AgentType.PLANNER.value)
    workflow.add_edge(AgentType.PLANNER.value, AgentType.RESEARCHER.value)
    workflow.add_edge(AgentType.RESEARCHER.value, AgentType.CALL_WRITER.value)
    workflow.add_edge(AgentType.CALL_WRITER.value, AgentType.WRITER.value)
    workflow.add_edge(AgentType.WRITER.value, AgentType.EDITOR.value)
    workflow.add_edge(AgentType.EDITOR.value, AgentType.IMAGE.value)
    workflow.add_edge(AgentType.IMAGE.value, AgentType.FORMATTER.value)
    
    # Add a conditional edge for the optional SEO step
    workflow.add_conditional_edges(
        AgentType.FORMATTER.value,
        should_run_seo,
        {
            "run_seo": AgentType.SEO.value,
            "skip_seo": AgentType.PUBLISHER.value,
        },
    )

    # Final sequence
    workflow.add_edge(AgentType.SEO.value, AgentType.PUBLISHER.value)
    workflow.add_edge(AgentType.PUBLISHER.value, END)

    # The compiled graph is a LangChain Runnable
    return workflow.compile()


# Export a single, ready-to-use compiled graph instance for the application
main_graph = build_graph()