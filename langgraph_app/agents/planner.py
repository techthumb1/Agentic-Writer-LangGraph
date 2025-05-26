# langgraph_app/agents/planner.py

import yaml
from langchain_core.runnables import RunnableLambda

def _planner_fn(state: dict) -> dict:
    with open("content_templates/federated_learning_101.yaml", "r") as f:
        data = yaml.safe_load(f)

    return {
        "topic": data["title"],
        "audience": data["audience"],
        "tags": data["tags"],
    }

planner: RunnableLambda = RunnableLambda(_planner_fn)
