"""Tests for channel discrepancy detection."""

from __future__ import annotations

import pandas as pd

from ga4_audit.audits.channel_discrepancy import run
from ga4_audit.config import AuditConfig
from ga4_audit.sources import AuditData


def _make_config() -> AuditConfig:
    return AuditConfig(
        property_id="123",
        date_range={"start": "2026-05-01", "end": "2026-05-30"},
        conversion_events=["purchase"],
        channel_groupings=["sessionDefaultChannelGroup"],
    )


def test_flags_channel_mismatch() -> None:
    """Google Ads conversion attributed to non-paid GA4 channel is flagged."""
    config = _make_config()
    data = AuditData(
        ga4_sessions=pd.DataFrame(
            [
                {
                    "session_id": "S1",
                    "session_campaign": "HG | Search | Spring Sale",
                    "default_channel_group": "Direct",
                    "gclid": "abc123",
                }
            ]
        ),
        ga4_conversions=pd.DataFrame(
            [{"session_id": "S1", "conversion_event": "purchase", "gclid": "abc123"}]
        ),
        ga4_events=pd.DataFrame(),
        callrail=pd.DataFrame(),
        google_ads=pd.DataFrame(
            [
                {
                    "campaign_name": "HG | Search | Spring Sale",
                    "conversion_action": "Purchase",
                    "conversion_date": "2026-05-08",
                    "gclid": "abc123",
                }
            ]
        ),
        config=config,
        source_modes={},
    )
    result = run(data)
    mismatches = [f for f in result.findings if f["issue_type"] == "Channel mismatch"]
    assert len(mismatches) == 1
    assert mismatches[0]["ga4_channel"] == "Direct"
