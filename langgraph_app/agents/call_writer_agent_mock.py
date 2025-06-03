import sys
import json
import os
import time
from datetime import datetime, timezone
import markdown  # ✅ Required for HTML conversion

def generate_mock_article(state: dict) -> dict:
    topic = state.get("topic", "Artificial Intelligence")
    platform = state.get("platform", "Substack")
    style = state.get("style_profile", {}).get("name", "default")

    time.sleep(2)  # Simulate thinking...

    draft = (
        f"# {topic}\n\n"
        f"This is a mock article generated for the topic **{topic}** using the **{style}** style profile.\n\n"
        "This content is purely for testing purposes and simulates what a real AI-written article would look like."
    )

    content_html = markdown.markdown(draft)

    return {
        "title": f"[MOCK] {topic} - A {platform.capitalize()} Article",
        "draft": draft,
        "contentHtml": content_html,  # ✅ Add this line
        "metadata": {
            "topic": topic,
            "platform": platform,
            "style": style,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    }

def save_generated_content(output: dict, topic: str, week: str = "week_mock") -> str:
    filename = f"{topic.strip().lower().replace(' ', '_')}_mock.md"
    directory = os.path.join("generated_content", week)
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, filename)
    with open(filepath, "w") as f:
        f.write(output["draft"])

    return filepath

if __name__ == "__main__":
    try:
        raw_input = sys.argv[1]
        state = json.loads(raw_input)

        print(">> [MOCK] Received input", file=sys.stderr)
        print(json.dumps(state), file=sys.stderr)

        result = generate_mock_article(state)
        topic = result.get("metadata", {}).get("topic", "untitled")
        week = state.get("templateId", "week_mock")
        saved_path = save_generated_content(result, topic, week)

        result["saved_path"] = saved_path
        # Save JSON version of the generated content
        json_path = os.path.join("generated_content", week, f"{topic.strip().lower().replace(' ', '_')}_mock.json")
        with open(json_path, "w") as f:
            json.dump({
                "title": result["title"],
                "contentHtml": result["contentHtml"],
                "metadata": result["metadata"]
            }, f, indent=2)
        
        # Optionally log it
        print(f"[MOCK] JSON saved to: {json_path}", file=sys.stderr)

        print(">> [MOCK] Function returned successfully", file=sys.stderr)
        print(json.dumps(result))

    except Exception as e:
        print(f"[MOCK_WRITER_AGENT_ERROR] {str(e)}", file=sys.stderr)
        sys.exit(1)

