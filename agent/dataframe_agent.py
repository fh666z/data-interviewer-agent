import os
from typing import Any, Dict, List

import pandas as pd
from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler  # type: ignore[attr-defined]

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


class StepLoggingCallback(BaseCallbackHandler):
    """Collect intermediate agent steps for display in the UI."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: List[str] = []

    def on_agent_action(self, action, **kwargs) -> None:  # type: ignore[override]
        # `action.log` typically contains the thought + tool call description.
        try:
            log = getattr(action, "log", None) or str(action)
        except Exception:  # noqa: BLE001
            log = str(action)
        self.messages.append(f"Agent action: {log}")

    def on_tool_end(self, output: str, **kwargs) -> None:  # type: ignore[override]
        self.messages.append(f"Tool output: {output}")


def _get_gemini_model() -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Please configure it in your environment."
        )
    return ChatGoogleGenerativeAI(
        model="gemini-3-pro-preview",
        api_key=api_key,
        temperature=0.2,
    )


def create_dataframe_agent(df: pd.DataFrame):
    """Create a LangChain pandas dataframe agent backed by Gemini."""
    llm = _get_gemini_model()
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        handle_parsing_errors=True,
        allow_dangerous_code=True,
    )
    return agent


def run_query(agent, query: str) -> Dict[str, Any]:
    """Run a query through the agent and return structured result.

    Returns both the final text answer and a list of intermediate reasoning steps.
    """
    callback = StepLoggingCallback()
    # LangChain agents accept callbacks at call-time.
    response = agent.invoke(query, callbacks=[callback])
    return {
        "text": str(response),
        "steps": callback.messages,
    }

