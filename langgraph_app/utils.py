def load_system_prompt(name: str) -> str:
    try:
        with open(f"prompts/writer/{name}", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful technical writing assistant."
