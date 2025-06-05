# langgraph_app/graph.py

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

from langgraph_app.agents.planner import planner
from langgraph_app.agents.researcher import researcher
from langgraph_app.agents.writer import writer
from langgraph_app.agents.editor import editor
from langgraph_app.agents.code_agent import code_agent
from langgraph_app.agents.formatter import formatter
from langgraph_app.agents.image_agent import image_agent
from langgraph_app.agents.seo_agent import seo_agent
from langgraph_app.agents.publisher import publisher

class GraphState(TypedDict):
    topic: str
    audience: str
    tags: list[str]
    tone: str
    platform: str
    length: str
    code: bool
    research: str
    draft: str
    edited_draft: str
    code_block: str
    formatted_article: str
    cover_image_url: str
    slug: str
    seo_output: str
    substack_status: str
    medium_import_path: str
    import_url: str

builder = StateGraph(GraphState)

# Agents
builder.add_node("planner", planner)
builder.add_node("researcher", researcher)
builder.add_node("writer", writer)
builder.add_node("editor", editor)
builder.add_node("code_agent", code_agent)
builder.add_node("formatter", formatter)
builder.add_node("image_agent", image_agent)
builder.add_node("seo_agent", seo_agent)
builder.add_node("publisher", publisher)

# Graph flow
builder.set_entry_point("planner")
builder.add_edge("planner", "researcher")
builder.add_edge("researcher", "writer")
builder.add_edge("writer", "editor")
builder.add_edge("editor", "code_agent")
builder.add_edge("code_agent", "formatter")
builder.add_edge("formatter", "image_agent")
builder.add_edge("image_agent", "seo_agent")
builder.set_finish_point("seo_agent")  # Pause before publishing

graph = builder.compile()
