# ga4-attribution-audit

Marketing teams lose budget to attribution errors that GA4's interface makes hard to catch at scale: duplicate phone conversions, paid traffic showing as Direct, and UTM fragments splitting one campaign into three. Clicking through explorations works for a single check on a single day. It does not work when you need the same five checks run across 30 days, three data sources, and a client-ready report before Monday's standup.

This toolkit pulls GA4 data through the Data API (or CSV exports), cross-references CallRail and Google Ads, and surfaces the issues that actually change channel ROI calculations.

## Features

- **Duplicate conversion detection** - Match GA4 conversion events to CallRail calls within a configurable time window
- **Channel discrepancy report** - Compare GA4 default channel grouping against Google Ads campaign attribution
- **Attribution gap detection** - Find direct/none conversions, untagged landing pages, and out-of-window conversions
- **Conversion event hygiene** - Inventory all events, flag misconfigured triggers and deprecated conversions
- **UTM consistency** - Surface casing inconsistencies and non-standard medium values
- **Markdown and HTML reports** - Readable output for marketing managers, not just developers
- **Sample data included** - Run a full audit with zero credentials in under two minutes
- **Live API support** - Connect real GA4 and Google Ads accounts via environment variables

## Quick Start

```bash
git clone https://github.com/your-org/ga4-attribution-audit.git
cd ga4-attribution-audit
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
ga4-audit sample
```

Open `examples/sample_report.md` to review the Harbor Goods fictional client audit.

Generate HTML output:

```bash
ga4-audit sample --format html --output examples/sample_report.html
```

Run against your own config:

```bash
ga4-audit run --config examples/config.yaml --output report.md
ga4-audit validate-config examples/config.yaml
```

## Why Python

The GA4 Data API client is mature in Python, pandas makes cross-source joins concise, and Jinja2 report templating is straightforward. Type hints, pytest, and ruff/black round out a stack that agency analytics engineers already use.

## Configuration Reference

Create a YAML file pointing at your data sources:

```yaml
client_name: Harbor Goods
property_id: "987654321"

date_range:
  start: "2026-05-01"
  end: "2026-05-30"

conversion_events:
  - purchase
  - generate_lead
  - phone_call_conversion

channel_groupings:
  - sessionDefaultChannelGroup

duplicate_window_minutes: 5
attribution_window_days: 30
high_value_landing_page_threshold: 15
suspicious_event_count_threshold: 80

sources:
  ga4:
    mode: csv          # or "api"
    path: sample_data/ga4_sample.csv
  callrail:
    mode: csv
    path: sample_data/callrail_sample.csv
  google_ads:
    mode: csv          # or "api"
    path: sample_data/ads_sample.csv
    # customer_id: "123-456-7890"  # required for api mode
```

| Key | Description |
|-----|-------------|
| `property_id` | GA4 property numeric ID |
| `date_range` | Audit period (YYYY-MM-DD) |
| `conversion_events` | Event names to include in conversion checks |
| `duplicate_window_minutes` | Max minutes between GA4 conversion and CallRail call to flag duplicate |
| `attribution_window_days` | Max days between session start and conversion |
| `high_value_landing_page_threshold` | Session count above which landing pages are checked for UTMs |
| `suspicious_event_count_threshold` | Event count above which hygiene check flags misconfiguration |
| `sources.*.mode` | `csv` for exports, `api` for live pulls |

Paths in `sources.*.path` are relative to the config file directory.

## Audits Explained

### Duplicate Conversion Detection

Cross-references GA4 conversion timestamps against CallRail call start times. When both fire within the duplicate window, the same customer action is likely counted twice. Also flags CallRail calls with no matching GA4 session, which usually means dynamic number insertion or GTM is broken on that page.

### Channel Discrepancy Report

Google Ads knows a click converted. GA4 may assign that session to Direct or Organic if auto-tagging or UTMs failed. This check matches Ads conversions to GA4 sessions and compares channel labels.

### Attribution Gap Detection

Conversions tagged as Direct/none often mask untagged email or social traffic. High-traffic landing pages without UTMs make channel ROI impossible to calculate. Conversions outside the attribution window suggest event configuration or lookback issues.

### Conversion Event Hygiene

Lists every event with counts and share of total. Events firing hundreds of times per day are usually misconfigured GTM triggers. Configured conversion events with zero activity are likely deprecated but still marked in GA4 admin.

### UTM Consistency

GA4 treats `Facebook`, `facebook`, and `FaceBook` as three sources. Non-standard mediums like `print` or `flyer` fragment reports. This check groups variants and flags values outside standard conventions.

## Sample Report

A committed sample report from the Harbor Goods fictional e-commerce client is at [`examples/sample_report.md`](examples/sample_report.md).

The report tells a coherent story: Harbor Goods ran spring sale campaigns across Google Ads and Facebook, but phone call conversions double-counted in GA4, two offline CallRail calls never matched a session, and several Google Ads purchases appeared as Direct in GA4. UTM casing splits further diluted Facebook reporting.

![Executive summary showing 15 total issues across duplicate conversions, channel discrepancies, and UTM inconsistencies for Harbor Goods spring sale audit](examples/sample_report.md)

## Setting Up Real Credentials

See [docs/api-credentials-setup.md](docs/api-credentials-setup.md) for service account setup, Google Ads API tokens, and CallRail export instructions.

Copy `.env.example` to `.env` and set:

- `GOOGLE_APPLICATION_CREDENTIALS` for GA4 API pulls
- `GOOGLE_ADS_*` variables for live Google Ads data

Set `sources.ga4.mode: api` and `sources.google_ads.mode: api` in your config to use live pulls.

List conversion events for a property:

```bash
ga4-audit list-conversions --property-id 123456789
```

## Extending with New Audits

1. Create a module in `src/ga4_audit/audits/` with a `run(data: AuditData) -> AuditResult` function.
2. Return an `AuditResult` with `name`, `summary`, `findings`, `severity`, and `methodology`.
3. Register the module in `AUDIT_MODULES` in `src/ga4_audit/cli.py`.
4. Add tests under `tests/`.

The report template iterates all results automatically. No template changes required for basic new checks.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
black src tests
```

## Why This Exists

Built by [Medium & Message](https://mediumandmessage.com) to demonstrate attribution auditing in code, not just GA4 interface clicks. Marketing agencies hiring for GA4 work want proof you can diagnose tracking issues programmatically. This repo is the generalized version of tooling used on client engagements.

## License

MIT. See [LICENSE](LICENSE).
