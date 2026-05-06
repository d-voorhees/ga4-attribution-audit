"""Load CallRail call export CSV data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ga4_audit.utils.timewindow import parse_datetime


def load_callrail_csv(path: str | Path) -> pd.DataFrame:
    """Load a standard CallRail Calls export CSV.

    Args:
        path: Path to the CallRail CSV export.

    Returns:
        Normalized DataFrame with call records.
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    column_map = {
        "start_time": "call_start",
        "call_start_time": "call_start",
        "duration_(seconds)": "duration_seconds",
        "duration": "duration_seconds",
        "tracking_phone_number": "tracking_number",
        "landing_page_url": "landing_page",
        "gclid": "gclid",
        "utm_source": "utm_source",
        "utm_medium": "utm_medium",
        "utm_campaign": "utm_campaign",
    }
    df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

    if "call_start" in df.columns:
        df["call_start"] = parse_datetime(df["call_start"])

    for col in ("caller_number", "tracking_number", "source", "medium", "campaign"):
        if col not in df.columns:
            df[col] = ""

    if "call_id" not in df.columns:
        df["call_id"] = df.index.astype(str).radd("CR-")

    return df
