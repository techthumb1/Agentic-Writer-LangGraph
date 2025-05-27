# langgraph_app/publisher_trigger.py

from langgraph_app.agents.publisher import publisher
import yaml

# Load previously stored values
with open("content_templates/federated_learning_101.yaml", "r") as f:
    yaml_data = yaml.safe_load(f)

# Load saved formatted article
slug = yaml_data['title'].lower().replace(" ", "-")
with open(f"generated_content/preview-{slug}.html", "r") as f:
    html = f.read()

state = {
    "topic": yaml_data["title"],
    "slug": slug,
    "tags": yaml_data["tags"],
    "formatted_article": html
}

result = publisher.invoke(state)

print("✅ Article published:")
print(f"Substack Status: {result['substack_status']}")
print(f"Medium Import Path: {result['medium_import_path']}")
print(f"Import URL: {result['import_url']}")
