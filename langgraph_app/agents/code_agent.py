# langgraph_app/agents/code_agent.py

import os
from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _code_block_fn(state: dict) -> dict:
    if not state.get("code", False):
        return {"code_block": ""}

    prompt = f"""
Topic: {state['topic']}
Audience: {state['audience']}
Task: Write a Python code block that supports or demonstrates the key idea behind the article topic.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You're a Python educator writing clean, readable examples."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    return {"code_block": response.choices[0].message.content.strip()}

code_agent: RunnableLambda = RunnableLambda(_code_block_fn)
