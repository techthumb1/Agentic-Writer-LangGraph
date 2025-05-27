import yaml
import os
import random
from datetime import datetime

# Configuration
output_dir = "content_templates"
tones = ["educational", "conversational", "assertive", "friendly"]
audiences = ["AI beginners", "technical leaders", "data scientists", "ML researchers"]
platforms = ["medium", "substack"]

def generate_template(topic: str):
    filename_slug = topic.lower().replace(" ", "_").replace("-", "_")
    filename = f"{datetime.today().strftime('%Y-%m-%d')}_{filename_slug}.yaml"

    template = {
        "title": topic,
        "audience": random.choice(audiences),
        "tags": [],
        "tone": random.choice(tones),
        "platform": random.choice(platforms),
        "length": "long" if "medium" in filename else "short",
        "code": False  # You can toggle manually after generation
    }

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w") as f:
        yaml.dump(template, f)

    print(f"Template generated: {filepath}")
    print("Add 5 relevant tags and adjust fields if needed before running pipeline.")

if __name__ == "__main__":
    topic = input("Enter article topic/title: ").strip()
    generate_template(topic)
