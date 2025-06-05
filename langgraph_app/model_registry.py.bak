import os

def get_model(agent_name: str) -> str:
    """
    Returns the model name for a given agent.
    Priority: Environment variable > default fallback
    """
    default_models = {
        "writer": "gpt-4o",
        "editor": "gpt-4o-mini",
        "seo": "gpt-4o-mini",
        "image": "dall-e-3",
        "code": "gpt-4o",
        "researcher": "gpt-4o-mini",
    }

    env_key = f"{agent_name.upper()}_MODEL"
    return os.getenv(env_key, default_models.get(agent_name, "gpt-4o"))
