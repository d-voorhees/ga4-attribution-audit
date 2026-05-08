"""Attribution gap detection in GA4 session data."""

from __future__ import annotations

import pandas as pd

from ga4_audit.audits import AuditResult
from ga4_audit.sources import AuditData


def run(data: AuditData) -> AuditResult:
    """Identify attribution gaps in GA4 conversion and session data.

    Finds sessions with conversions but no recorded source/medium, high-value
    landing pages without UTM coverage, and conversions outside the configured
    attribution window.

    Args:
        data: Loaded audit datasets.

    Returns:
        AuditResult with attribution gap findings.
    """
    config = data.config
    findings: list[dict[str, object]] = []

    sessions = data.ga4_sessions.copy()
    conversions = data.ga4_conversions.copy()

    direct_values = {"", "(direct)", "direct", "(none)", "none", "(not set)"}

    conv_session_ids = set(conversions["session_id"].astype(str))
    conv_sessions = sessions[sessions["session_id"].astype(str).isin(conv_session_ids)]

    for _, row in conv_sessions.iterrows():
        source = str(row.get("session_source", "") or "").strip().lower()
        medium = str(row.get("session_medium", "") or "").strip().lower()
        if source in direct_values and medium in direct_values:
            findings.append(
                {
                    "issue_type": "Conversion with direct/none attribution",
                    "session_id": row.get("session_id", ""),
                    "landing_page": row.get("landing_page", ""),
                    "session_source": row.get("session_source", ""),
                    "session_medium": row.get("session_medium", ""),
                    "default_channel_group": row.get("default_channel_group", ""),
                    "detail": (
                        "Session has a conversion but source/medium appear as direct "
                        "or none, which often indicates a tagging gap"
                    ),
                }
            )

    landing_counts = (
        sessions.groupby("landing_page").size().reset_index(name="session_count")
    )
    threshold = config.high_value_landing_page_threshold
    high_traffic = landing_counts[landing_counts["session_count"] >= threshold]

    for _, row in high_traffic.iterrows():
        landing = str(row["landing_page"])
        landing_sessions = sessions[sessions["landing_page"] == landing]
        utm_cols = ["utm_source", "utm_medium", "utm_campaign"]
        has_utm = any(
            col in landing_sessions.columns
            and landing_sessions[col].notna().any()
            and (landing_sessions[col].astype(str).str.strip() != "").any()
            for col in utm_cols
        )
        has_query_utm = (
            landing_sessions["landing_page"]
            .astype(str)
            .str.contains("utm_", na=False)
            .any()
        )

        if not has_utm and not has_query_utm:
            findings.append(
                {
                    "issue_type": "High-traffic landing page without UTM coverage",
                    "landing_page": landing,
                    "session_count": int(row["session_count"]),
                    "threshold": threshold,
                    "detail": (
                        f"Landing page exceeds {threshold} sessions but shows no "
                        "UTM parameters in session data"
                    ),
                }
            )

    if "event_timestamp" in conversions.columns and "session_start" in sessions.columns:
        session_starts = sessions.set_index("session_id")["session_start"].to_dict()
        window_days = config.attribution_window_days
        for _, conv in conversions.iterrows():
            sid = conv.get("session_id")
            conv_time = conv.get("event_timestamp")
            session_start = session_starts.get(sid)
            if pd.isna(conv_time) or pd.isna(session_start):
                continue
            delta = pd.Timestamp(conv_time) - pd.Timestamp(session_start)
            if delta.days > window_days:
                findings.append(
                    {
                        "issue_type": "Conversion outside attribution window",
                        "session_id": sid,
                        "conversion_event": conv.get("conversion_event", ""),
                        "session_start": str(session_start),
                        "conversion_time": str(conv_time),
                        "days_after_session": delta.days,
                        "window_days": window_days,
                        "detail": (
                            f"Conversion occurred {delta.days} days after session start, "
                            f"exceeding the {window_days}-day window"
                        ),
                    }
                )

    issue_count = len(findings)
    if issue_count:
        summary = (
            f"Found {issue_count} attribution gaps including direct/none conversions, "
            "landing pages without UTM coverage, and out-of-window conversions."
        )
        severity = "warning" if issue_count >= 3 else "info"
    else:
        summary = "No significant attribution gaps detected in the session data."
        severity = "pass"

    return AuditResult(
        name="Attribution Gap Detection",
        summary=summary,
        findings=findings,
        severity=severity,
        issue_count=issue_count,
        methodology=(
            "Sessions with conversions are checked for direct/none source-medium pairs. "
            "Landing pages above the session threshold are checked for UTM parameters. "
            "Conversions are compared against session start dates using the configured "
            "attribution window."
        ),
    )
