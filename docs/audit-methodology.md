# Audit Methodology

Technical reference for how each check works inside the toolkit.

## Data Loading

The toolkit loads three datasets based on `config.yaml`:

| Source | CSV mode | API mode |
|--------|----------|----------|
| GA4 | Unified session/conversion CSV export | Google Analytics Data API v1beta |
| CallRail | Standard Calls export CSV | Not supported |
| Google Ads | Campaign conversion CSV export | Google Ads API v17+ |

All timestamps are normalized to timezone-naive UTC for matching.

## Duplicate Conversion Detection

1. For each GA4 conversion event, find CallRail calls where `|conversion_time - call_start| <= duplicate_window_minutes`.
2. Matching pairs are flagged as likely duplicates.
3. For each CallRail call, search GA4 sessions by gclid, landing page substring, or session start within 2x the duplicate window.
4. Calls with no session match are flagged as tracking gaps.

Default window: 5 minutes (configurable via `duplicate_window_minutes`).

## Channel Discrepancy Report

1. For each Google Ads conversion row, match to a GA4 session by gclid or campaign name substring.
2. Read the GA4 `default_channel_group` for the matched session.
3. If GA4 channel is not a paid channel (Paid Search, Paid Social, Display, Cross-network), flag as mismatch.
4. Aggregate mismatch patterns and report the top recurring combinations.

## Attribution Gap Detection

Three sub-checks:

1. **Direct/none conversions:** Sessions with conversion events where both source and medium are direct, none, or empty.
2. **UTM coverage:** Landing pages exceeding `high_value_landing_page_threshold` sessions without UTM parameters in URL or session fields.
3. **Attribution window:** Conversions where `event_timestamp - session_start > attribution_window_days`.

## Conversion Event Hygiene

1. Aggregate event counts from the GA4 events frame.
2. Calculate each event's percentage of total fires.
3. Flag events exceeding `suspicious_event_count_threshold`.
4. Flag configured conversion events with zero rows in the export.

## UTM Consistency

1. Collect all source, medium, and campaign values from session data.
2. Group by canonical lowercase form; flag groups with more than one casing variant.
3. Compare medium values against the standard list in config; flag unrecognized values.

## Report Generation

Findings are rendered through Jinja2 templates into Markdown or HTML. Each section includes a plain-English summary, findings table, and methodology note. The executive summary ranks audits by severity (critical > warning > info > pass).

## Extending Audits

Add a new module under `src/ga4_audit/audits/` exposing `run(data: AuditData) -> AuditResult`. Register it in `AUDIT_MODULES` in `cli.py`. The report template iterates all results automatically.
