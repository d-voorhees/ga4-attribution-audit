"""Tests for UTM consistency checks."""

from __future__ import annotations

import pandas as pd

from ga4_audit.audits.utm_consistency import run
from ga4_audit.config import AuditConfig
from ga4_audit.sources import AuditData


def _make_config() -> AuditConfig:
    return AuditConfig(
        property_id="123",
        date_range={"start": "2026-05-01", "end": "2026-05-30"},
        conversion_events=["purchase"],
        channel_groupings=["sessionDefaultChannelGroup"],
    )


def test_detects_casing_inconsistency() -> None:
    """Multiple casing variants of the same source are flagged."""
    config = _make_config()
    data = AuditData(
        ga4_sessions=pd.DataFrame(
            {
                "session_source": ["Facebook", "facebook", "FaceBook", "google"],
                "session_medium": ["cpc", "cpc", "cpc", "cpc"],
                "session_campaign": ["a", "b", "c", "d"],
            }
        ),
        ga4_conversions=pd.DataFrame(),
        ga4_events=pd.DataFrame(),
        callrail=pd.DataFrame(),
        google_ads=pd.DataFrame(),
        config=config,
        source_modes={},
    )
    result = run(data)
    casing = [
        f for f in result.findings if f["issue_type"] == "UTM casing inconsistency"
    ]
    assert len(casing) >= 1


def test_detects_non_standard_medium() -> None:
    """Non-standard medium values are flagged."""
    config = _make_config()
    data = AuditData(
        ga4_sessions=pd.DataFrame(
            {
                "session_source": ["partner"],
                "session_medium": ["print"],
                "session_campaign": ["flyer"],
            }
        ),
        ga4_conversions=pd.DataFrame(),
        ga4_events=pd.DataFrame(),
        callrail=pd.DataFrame(),
        google_ads=pd.DataFrame(),
        config=config,
        source_modes={},
    )
    result = run(data)
    medium_issues = [
        f for f in result.findings if f["issue_type"] == "Non-standard medium value"
    ]
    assert len(medium_issues) == 1
