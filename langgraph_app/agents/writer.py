# langgraph_app/agents/writer.py

import os
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")

def _writer_fn(state: dict) -> dict:
    prompt = f"""
Write a short article for {state['audience']} titled "{state['topic']}".
Use an educational tone. Include a short intro and one or two paragraphs.
Mention these keywords: {", ".join(state['tags'])}
    """
    result = llm.invoke(prompt)
    return {"draft": result.content}

writer: RunnableLambda = RunnableLambda(_writer_fn)
