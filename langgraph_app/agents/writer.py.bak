import os
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
    
def _writer_fn(state: dict) -> dict:
    topic = state.get("topic", "Untitled Topic")
    return {
        "draft": f"# This is a placeholder article for {topic}\n\nContent will be generated here.",
        "metadata": {
            "topic": topic
        }
    }



#def _writer_fn(state: dict) -> dict:
#    # General input
#    platform = state.get("platform", "substack")
#    tone = state.get("tone", "educational")
#    style = state.get("style_profile", {})
#    research = state.get("research", "")
#
#    # Parameters passed by the template form
#    params = state.get("dynamic_parameters", {})
#    topic = params.get("topic", "Untitled")
#    audience = params.get("audience", "General audience")
#    tags = params.get("tags", [])
#
#    # Article length based on platform
#    if platform == "medium":
#        length_instruction = "Write a long-form technical article between 1600 and 2200 words, suitable for an 8–12 minute read."
#    else:
#        length_instruction = "Write a short, digestible blog post under 600 words."
#
#    # Style profile extraction
#    structure = style.get("structure", "hook → explanation → example → summary")
#    voice = style.get("voice", "experienced and conversational")
#    style_tone = style.get("tone", tone)
#    system_prompt_file = style.get("system_prompt", "grad_level_writer.txt")
#    system_prompt = load_system_prompt(system_prompt_file)
#
#    # Final prompt
#    prompt = f"""
#{length_instruction}
#Use a {style_tone} tone and a {voice} voice.
#Structure the article using this flow: {structure}.
#
#Title: {topic}
#Audience: {audience}
#Tags: {', '.join(tags)}
#
#You may incorporate relevant research:
#{research}
#    """
#
#    # Load model + call OpenAI
#    model = get_model("writer")
#    response = client.chat.completions.create(
#        model=model,
#        messages=[
#            {"role": "system", "content": system_prompt},
#            {"role": "user", "content": prompt}
#        ],
#        temperature=0.5,
#    )
#
#    return {
#        "draft": response.choices[0].message.content.strip(),
#        "metadata": {
#            "topic": topic,
#            "audience": audience,
#            "tags": tags,
#            "platform": platform,
#            "style_tone": style_tone,
#            "voice": voice,
#            "structure": structure
#        }
#    }


writer: RunnableLambda = RunnableLambda(_writer_fn)
