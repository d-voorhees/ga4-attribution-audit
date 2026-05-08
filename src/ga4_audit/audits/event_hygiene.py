"""Conversion event hygiene checks."""

from __future__ import annotations

from ga4_audit.audits import AuditResult
from ga4_audit.sources import AuditData


def run(data: AuditData) -> AuditResult:
    """Audit GA4 conversion event configuration and activity levels.

    Lists all conversion events with counts and percentages, flags suspiciously
    high counts, and flags events with zero recent activity.

    Args:
        data: Loaded audit datasets.

    Returns:
        AuditResult with event hygiene findings.
    """
    config = data.config
    findings: list[dict[str, object]] = []
    events = data.ga4_events.copy()
    conversions = data.ga4_conversions.copy()

    if events.empty and not conversions.empty:
        events = (
            conversions.groupby("conversion_event")
            .size()
            .reset_index(name="event_count")
            .rename(columns={"conversion_event": "event_name"})
        )

    if events.empty:
        return AuditResult(
            name="Conversion Event Hygiene",
            summary="No GA4 event data available for hygiene review.",
            findings=[],
            severity="info",
            methodology=(
                "Event counts are compared against configured conversion events. "
                "High counts and zero-activity events are flagged."
            ),
        )

    total = int(events["event_count"].astype(int).sum())
    threshold = config.suspicious_event_count_threshold
    configured = set(config.conversion_events)

    for _, row in events.iterrows():
        name = str(row["event_name"])
        count = int(row["event_count"])
        pct = round((count / total) * 100, 2) if total else 0.0
        is_configured = name in configured
        status = "OK"

        if count >= threshold:
            status = "Suspiciously high count"
            findings.append(
                {
                    "issue_type": "High event count",
                    "event_name": name,
                    "event_count": count,
                    "percent_of_total": pct,
                    "threshold": threshold,
                    "is_configured_conversion": is_configured,
                    "detail": (
                        f"Event count ({count}) exceeds threshold ({threshold}), "
                        "which may indicate a misconfigured trigger"
                    ),
                }
            )
        elif count == 0:
            status = "Zero activity"
            findings.append(
                {
                    "issue_type": "Zero recent activity",
                    "event_name": name,
                    "event_count": count,
                    "percent_of_total": pct,
                    "is_configured_conversion": is_configured,
                    "detail": "Event has zero fires in the audit period and may be deprecated",
                }
            )

        findings.append(
            {
                "issue_type": "Event inventory",
                "event_name": name,
                "event_count": count,
                "percent_of_total": pct,
                "is_configured_conversion": is_configured,
                "status": status,
            }
        )

    for event_name in configured:
        if event_name not in events["event_name"].astype(str).values:
            findings.append(
                {
                    "issue_type": "Configured event missing from data",
                    "event_name": event_name,
                    "event_count": 0,
                    "percent_of_total": 0.0,
                    "is_configured_conversion": True,
                    "detail": (
                        f"Event '{event_name}' is in config but has no rows in the export"
                    ),
                }
            )

    issue_count = sum(
        1
        for f in findings
        if f["issue_type"]
        in {
            "High event count",
            "Zero recent activity",
            "Configured event missing from data",
        }
    )

    if issue_count:
        summary = (
            f"Reviewed {len(events)} GA4 events and flagged {issue_count} hygiene issues. "
            "See inventory table for full event breakdown."
        )
        severity = "warning" if issue_count >= 2 else "info"
    else:
        summary = f"All {len(events)} GA4 conversion events appear within normal activity ranges."
        severity = "pass"

    return AuditResult(
        name="Conversion Event Hygiene",
        summary=summary,
        findings=findings,
        severity=severity,
        issue_count=issue_count,
        methodology=(
            "Event counts are totaled across the audit period. Events exceeding the "
            "configured threshold are flagged as potentially misconfigured. Configured "
            "conversion events with zero activity are flagged as likely deprecated."
        ),
    )
