# langgraph_app/agents/image_agent.py

import os
from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _image_agent_fn(state: dict) -> dict:
    prompt = f"Minimalist illustration for an article titled '{state['topic']}', keywords: {', '.join(state['tags'])}"
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    return {"cover_image_url": image_url}

image_agent: RunnableLambda = RunnableLambda(_image_agent_fn)
