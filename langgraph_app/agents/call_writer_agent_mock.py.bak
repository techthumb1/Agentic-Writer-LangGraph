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
        "contentHtml": content_html,
        "metadata": {
            "topic": topic,
            "platform": platform,
            "style": style,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    }

def save_generated_content(output: dict, topic: str, week: str = "week_mock") -> str:
    slug = topic.strip().lower().replace(' ', '_')
    directory = os.path.join("../storage", week)
    os.makedirs(directory, exist_ok=True)

    # Save markdown file
    md_path = os.path.join(directory, f"{slug}_mock.md")
    with open(md_path, "w") as f:
        f.write(output["draft"])

    # Save JSON file
    json_path = os.path.join(directory, f"{slug}_mock.json")
    with open(json_path, "w") as f:
        json.dump({
            "title": output["title"],
            "contentHtml": output["contentHtml"],
            "metadata": output["metadata"]
        }, f, indent=2)

    print(f"[MOCK] JSON saved to: {json_path}", file=sys.stderr)

    return md_path

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

        print(">> [MOCK] Function returned successfully", file=sys.stderr)
        print(json.dumps(result))

    except Exception as e:
        print(f"[MOCK_WRITER_AGENT_ERROR] {str(e)}", file=sys.stderr)
        sys.exit(1)
