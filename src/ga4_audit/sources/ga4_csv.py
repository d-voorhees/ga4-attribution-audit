"""Load GA4 data from CSV exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ga4_audit.config import AuditConfig
from ga4_audit.utils.timewindow import parse_datetime


def load_ga4_csv(
    path: str | Path,
    config: AuditConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load GA4 session, conversion, and event data from a unified CSV export.

    The CSV is expected to contain session-level rows with optional conversion
    event columns. Rows with conversion_event populated are extracted into a
    separate conversions frame.

    Args:
        path: Path to the GA4 CSV file.
        config: Audit configuration for event filtering.

    Returns:
        Tuple of (sessions, conversions, events) DataFrames.
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    if "date" in df.columns:
        df["date"] = parse_datetime(df["date"])
    if "session_start" in df.columns:
        df["session_start"] = parse_datetime(df["session_start"])
    if "event_timestamp" in df.columns:
        df["event_timestamp"] = parse_datetime(df["event_timestamp"])

    for col in ("session_source", "session_medium", "session_campaign", "landing_page"):
        if col not in df.columns:
            df[col] = ""

    sessions = df.drop_duplicates(subset=["session_id"]).copy()

    conversion_mask = df["conversion_event"].notna() & (df["conversion_event"] != "")
    conversions = df[conversion_mask].copy()
    if not conversions.empty:
        conversions = conversions[
            conversions["conversion_event"].isin(config.conversion_events)
        ]

    events = (
        df.groupby("event_name", dropna=False)
        .size()
        .reset_index(name="event_count")
        .sort_values("event_count", ascending=False)
    )

    return sessions, conversions, events
