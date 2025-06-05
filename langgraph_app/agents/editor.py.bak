# langgraph_app/agents/editor.py

import os
from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _editor_fn(state: dict) -> dict:
    system_prompt = f"""
You are an expert technical editor. Your job is to revise AI-generated articles.
Make the writing clear, concise, and aligned with a(n) {state.get('tone', 'educational')} tone.
Keep the structure and meaning, but enhance grammar and flow.
    """

    user_prompt = f"Here is the draft:\n\n{state['draft']}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3, # Lower temperature for more focused edits
    )

    return {"edited_draft": response.choices[0].message.content}

editor: RunnableLambda = RunnableLambda(_editor_fn)
