# graph.py
# langgraph_app/graph.py

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START

# === Step 1: Define the state structure ===
class GraphState(TypedDict):
    topic: str
    audience: str
    tags: list[str]
    draft: str
    formatted_article: str

# === Step 2: Import agent node functions ===
from langgraph_app.agents.planner import planner
from langgraph_app.agents.writer import writer
from langgraph_app.agents.formatter import formatter

# === Step 3: Build the graph ===
builder = StateGraph(GraphState)

# Add nodes
builder.add_node("planner", planner)
builder.add_node("writer", writer)
builder.add_node("formatter", formatter)

# Define edges
builder.set_entry_point("planner")
builder.add_edge("planner", "writer")
builder.add_edge("writer", "formatter")
builder.set_finish_point("formatter")

# Compile the graph
graph = builder.compile()
