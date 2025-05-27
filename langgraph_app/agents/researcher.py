# langgraph_app/agents/researcher.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _researcher_fn(state: dict) -> dict:
    prompt = f"""
Topic: {state['topic']}
Audience: {state['audience']}
Goal: Provide key facts, relevant citations (news, academic), and 2-3 reputable links for use in an educational article. Avoid fake or low-quality sources.
Tags: {', '.join(state['tags'])}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You're a technical researcher gathering facts for a blog post."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
    )

    return {"research": response.choices[0].message.content}

researcher: RunnableLambda = RunnableLambda(_researcher_fn)
