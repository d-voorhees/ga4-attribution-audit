"""Duplicate conversion detection between GA4 and CallRail."""

from __future__ import annotations

import pandas as pd

from ga4_audit.audits import AuditResult
from ga4_audit.sources import AuditData
from ga4_audit.utils.timewindow import within_window


def run(data: AuditData) -> AuditResult:
    """Detect likely duplicate conversions and CallRail tracking gaps.

    Cross-references GA4 conversion events against CallRail calls within a
    configurable time window. Flags GA4 conversions that likely double-count
    phone calls already attributed in CallRail, and CallRail calls with no
    corresponding GA4 session.

    Args:
        data: Loaded audit datasets.

    Returns:
        AuditResult with duplicate and gap findings.
    """
    config = data.config
    window = config.duplicate_window_minutes
    findings: list[dict[str, object]] = []

    conversions = data.ga4_conversions.copy()
    callrail = data.callrail.copy()
    sessions = data.ga4_sessions.copy()

    if "event_timestamp" not in conversions.columns and "date" in conversions.columns:
        conversions["event_timestamp"] = conversions["date"]
    if "session_start" not in sessions.columns and "date" in sessions.columns:
        sessions["session_start"] = sessions["date"]

    for _, conv in conversions.iterrows():
        conv_time = conv.get("event_timestamp") or conv.get("date")
        if pd.isna(conv_time):
            continue
        for _, call in callrail.iterrows():
            call_time = call.get("call_start")
            if within_window(pd.Timestamp(conv_time), pd.Timestamp(call_time), window):
                findings.append(
                    {
                        "issue_type": "Likely duplicate conversion",
                        "ga4_session_id": conv.get("session_id", ""),
                        "ga4_event": conv.get("conversion_event", ""),
                        "ga4_timestamp": str(conv_time),
                        "callrail_id": call.get("call_id", ""),
                        "callrail_timestamp": str(call_time),
                        "window_minutes": window,
                        "detail": (
                            "GA4 conversion occurred within "
                            f"{window} minutes of a CallRail call"
                        ),
                    }
                )
                break

    for _, call in callrail.iterrows():
        gclid = str(call.get("gclid", "") or "")
        landing = str(call.get("landing_page", "") or "")
        matched_session = False

        if gclid:
            gclid_sessions = sessions[
                sessions.get("gclid", pd.Series(dtype=str)).astype(str) == gclid
            ]
            if not gclid_sessions.empty:
                matched_session = True

        if not matched_session and landing:
            landing_sessions = sessions[
                sessions["landing_page"]
                .astype(str)
                .str.contains(landing.split("?")[0][-40:], na=False, regex=False)
            ]
            if not landing_sessions.empty:
                matched_session = True

        call_time = call.get("call_start")
        if not matched_session and not pd.isna(call_time):
            nearby = sessions.copy()
            if "session_start" in nearby.columns:
                nearby["time_delta"] = (
                    pd.to_datetime(nearby["session_start"]) - pd.Timestamp(call_time)
                ).abs()
                if (nearby["time_delta"] <= pd.Timedelta(minutes=window * 2)).any():
                    matched_session = True

        if not matched_session:
            findings.append(
                {
                    "issue_type": "CallRail call without GA4 session",
                    "callrail_id": call.get("call_id", ""),
                    "callrail_timestamp": str(call.get("call_start", "")),
                    "caller_number": call.get("caller_number", ""),
                    "tracking_number": call.get("tracking_number", ""),
                    "landing_page": call.get("landing_page", ""),
                    "detail": "No matching GA4 session found for this call",
                }
            )

    duplicate_count = sum(
        1 for f in findings if f["issue_type"] == "Likely duplicate conversion"
    )
    gap_count = sum(
        1 for f in findings if f["issue_type"] == "CallRail call without GA4 session"
    )

    if duplicate_count or gap_count:
        severity = "critical" if duplicate_count >= 3 or gap_count >= 2 else "warning"
        summary = (
            f"Found {duplicate_count} likely duplicate conversions and "
            f"{gap_count} CallRail calls with no matching GA4 session. "
            "These patterns usually indicate double-counting or call tracking gaps."
        )
    else:
        severity = "pass"
        summary = (
            "No duplicate conversions or CallRail session gaps detected "
            f"within the {window}-minute matching window."
        )

    return AuditResult(
        name="Duplicate Conversion Detection",
        summary=summary,
        findings=findings,
        severity=severity,
        issue_count=len(findings),
        methodology=(
            f"GA4 conversion events are matched to CallRail calls within "
            f"{window} minutes by timestamp. Calls are checked for a corresponding "
            "GA4 session by gclid, landing page, or nearby session start time."
        ),
    )
