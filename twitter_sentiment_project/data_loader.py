from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import resolve_default_input_file

DATA_FILE = str(resolve_default_input_file())
REQUIRED_COLUMNS = {"created_at", "text"}


def load_data(file_path: str | Path | None = None) -> pd.DataFrame:
    path = Path(file_path) if file_path else resolve_default_input_file()
    if not path.exists():
        raise FileNotFoundError(f"Cannot find data file: {path}")

    df = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Data file is missing required columns: {missing}")

    prepared = df.copy()
    prepared["text"] = prepared["text"].astype(str)
    prepared["created_at"] = pd.to_datetime(prepared["created_at"], errors="coerce", utc=True)
    prepared = prepared.dropna(subset=["created_at", "text"]).copy()
    prepared["created_at"] = prepared["created_at"].dt.tz_convert("UTC").dt.tz_localize(None)

    dedupe_subset = ["tweet_id"] if "tweet_id" in prepared.columns else ["created_at", "text"]
    prepared = prepared.drop_duplicates(subset=dedupe_subset).sort_values("created_at").reset_index(drop=True)
    return prepared


def summarize_dataset(df: pd.DataFrame) -> dict[str, str | int]:
    start_time = df["created_at"].min()
    end_time = df["created_at"].max()
    return {
        "total_rows": int(len(df)),
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(start_time) else "N/A",
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(end_time) else "N/A",
    }
