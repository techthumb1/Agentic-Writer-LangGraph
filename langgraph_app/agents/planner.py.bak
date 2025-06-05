# langgraph_app/agents/planner.py
import yaml
from langchain_core.runnables import RunnableLambda

def _planner_fn(state: dict) -> dict:
    template_path = state.get("template_path", "content_templates/federated_learning_101.yaml")
    style_path = state.get("style_path", "style_profiles/jason.yaml")

    with open(template_path, "r") as f:
        data = yaml.safe_load(f)

    with open(style_path, "r") as f:
        style = yaml.safe_load(f)

    return {
        "topic": data["title"],
        "audience": data["audience"],
        "tags": data["tags"],
        "tone": data.get("tone", "educational"),
        "platform": data.get("platform", "substack"),
        "length": data.get("length", "short"),
        "code": data.get("code", False),
        "style_profile": style
    }

planner: RunnableLambda = RunnableLambda(_planner_fn)
