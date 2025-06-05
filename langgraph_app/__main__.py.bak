# langgraph_app/__main__.py

import argparse
from langgraph_app.graph import graph
import os

def run_pipeline(template: str, style: str):
    initial_state = {
        "template_path": f"content_templates/{template}",
        "style_path": f"style_profiles/{style}",
    }

    final_state = graph.invoke(initial_state)

    slug = final_state["slug"]
    preview_path = f"generated_content/preview-{slug}.html"
    os.makedirs("generated_content", exist_ok=True)
    with open(preview_path, "w") as f:
        f.write(final_state["formatted_article"])

    print("Draft ready for review.")
    print(f"Cover Image: {final_state['cover_image_url']}")
    print(f"HTML Preview File: {preview_path}")
    print(f"SEO Output:\n{final_state['seo_output']}")
    print("\nTo publish, run:")
    print("python langgraph_app/publisher_trigger.py")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=str, default="federated_learning_101.yaml")
    parser.add_argument("--style", type=str, default="jason.yaml")
    args = parser.parse_args()
    run_pipeline(args.template, args.style)
