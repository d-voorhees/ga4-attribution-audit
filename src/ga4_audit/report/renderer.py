"""Report rendering for Markdown and HTML output."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ga4_audit.audits import AuditResult
from ga4_audit.config import AuditConfig
from ga4_audit.sources import AuditData

SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2, "pass": 3}


def _severity_rank(severity: str) -> int:
    return SEVERITY_ORDER.get(severity, 99)


def build_report_context(
    config: AuditConfig,
    data: AuditData,
    results: list[AuditResult],
) -> dict[str, Any]:
    """Build the template context for report rendering.

    Args:
        config: Audit configuration.
        data: Loaded datasets.
        results: List of audit results.

    Returns:
        Context dict for Jinja2 templates.
    """
    total_issues = sum(r.issue_count for r in results)
    severity_counts: dict[str, int] = {}
    for result in results:
        severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1

    executive = sorted(results, key=lambda r: _severity_rank(r.severity))

    recommendations = _build_recommendations(results)

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "client_name": config.client_name,
        "config": config,
        "source_modes": data.source_modes,
        "session_count": len(data.ga4_sessions),
        "conversion_count": len(data.ga4_conversions),
        "callrail_count": len(data.callrail),
        "ads_count": len(data.google_ads),
        "total_issues": total_issues,
        "severity_counts": severity_counts,
        "executive_summary": executive,
        "results": results,
        "recommendations": recommendations,
    }


def _build_recommendations(results: list[AuditResult]) -> list[str]:
    """Generate actionable next steps from audit findings."""
    recs: list[str] = []
    by_name = {r.name: r for r in results}

    dup = by_name.get("Duplicate Conversion Detection")
    if dup and dup.issue_count:
        recs.append(
            "Review phone call conversion events in GTM/GA4 and exclude or deduplicate "
            "events that fire on the same CallRail-tracked call."
        )

    channel = by_name.get("Channel Discrepancy Report")
    if channel and channel.issue_count:
        recs.append(
            "Align UTM tagging and gclid auto-tagging on Google Ads landing pages so "
            "GA4 default channel grouping matches paid search attribution."
        )

    gaps = by_name.get("Attribution Gap Detection")
    if gaps and gaps.issue_count:
        recs.append(
            "Add UTM parameters to email, social, and partner links pointing at "
            "high-traffic landing pages currently showing as direct traffic."
        )

    hygiene = by_name.get("Conversion Event Hygiene")
    if hygiene and hygiene.issue_count:
        recs.append(
            "Audit GTM triggers for conversion events with unusually high counts and "
            "archive deprecated events no longer tied to business outcomes."
        )

    utm = by_name.get("UTM Consistency")
    if utm and utm.issue_count:
        recs.append(
            "Publish a UTM naming convention document and enforce lowercase source/medium "
            "values in campaign build checklists."
        )

    if not recs:
        recs.append(
            "No critical issues found. Re-run this audit monthly or after major "
            "campaign or tracking changes."
        )

    return recs


def render_report(
    config: AuditConfig,
    data: AuditData,
    results: list[AuditResult],
    output_format: str = "markdown",
) -> str:
    """Render the audit report as Markdown or HTML.

    Args:
        config: Audit configuration.
        data: Loaded datasets.
        results: Audit results from all modules.
        output_format: Either 'markdown' or 'html'.

    Returns:
        Rendered report string.
    """
    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["md_cell"] = lambda value: str(value).replace("|", "\\|")

    context = build_report_context(config, data, results)
    context["results_dicts"] = [asdict(r) for r in results]

    template_name = "report.html.j2" if output_format == "html" else "report.md.j2"
    template = env.get_template(template_name)
    return template.render(**context)


def write_report(
    content: str,
    output_path: str | Path,
) -> Path:
    """Write rendered report content to disk.

    Args:
        content: Rendered report string.
        output_path: Destination file path.

    Returns:
        Path to the written file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
