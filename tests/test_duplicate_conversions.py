"""Tests for duplicate conversion detection."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ga4_audit.audits.duplicate_conversions import run
from ga4_audit.config import AuditConfig
from ga4_audit.sources import AuditData

FIXTURES = Path(__file__).parent / "fixtures"


def _make_config() -> AuditConfig:
    return AuditConfig(
        property_id="123",
        date_range={"start": "2026-05-01", "end": "2026-05-30"},
        conversion_events=["phone_call_conversion", "purchase"],
        channel_groupings=["sessionDefaultChannelGroup"],
        duplicate_window_minutes=5,
    )


def test_detects_duplicate_within_window() -> None:
    """GA4 conversion within 5 minutes of CallRail call is flagged."""
    config = _make_config()
    data = AuditData(
        ga4_sessions=pd.DataFrame(
            [
                {
                    "session_id": "S1",
                    "session_start": "2026-05-08 14:30:00",
                    "landing_page": "",
                    "gclid": "",
                }
            ]
        ),
        ga4_conversions=pd.DataFrame(
            [
                {
                    "session_id": "S1",
                    "conversion_event": "phone_call_conversion",
                    "event_timestamp": "2026-05-08 14:32:00",
                }
            ]
        ),
        ga4_events=pd.DataFrame(),
        callrail=pd.DataFrame(
            [
                {
                    "call_id": "CR-1",
                    "call_start": "2026-05-08 14:32:00",
                    "landing_page": "",
                }
            ]
        ),
        google_ads=pd.DataFrame(),
        config=config,
        source_modes={},
    )
    result = run(data)
    duplicates = [
        f for f in result.findings if f["issue_type"] == "Likely duplicate conversion"
    ]
    assert len(duplicates) >= 1


def test_detects_callrail_without_session() -> None:
    """CallRail call with no matching GA4 session is flagged."""
    config = _make_config()
    data = AuditData(
        ga4_sessions=pd.DataFrame(
            [
                {
                    "session_id": "S1",
                    "session_start": "2026-05-01 10:00:00",
                    "landing_page": "/other",
                    "gclid": "",
                }
            ]
        ),
        ga4_conversions=pd.DataFrame(),
        ga4_events=pd.DataFrame(),
        callrail=pd.DataFrame(
            [
                {
                    "call_id": "CR-99",
                    "call_start": "2026-05-28 08:40:00",
                    "landing_page": "https://example.com/unknown-page",
                    "gclid": "",
                }
            ]
        ),
        google_ads=pd.DataFrame(),
        config=config,
        source_modes={},
    )
    result = run(data)
    gaps = [
        f
        for f in result.findings
        if f["issue_type"] == "CallRail call without GA4 session"
    ]
    assert len(gaps) == 1
