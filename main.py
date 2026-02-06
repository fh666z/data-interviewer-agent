import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from cli.cli_interface import run_cli
from ui.main_window import run_ui


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Data Interviewer Agent - CLI and UI for CSV data exploration."
    )
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch the Tkinter UI instead of running a one-off CLI query.",
    )
    parser.add_argument("csv_path", nargs="?", help="Path to CSV file for CLI mode.")
    parser.add_argument("query", nargs=argparse.REMAINDER, help="Query text for CLI.")

    args = parser.parse_args()

    if args.ui or args.csv_path is None or not args.query:
        run_ui()
    else:
        # Reconstruct CLI-style arguments for reuse
        from cli.cli_interface import run_cli as _run_cli  # type: ignore

        _run_cli()


if __name__ == "__main__":
    main()

