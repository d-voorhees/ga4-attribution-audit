"""UTM parameter consistency checks."""

from __future__ import annotations

from ga4_audit.audits import AuditResult
from ga4_audit.sources import AuditData
from ga4_audit.utils.normalize import casing_variants, normalize_string


def run(data: AuditData) -> AuditResult:
    """Surface UTM casing inconsistencies and non-standard medium values.

    Args:
        data: Loaded audit datasets.

    Returns:
        AuditResult with UTM consistency findings.
    """
    config = data.config
    findings: list[dict[str, object]] = []
    sessions = data.ga4_sessions

    source_values = sessions.get("session_source", sessions.get("utm_source", []))
    medium_values = sessions.get("session_medium", sessions.get("utm_medium", []))
    campaign_values = sessions.get("session_campaign", sessions.get("utm_campaign", []))

    for param_name, values in [
        ("utm_source", source_values.astype(str).tolist()),
        ("utm_medium", medium_values.astype(str).tolist()),
        ("utm_campaign", campaign_values.astype(str).tolist()),
    ]:
        variants = casing_variants(values)
        for canonical, observed in variants.items():
            findings.append(
                {
                    "issue_type": "UTM casing inconsistency",
                    "parameter": param_name,
                    "canonical_form": canonical,
                    "observed_variants": ", ".join(observed),
                    "variant_count": len(observed),
                    "detail": (
                        f"Parameter {param_name} appears with {len(observed)} different "
                        f"casing variants: {', '.join(observed)}"
                    ),
                }
            )

    standard_mediums = {normalize_string(m) for m in config.utm_standard_mediums}
    seen_mediums: set[str] = set()
    for raw in medium_values.astype(str):
        medium = normalize_string(raw)
        if not medium or medium in {"(not set)", "(none)", "nan"}:
            continue
        if medium in seen_mediums:
            continue
        seen_mediums.add(medium)
        if medium not in standard_mediums:
            count = int((medium_values.astype(str).str.lower() == medium).sum())
            findings.append(
                {
                    "issue_type": "Non-standard medium value",
                    "medium": raw,
                    "normalized": medium,
                    "session_count": count,
                    "detail": (
                        f"Medium value '{raw}' does not match standard conventions "
                        "(cpc, organic, email, referral, social, etc.)"
                    ),
                }
            )

    casing_issues = sum(
        1 for f in findings if f["issue_type"] == "UTM casing inconsistency"
    )
    medium_issues = sum(
        1 for f in findings if f["issue_type"] == "Non-standard medium value"
    )
    issue_count = casing_issues + medium_issues

    if issue_count:
        summary = (
            f"Found {casing_issues} UTM casing inconsistencies and "
            f"{medium_issues} non-standard medium values across session data."
        )
        severity = "warning" if issue_count >= 3 else "info"
    else:
        summary = "UTM parameters appear consistent across session data."
        severity = "pass"

    return AuditResult(
        name="UTM Consistency",
        summary=summary,
        findings=findings,
        severity=severity,
        issue_count=issue_count,
        methodology=(
            "UTM source, medium, and campaign values are grouped by canonical lowercase "
            "form. Multiple casing variants for the same value are flagged. Medium values "
            "are compared against a standard list of recognized marketing mediums."
        ),
    )
