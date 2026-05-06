"""Load Google Ads data from CSV exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ga4_audit.utils.timewindow import parse_datetime


def load_ads_csv(path: str | Path) -> pd.DataFrame:
    """Load a Google Ads conversion export CSV.

    Args:
        path: Path to the Google Ads CSV export.

    Returns:
        Normalized DataFrame with conversion records.
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    column_map = {
        "campaign": "campaign_name",
        "conversion_action": "conversion_action",
        "conversion_date": "conversion_date",
        "conversion_time": "conversion_time",
        "all_conversions": "conversions",
        "conv._value": "conversion_value",
    }
    df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

    if "conversion_date" in df.columns:
        df["conversion_date"] = parse_datetime(df["conversion_date"])
    if "conversion_time" in df.columns:
        df["conversion_time"] = parse_datetime(df["conversion_time"])
    elif "conversion_date" in df.columns:
        df["conversion_time"] = df["conversion_date"]

    for col in ("campaign_name", "conversion_action", "gclid"):
        if col not in df.columns:
            df[col] = ""

    return df
