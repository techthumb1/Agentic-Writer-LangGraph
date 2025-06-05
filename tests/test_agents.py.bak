# tests/test_agents.py

import pytest
from langgraph_app.agents.planner import planner
from langgraph_app.agents.writer import writer
from langgraph_app.agents.formatter import formatter
from langgraph_app.agents.image_agent import image_agent
from langgraph_app.agents.editor import editor

def test_planner_reads_yaml():
    output = planner.invoke({})
    assert "topic" in output
    assert "audience" in output
    assert isinstance(output["tags"], list)

def test_writer_generates_text():
    planner_out = planner.invoke({})
    writer_out = writer.invoke(planner_out)
    assert "draft" in writer_out
    assert len(writer_out["draft"]) > 30

def test_formatter_wraps_html():
    wrapped = formatter.invoke({"draft": "Test Draft"})
    assert wrapped["formatted_article"].startswith("<html>")

def test_image_agent_generates_url():
    planner_out = planner.invoke({})
    result = image_agent.invoke(planner_out)
    assert result["cover_image_url"].startswith("http")

def test_editor_agent_polishes_text():
    draft = {
        "draft": "this is a sample. it should be polished for better readability and tone.",
        "tone": "educational"
    }
    result = editor.invoke(draft)
    assert "This is a sample" in result["edited_draft"]

from langgraph_app.agents.seo_agent import seo_agent

def test_seo_agent_generates_slug_and_metadata():
    state = {
        "topic": "Federated Learning for Beginners",
        "audience": "AI engineers",
        "tags": ["federated learning", "privacy", "edge"],
        "tone": "educational"
    }
    result = seo_agent.invoke(state)
    assert result["slug"] == "federated-learning-for-beginners"
    assert "meta" in result["seo_output"].lower()

from langgraph_app.agents.publisher import publisher

def test_publisher_agent_creates_medium_draft(monkeypatch):
    test_state = {
        "topic": "Federated Learning for Beginners",
        "formatted_article": "<html><body><h1>Test</h1><p>This is a test post</p></body></html>",
        "tags": ["federated learning", "privacy"]
    }

    # Optional: monkeypatch the _get_medium_user_id if you want to fake ID
    result = publisher.invoke(test_state)
    assert result["medium_post_url"].startswith("https://medium.com/")

def test_publisher_agent_sends_via_brevo_and_exports():
    state = {
        "topic": "Federated Learning for Beginners",
        "slug": "federated-learning-for-beginners",
        "formatted_article": "<html><body><h1>Test</h1><p>This is a test post</p></body></html>",
        "tags": ["federated learning", "privacy"]
    }
    result = publisher.invoke(state)
    assert "Brevo" in result["substack_status"]
    assert result["medium_import_path"].endswith(".html")
