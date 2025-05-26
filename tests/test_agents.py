# tests/test_agents.py

import pytest
from langgraph_app.agents.planner import planner
from langgraph_app.agents.writer import writer
from langgraph_app.agents.formatter import formatter

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
