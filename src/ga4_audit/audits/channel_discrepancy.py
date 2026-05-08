"""Channel discrepancy analysis between GA4 and Google Ads."""

from __future__ import annotations

from ga4_audit.audits import AuditResult
from ga4_audit.sources import AuditData


def run(data: AuditData) -> AuditResult:
    """Compare GA4 default channel grouping against Google Ads campaign attribution.

    Flags cases where Google Ads reports a conversion that GA4 attributes to a
    different channel, and surfaces the most common discrepancy patterns.

    Args:
        data: Loaded audit datasets.

    Returns:
        AuditResult with channel mismatch findings.
    """
    findings: list[dict[str, object]] = []
    pattern_counts: dict[str, int] = {}

    ads = data.google_ads.copy()
    conversions = data.ga4_conversions.copy()
    sessions = data.ga4_sessions.copy()

    if ads.empty or conversions.empty:
        return AuditResult(
            name="Channel Discrepancy Report",
            summary="Insufficient Google Ads or GA4 conversion data to compare channels.",
            findings=[],
            severity="info",
            methodology=(
                "Google Ads conversions are matched to GA4 sessions by gclid or "
                "campaign name, then default channel grouping is compared."
            ),
        )

    session_lookup = sessions.set_index("session_id").to_dict("index")

    paid_channels = {"paid search", "paid social", "display", "cross-network"}

    for _, ad_row in ads.iterrows():
        gclid = str(ad_row.get("gclid", "") or "")
        campaign = str(ad_row.get("campaign_name", "") or "")
        matched_channel = None
        matched_session = ""

        conv_matches = conversions.copy()
        if gclid and "gclid" in conv_matches.columns:
            gclid_matches = conv_matches[conv_matches["gclid"].astype(str) == gclid]
            if not gclid_matches.empty:
                sid = str(gclid_matches.iloc[0].get("session_id", ""))
                matched_session = sid
                if sid in session_lookup:
                    matched_channel = session_lookup[sid].get(
                        "default_channel_group", ""
                    )

        if matched_channel is None and campaign:
            campaign_sessions = sessions[
                sessions["session_campaign"]
                .astype(str)
                .str.contains(campaign[:30], case=False, na=False, regex=False)
            ]
            if not campaign_sessions.empty:
                matched_channel = campaign_sessions.iloc[0].get(
                    "default_channel_group", ""
                )
                matched_session = str(campaign_sessions.iloc[0].get("session_id", ""))

        ga4_channel = str(matched_channel or "Unmatched").strip()
        ads_channel = "Paid Search"

        if ga4_channel.lower() not in paid_channels and ga4_channel != "Unmatched":
            pattern = f"Google Ads ({ads_channel}) vs GA4 ({ga4_channel})"
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            findings.append(
                {
                    "issue_type": "Channel mismatch",
                    "google_ads_campaign": campaign,
                    "google_ads_channel": ads_channel,
                    "ga4_channel": ga4_channel,
                    "ga4_session_id": matched_session,
                    "gclid": gclid,
                    "conversion_action": ad_row.get("conversion_action", ""),
                    "conversion_date": str(ad_row.get("conversion_date", "")),
                    "pattern": pattern,
                }
            )

    top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for pattern, count in top_patterns:
        findings.append(
            {
                "issue_type": "Common discrepancy pattern",
                "pattern": pattern,
                "occurrences": count,
                "detail": f"This mismatch pattern appeared {count} time(s) in the audit period",
            }
        )

    issue_count = sum(1 for f in findings if f["issue_type"] == "Channel mismatch")
    if issue_count:
        summary = (
            f"Found {issue_count} conversions where Google Ads and GA4 disagree on "
            "channel attribution. The most common patterns are listed below."
        )
        severity = "warning" if issue_count >= 2 else "info"
    else:
        summary = "GA4 channel grouping aligns with Google Ads campaign attribution."
        severity = "pass"

    return AuditResult(
        name="Channel Discrepancy Report",
        summary=summary,
        findings=findings,
        severity=severity,
        issue_count=issue_count,
        methodology=(
            "Each Google Ads conversion is matched to a GA4 session by gclid or "
            "campaign name. The GA4 default channel grouping is compared to the "
            "expected Paid Search attribution from Google Ads."
        ),
    )
