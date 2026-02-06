from pathlib import Path

import pandas as pd


def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame with basic validation."""
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Failed to read CSV file: {exc}") from exc
    if df.empty:
        raise ValueError("Loaded CSV is empty.")
    return df

