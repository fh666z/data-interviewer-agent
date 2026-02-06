import os
from typing import Any, Dict, Optional

import pandas as pd
from dotenv import load_dotenv
from langchain.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


def _get_gemini_model() -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Please configure it in your environment."
        )
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-preview-0409",
        api_key=api_key,
        temperature=0.2,
    )


def create_dataframe_agent(df: pd.DataFrame):
    """Create a LangChain pandas dataframe agent backed by Gemini."""
    llm = _get_gemini_model()
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=False,
        handle_parsing_errors=True,
    )
    return agent


def run_query(agent, query: str) -> Dict[str, Any]:
    """Run a query through the agent and return structured result."""
    # For now we just return the raw text; hooks for chart instructions can be added later.
    response = agent.run(query)
    return {"text": str(response)}

