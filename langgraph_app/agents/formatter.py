# langgraph_app/agents/formatter.py

from langchain_core.runnables import RunnableLambda

def _formatter_fn(state: dict) -> dict:
    draft = state.get("draft", "No Draft Found")
    wrapped = f"<html><body>{draft}</body></html>"
    return {"formatted_article": wrapped}


def load_style_profile(name: str) -> dict:
    try:
        import yaml
        with open(f"data/style_profiles/{name}.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Style profile not found: {name}.yaml")

def load_content_template(name: str) -> dict:
    try:
        import yaml
        with open(f"data/content_templates/{name}.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Template not found: {name}.yaml")

formatter: RunnableLambda = RunnableLambda(_formatter_fn)
