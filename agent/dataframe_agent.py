import os
from typing import Any, Dict, List

import matplotlib
import pandas as pd
from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler  # type: ignore[attr-defined]
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Use TkAgg backend which works with Tkinter and allows showing windows
# This must be set before importing pyplot
try:
    matplotlib.use("TkAgg")
except Exception:  # noqa: BLE001
    # Fallback to Agg if TkAgg is not available
    matplotlib.use("Agg")

load_dotenv()


class StepLoggingCallback(BaseCallbackHandler):
    """Collect intermediate agent steps for display in the UI."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: List[str] = []
        self.executed_code: List[str] = []  # Track code that was executed

    def on_agent_action(self, action, **kwargs) -> None:  # type: ignore[override]
        # `action.log` typically contains the thought + tool call description.
        try:
            log = getattr(action, "log", None) or str(action)
        except Exception:  # noqa: BLE001
            log = str(action)
        self.messages.append(f"Agent action: {log}")
        
        # Extract code from tool input if it's a python_repl action
        try:
            # Try different ways to get the tool input
            tool_input = getattr(action, "tool_input", None)
            if not tool_input:
                # Try tool_input_str
                tool_input = getattr(action, "tool_input_str", None)
            if not tool_input:
                # Try to extract from the action string representation
                action_str = str(action)
                if "Action Input:" in action_str:
                    parts = action_str.split("Action Input:", 1)
                    if len(parts) > 1:
                        tool_input = parts[1].strip()
            
            if tool_input and isinstance(tool_input, str):
                self.executed_code.append(tool_input)
        except Exception:  # noqa: BLE001
            pass

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
        "executed_code": callback.executed_code,  # Include executed code for plot detection
    }

