"""Time window matching utilities."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd


def parse_datetime(series: pd.Series) -> pd.Series:
    """Parse a pandas Series to timezone-naive datetimes."""
    return pd.to_datetime(series, utc=True, errors="coerce").dt.tz_localize(None)


def within_window(
    left: pd.Timestamp,
    right: pd.Timestamp,
    minutes: int,
) -> bool:
    """Return True if two timestamps are within the given minute window."""
    if pd.isna(left) or pd.isna(right):
        return False
    delta = abs(left - right)
    return delta <= timedelta(minutes=minutes)
