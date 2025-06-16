# langgraph_app/agents/call_writer_agent.py

import sys
import json
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from langgraph_app.agents.writer import _writer_fn

def save_generated_content(output: dict, topic: str, week: str = "week_2") -> str:
    filename = f"{topic.strip().lower().replace(' ', '_')}.md"
    directory = os.path.join("../storage", week)
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, filename)
    with open(filepath, "w") as f:
        f.write(output["draft"])

    return filepath

if __name__ == "__main__":
    try:
        raw_input = sys.argv[1]
        state = json.loads(raw_input)
        print(">> Received input", file=sys.stderr)
        print(json.dumps(state), file=sys.stderr)

        print(">> Calling _writer_fn...", file=sys.stderr)
        result = _writer_fn(state)

        # Save file
        topic = result.get("metadata", {}).get("topic", "untitled")
        week = state.get("templateId", "week_1")  # fallback if needed
        saved_path = save_generated_content(result, topic, week)

        # Add file path to response
        result["saved_path"] = saved_path

        print(">> Function returned successfully", file=sys.stderr)
        print(json.dumps(result))

    except Exception as e:
        print(f"[WRITER_AGENT_ERROR] {str(e)}", file=sys.stderr)
        sys.exit(1)

