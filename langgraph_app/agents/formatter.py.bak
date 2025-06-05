# langgraph_app/agents/formatter.py

from langchain_core.runnables import RunnableLambda

def _formatter_fn(state: dict) -> dict:
    draft = state.get("draft", "No Draft Found")
    wrapped = f"<html><body>{draft}</body></html>"
    return {"formatted_article": wrapped}

formatter: RunnableLambda = RunnableLambda(_formatter_fn)
