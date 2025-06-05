# langgraph_app/agents/seo_agent.py

import re
import os
from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def slugify(title: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

def _seo_fn(state: dict) -> dict:
    title = state["topic"]
    audience = state.get("audience", "")
    tags = state.get("tags", [])
    tone = state.get("tone", "educational")

    base_slug = slugify(title)

    prompt = f"""
You are an SEO assistant helping to optimize blog metadata.

Title: {title}
Audience: {audience}
Tags: {', '.join(tags)}
Tone: {tone}

Return:
1. A meta title under 60 characters.
2. A meta description under 155 characters.
3. 5 SEO-relevant keywords.
4. A catchy open graph image tagline (OG text).
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You're an SEO copywriter optimizing metadata for maximum visibility."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
    )

    output = response.choices[0].message.content

    return {
        "slug": base_slug,
        "seo_output": output
    }

seo_agent: RunnableLambda = RunnableLambda(_seo_fn)
