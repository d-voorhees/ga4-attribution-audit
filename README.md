# GA4 Attribution Audit

Marketing teams lose budget to attribution errors that GA4's interface makes hard to catch at scale: duplicate phone conversions, paid traffic showing as Direct, and UTM fragments splitting one campaign into three. Clicking through explorations works for a single check on a single day. It does not work when you need the same five checks run across 30 days, three data sources, and a client-ready report before Monday.

This toolkit pulls GA4 data through the Data API (or CSV exports), cross-references CallRail and Google Ads, and surfaces the issues that change channel ROI calculations. Output is markdown or HTML, structured for a marketing manager audience.

For the technical narrative on the audit design decisions, the sample data approach, and the call-matching logic, see the companion post: https://dvoorhees.com/2026/05/12/auditing-ga4-attribution-in-code-duplicate-conversions-channel-discrepancies-and-utm-drift/

## What it does

Five audits run against GA4 data, cross-referenced against CallRail call records and Google Ads campaign data.

**Duplicate conversion detection** matches GA4 conversion event timestamps against CallRail call start times within a configurable window. When both fire for the same customer action, the conversion is counted twice. The audit also flags CallRail calls with no matching GA4 session, which usually means dynamic number insertion or GTM is broken on that page.

**Channel discrepancy report** compares GA4's default channel grouping against Google Ads campaign attribution. Google Ads knows a click converted. GA4 may assign that same session to Direct or Organic if auto-tagging or UTMs failed.

**Attribution gap detection** surfaces conversions tagged as Direct/none (often masking untagged email or social traffic), high-traffic landing pages without UTMs (making channel ROI impossible to calculate), and conversions outside the configured attribution window (suggesting event configuration or lookback issues).

**Conversion event hygiene** inventories all events with counts and share of total. Events firing hundreds of times per day are usually misconfigured GTM triggers. Configured conversion events with zero activity are likely deprecated but still marked in GA4 admin.

**UTM consistency** surfaces casing inconsistencies (`Facebook` vs `facebook` vs `FaceBook`, which GA4 treats as three separate sources) and non-standard medium values that fragment reports.

## Quick start

```bash
git clone https://github.com/d-voorhees/ga4-attribution-audit.git
cd ga4-attribution-audit
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
ga4-audit sample
```

Open `examples/sample_report.md` to review the Harbor Goods fictional client audit. The full audit runs against included sample data with zero credentials in under two minutes.

Generate HTML output:

```bash
ga4-audit sample --format html --output examples/sample_report.html
```

Run against your own configuration:

```bash
ga4-audit run --config examples/config.yaml --output report.md
ga4-audit validate-config examples/config.yaml
```

List conversion events for a GA4 property:

```bash
ga4-audit list-conversions --property-id 123456789
```

## Repository structure

```
ga4-attribution-audit/
├── src/ga4_audit/
│   ├── audits/              One module per audit type
│   │   ├── duplicate_detection.py
│   │   ├── channel_discrepancy.py
│   │   ├── attribution_gaps.py
│   │   ├── conversion_hygiene.py
│   │   └── utm_consistency.py
│   ├── cli.py               CLI entry point and audit registration
│   └── AUDIT_MODULES        Registry of active audits
├── examples/
│   ├── config.yaml          Sample configuration
│   └── sample_report.md     Harbor Goods fictional client audit
├── sample_data/
│   ├── ga4_sample.csv
│   ├── callrail_sample.csv
│   └── ads_sample.csv
├── docs/
│   └── api-credentials-setup.md
├── tests/
└── .env.example
```

## Configuration

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

| Key | What it controls |
|-----|-----------------|
| `property_id` | GA4 property numeric ID |
| `date_range` | Audit period (YYYY-MM-DD format) |
| `conversion_events` | Event names included in conversion checks |
| `duplicate_window_minutes` | Maximum minutes between a GA4 conversion and a CallRail call to flag as a duplicate |
| `attribution_window_days` | Maximum days between session start and conversion |
| `high_value_landing_page_threshold` | Session count above which landing pages are checked for UTM presence |
| `suspicious_event_count_threshold` | Daily event count above which the hygiene check flags likely misconfiguration |
| `sources.*.mode` | `csv` for file exports, `api` for live API pulls |

