import os
import yaml
from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from langgraph_app.model_registry import get_model

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_system_prompt(prompt_name: str) -> str:
    prompt_path = os.path.join("prompts", "writer", prompt_name)
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful, high-level technical writing assistant."

def load_style_profile(name: str) -> dict:
    """Load style profile from data/style_profiles/"""
    try:
        with open(f"data/style_profiles/{name}.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Style profile not found: {name}.yaml, using default")
        return {
            "structure": "hook → explanation → example → summary",
            "voice": "experienced and conversational", 
            "tone": "educational",
            "system_prompt": "grad_level_writer.txt"
        }

def load_content_template(name: str) -> dict:
    """Load content template from data/content_templates/"""
    try:
        with open(f"data/content_templates/{name}.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Template not found: {name}.yaml")
        return {}


def _writer_fn(state: dict) -> dict:
    # Check if we should use mock mode
    use_mock = state.get("use_mock", False)
    if use_mock:
        topic = state.get("topic", "Untitled Topic")
        return {
            "draft": f"# This is a placeholder article for {topic}\n\nContent will be generated here.",
            "metadata": {
                "topic": topic
            }
        }

    # Real content generation
    platform = state.get("platform", "substack")
    tone = state.get("tone", "educational")
    
    # Load style profile - handle both string name and dict
    style_profile_input = state.get("style_profile", "jason")
    if isinstance(style_profile_input, str):
        style = load_style_profile(style_profile_input)
    else:
        style = style_profile_input

    research = state.get("research", "")

    # Parameters from template or direct input
    params = state.get("dynamic_parameters", {})
    topic = params.get("topic") or state.get("topic", "Untitled")
    audience = params.get("audience") or state.get("audience", "General audience")
    tags = params.get("tags") or state.get("tags", [])

    # Article length based on platform
    if platform == "medium":
        length_instruction = "Write a long-form technical article between 1600 and 2200 words, suitable for an 8–12 minute read."
    else:
        length_instruction = "Write a short, digestible blog post under 600 words."

    # Style profile extraction
    structure = style.get("structure", "hook → explanation → example → summary")
    voice = style.get("voice", "experienced and conversational")
    style_tone = style.get("tone", tone)
    system_prompt_file = style.get("system_prompt", "grad_level_writer.txt")
    system_prompt = load_system_prompt(system_prompt_file)

    # Final prompt
    prompt = f"""
{length_instruction}
Use a {style_tone} tone and a {voice} voice.
Structure the article using this flow: {structure}.

Title: {topic}
Audience: {audience}
Tags: {', '.join(tags)}

You may incorporate relevant research:
{research}
    """

    # Load model + call OpenAI
    model = get_model("writer")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
    )

    return {
        "draft": response.choices[0].message.content.strip(),
        "metadata": {
            "topic": topic,
            "audience": audience,
            "tags": tags,
            "platform": platform,
            "style_tone": style_tone,
            "voice": voice,
            "structure": structure
        }
    }


writer: RunnableLambda = RunnableLambda(_writer_fn)