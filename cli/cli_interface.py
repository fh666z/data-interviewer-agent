import argparse
from pathlib import Path

import pandas as pd

from agent.dataframe_agent import create_dataframe_agent, run_query
from utils.csv_loader import load_csv


def run_cli() -> None:
    parser = argparse.ArgumentParser(
        description="Query a CSV file using a LangChain + Gemini dataframe agent."
    )
    parser.add_argument("csv_path", type=str, help="Path to the CSV file.")
    parser.add_argument(
        "query",
        type=str,
        nargs="+",
        help="Natural language query about the data.",
    )

    args = parser.parse_args()
    csv_path = Path(args.csv_path)
    query_text = " ".join(args.query)

    df: pd.DataFrame = load_csv(csv_path)
    agent = create_dataframe_agent(df)
    result = run_query(agent, query_text)
    print(result.get("text", ""))


if __name__ == "__main__":
    run_cli()