Paths in `sources.*.path` are relative to the configuration file directory.

## Why Python

The GA4 Data API client is mature in Python. Pandas makes cross-source joins concise. Jinja2 handles report templating. Type hints, pytest, and ruff/black round out a stack that agency analytics engineers already use daily.

## The sample report

A committed sample report from the Harbor Goods fictional e-commerce client is at [`examples/sample_report.md`](examples/sample_report.md).

The sample data tells a coherent story: Harbor Goods ran spring sale campaigns across Google Ads and Facebook. Phone call conversions double-counted in GA4. Two offline CallRail calls never matched a session. Several Google Ads purchases appeared as Direct in GA4. UTM casing splits diluted Facebook reporting further. The audit catches all of these and presents them in a format a marketing manager can act on.

## Setting up real credentials

See [docs/api-credentials-setup.md](docs/api-credentials-setup.md) for service account setup, Google Ads API tokens, and CallRail export instructions.

Copy `.env.example` to `.env` and set:

- `GOOGLE_APPLICATION_CREDENTIALS` for GA4 API pulls
- `GOOGLE_ADS_*` variables for live Google Ads data

Set `sources.ga4.mode: api` and `sources.google_ads.mode: api` in your configuration to use live pulls.

## Design decisions and tradeoffs

**CSV-first, API-optional.** Most agency analytics engineers already export data to CSV for client work. Making CSV the default input mode means the tool runs without service account setup, OAuth flows, or API quota management. API mode exists for teams that want automated runs, but the CSV path keeps the barrier to first use at zero.

**Sample data with a coherent narrative.** The Harbor Goods sample is not random test data. The fictional audit tells a story with realistic patterns (double-counted phone conversions, auto-tagging failures, UTM casing splits) so that the sample report reads like a real deliverable. A reviewer can evaluate the tool's output quality without connecting their own GA4 property.

**Configurable duplicate window.** The default five-minute window between a GA4 conversion event and a CallRail call to flag a duplicate is a judgment call. Phone calls that happen more than five minutes after a page conversion are likely separate actions. Calls within seconds are almost certainly the same action tracked twice. The window is exposed as a configuration parameter because the right value depends on the client's conversion flow.

**Markdown and HTML output, not PDF.** Markdown renders on GitHub, pastes into Slack, and converts to any format. HTML opens in a browser and prints to PDF. Generating PDF directly would add a dependency (WeasyPrint or similar) and a rendering layer without adding capability the existing formats do not cover.

## Extending with new audits

1. Create a module in `src/ga4_audit/audits/` with a `run(data: AuditData) -> AuditResult` function.
2. Return an `AuditResult` with `name`, `summary`, `findings`, `severity`, and `methodology`.
3. Register the module in `AUDIT_MODULES` in `src/ga4_audit/cli.py`.
4. Add tests under `tests/`.

The report template iterates all results automatically.

## What this does not do

This toolkit audits attribution data. It does not fix the underlying tracking problems it surfaces. A channel discrepancy between GA4 and Google Ads requires investigating auto-tagging configuration, UTM parameters, or cross-domain tracking setup on the actual site. A duplicate conversion requires deciding which system (GA4 or CallRail) is the source of truth for that conversion type. The audit tells you where to look; remediation depends on the specific implementation.

The toolkit does not connect to HubSpot, Salesforce, or other CRMs. It operates on the analytics and ad platform layer. Attribution data that flows from GA4 into a CRM is a separate integration problem (see the companion [GA4-to-HubSpot Attribution Bridge](https://github.com/d-voorhees/ga4-hubspot-attribution-bridge) for that use case).

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
black src tests
```

## Why this exists

Built by [Medium & Message](https://mediumandmessage.com) to demonstrate attribution auditing in code. Marketing agencies hiring for GA4 work want proof you can diagnose tracking issues programmatically, not through interface clicks. This repo is the generalized version of tooling used on client engagements.

## License

MIT. See [LICENSE](LICENSE).
