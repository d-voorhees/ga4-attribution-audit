# Harbor Goods GA4 Attribution Audit

**Generated:** 2026-06-18 13:36:31

---

## Executive Summary

This audit reviewed **220** GA4 sessions, **26** conversions, **12** CallRail calls, and **7** Google Ads conversions for **Harbor Goods**.

**Total issues found:** 25

| Severity | Audits |
|----------|--------|
| Critical | 1 |
| Warning | 2 |
| Info | 2 |

### Findings by audit (severity-ranked)

- **Duplicate Conversion Detection** (critical): 7 issue(s). Found 4 likely duplicate conversions and 3 CallRail calls with no matching GA4 session. These patterns usually indicate double-counting or call tracking gaps.
- **Channel Discrepancy Report** (warning): 2 issue(s). Found 2 conversions where Google Ads and GA4 disagree on channel attribution. The most common patterns are listed below.
- **Attribution Gap Detection** (warning): 13 issue(s). Found 13 attribution gaps including direct/none conversions, landing pages without UTM coverage, and out-of-window conversions.
- **Conversion Event Hygiene** (info): 1 issue(s). Reviewed 8 GA4 events and flagged 1 hygiene issues. See inventory table for full event breakdown.
- **UTM Consistency** (info): 2 issue(s). Found 2 UTM casing inconsistencies and 0 non-standard medium values across session data.


---

## Audit Configuration

| Setting | Value |
|---------|-------|
| Property ID | 987654321 |
| Date range | 2026-05-01 to 2026-05-30 |
| Conversion events | purchase, generate_lead, phone_call_conversion |
| Channel groupings | sessionDefaultChannelGroup |
| Duplicate window | 5 minutes |
| Attribution window | 30 days |
| GA4 source | csv |
| CallRail source | csv |
| Google Ads source | csv |

---

## Duplicate Conversion Detection

Found 4 likely duplicate conversions and 3 CallRail calls with no matching GA4 session. These patterns usually indicate double-counting or call tracking gaps.

| Issue Type | Ga4 Session Id | Ga4 Event | Ga4 Timestamp | Callrail Id | Callrail Timestamp | Window Minutes | Detail | 
| --- | --- | --- | --- | --- | --- | --- | --- | 
| Likely duplicate conversion | S0012 | phone_call_conversion | 2026-05-08 14:32:02 | CR-1001 | 2026-05-08 14:32:00 | 5 | GA4 conversion occurred within 5 minutes of a CallRail call | 
| Likely duplicate conversion | S0001 | phone_call_conversion | 2026-05-12 10:15:01 | CR-1002 | 2026-05-12 10:15:00 | 5 | GA4 conversion occurred within 5 minutes of a CallRail call | 
| Likely duplicate conversion | S0049 | phone_call_conversion | 2026-05-22 15:30:03 | CR-1006 | 2026-05-22 15:30:00 | 5 | GA4 conversion occurred within 5 minutes of a CallRail call | 
| Likely duplicate conversion | S0021 | phone_call_conversion | 2026-05-26 17:55:02 | CR-1008 | 2026-05-26 17:55:00 | 5 | GA4 conversion occurred within 5 minutes of a CallRail call | 
| CallRail call without GA4 session |  |  |  | CR-1003 | 2026-05-15 16:45:00 |  | No matching GA4 session found for this call | 
| CallRail call without GA4 session |  |  |  | CR-1005 | 2026-05-20 11:08:00 |  | No matching GA4 session found for this call | 
| CallRail call without GA4 session |  |  |  | CR-1009 | 2026-05-28 08:40:00 |  | No matching GA4 session found for this call | 

---

## Channel Discrepancy Report

Found 2 conversions where Google Ads and GA4 disagree on channel attribution. The most common patterns are listed below.

| Issue Type | Google Ads Campaign | Google Ads Channel | Ga4 Channel | Ga4 Session Id | Gclid | Conversion Action | Conversion Date | Pattern | 
| --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| Channel mismatch | HG \| Search \| Brand | Paid Search | Direct | S0112 | CjwKCAjw789ghi | Lead Form | 2026-05-15 00:00:00 | Google Ads (Paid Search) vs GA4 (Direct) | 
| Channel mismatch | HG \| Search \| Spring Sale | Paid Search | Direct | S0209 | CjwKCAjw012jkl | Purchase | 2026-05-18 00:00:00 | Google Ads (Paid Search) vs GA4 (Direct) | 
| Common discrepancy pattern |  |  |  |  |  |  |  | Google Ads (Paid Search) vs GA4 (Direct) | 

---

## Attribution Gap Detection

Found 13 attribution gaps including direct/none conversions, landing pages without UTM coverage, and out-of-window conversions.

| Issue Type | Session Id | Landing Page | Session Source | Session Medium | Default Channel Group | Detail | 
| --- | --- | --- | --- | --- | --- | --- | 
| Conversion with direct/none attribution | S0067 | https://www.harborgoods.com/products/coastal-table | (direct) | (none) | Direct | Session has a conversion but source/medium appear as direct or none, which often indicates a tagging gap | 
| Conversion with direct/none attribution | S0112 | https://www.harborgoods.com/pages/contact | (direct) | (none) | Direct | Session has a conversion but source/medium appear as direct or none, which often indicates a tagging gap | 
| Conversion with direct/none attribution | S0156 | https://www.harborgoods.com/pages/contact?utm_source=(direct)&utm_medium=(none) | (direct) | (none) | Direct | Session has a conversion but source/medium appear as direct or none, which often indicates a tagging gap | 
| Conversion with direct/none attribution | S0178 | https://www.harborgoods.com/products/coastal-table | (direct) | (none) | Direct | Session has a conversion but source/medium appear as direct or none, which often indicates a tagging gap | 
| Conversion with direct/none attribution | S0195 | https://www.harborgoods.com/products/harbor-chair?utm_source=(direct)&utm_medium=(none) | (direct) | (none) | Direct | Session has a conversion but source/medium appear as direct or none, which often indicates a tagging gap | 
| Conversion with direct/none attribution | S0209 | https://www.harborgoods.com/products/coastal-table | (direct) | (none) | Direct | Session has a conversion but source/medium appear as direct or none, which often indicates a tagging gap | 
| High-traffic landing page without UTM coverage |  | https://www.harborgoods.com/ |  |  |  | Landing page exceeds 15 sessions but shows no UTM parameters in session data | 
| High-traffic landing page without UTM coverage |  | https://www.harborgoods.com/collections/outdoor |  |  |  | Landing page exceeds 15 sessions but shows no UTM parameters in session data | 
| High-traffic landing page without UTM coverage |  | https://www.harborgoods.com/collections/sale |  |  |  | Landing page exceeds 15 sessions but shows no UTM parameters in session data | 
| High-traffic landing page without UTM coverage |  | https://www.harborgoods.com/pages/contact |  |  |  | Landing page exceeds 15 sessions but shows no UTM parameters in session data | 
| High-traffic landing page without UTM coverage |  | https://www.harborgoods.com/products/coastal-table |  |  |  | Landing page exceeds 15 sessions but shows no UTM parameters in session data | 
| High-traffic landing page without UTM coverage |  | https://www.harborgoods.com/products/harbor-chair |  |  |  | Landing page exceeds 15 sessions but shows no UTM parameters in session data | 
| Conversion outside attribution window | S0033 |  |  |  |  | Conversion occurred 35 days after session start, exceeding the 30-day window | 

---

## Conversion Event Hygiene

Reviewed 8 GA4 events and flagged 1 hygiene issues. See inventory table for full event breakdown.

| Issue Type | Event Name | Event Count | Percent Of Total | Threshold | Is Configured Conversion | Detail | 
| --- | --- | --- | --- | --- | --- | --- | 
| High event count | page_view | 223 | 86.1 | 80 | False | Event count (223) exceeds threshold (80), which may indicate a misconfigured trigger | 
| Event inventory | page_view | 223 | 86.1 |  | False |  | 
| Event inventory | purchase | 12 | 4.63 |  | True |  | 
| Event inventory | phone_call_conversion | 9 | 3.47 |  | True |  | 
| Event inventory | generate_lead | 5 | 1.93 |  | True |  | 
| Event inventory | click | 3 | 1.16 |  | False |  | 
| Event inventory | scroll | 3 | 1.16 |  | False |  | 
| Event inventory | view_item | 3 | 1.16 |  | False |  | 
| Event inventory | add_to_cart | 1 | 0.39 |  | False |  | 

---

## UTM Consistency

Found 2 UTM casing inconsistencies and 0 non-standard medium values across session data.

| Issue Type | Parameter | Canonical Form | Observed Variants | Variant Count | Detail | 
| --- | --- | --- | --- | --- | --- | 
| UTM casing inconsistency | utm_source | facebook | FaceBook, Facebook, facebook | 3 | Parameter utm_source appears with 3 different casing variants: FaceBook, Facebook, facebook | 
| UTM casing inconsistency | utm_medium | cpc | CPC, Cpc, cpc | 3 | Parameter utm_medium appears with 3 different casing variants: CPC, Cpc, cpc | 

---

## Methodology Notes

### Duplicate Conversion Detection

GA4 conversion events are matched to CallRail calls within 5 minutes by timestamp. Calls are checked for a corresponding GA4 session by gclid, landing page, or nearby session start time.

### Channel Discrepancy Report

Each Google Ads conversion is matched to a GA4 session by gclid or campaign name. The GA4 default channel grouping is compared to the expected Paid Search attribution from Google Ads.

### Attribution Gap Detection

Sessions with conversions are checked for direct/none source-medium pairs. Landing pages above the session threshold are checked for UTM parameters. Conversions are compared against session start dates using the configured attribution window.

### Conversion Event Hygiene

Event counts are totaled across the audit period. Events exceeding the configured threshold are flagged as potentially misconfigured. Configured conversion events with zero activity are flagged as likely deprecated.

### UTM Consistency

UTM source, medium, and campaign values are grouped by canonical lowercase form. Multiple casing variants for the same value are flagged. Medium values are compared against a standard list of recognized marketing mediums.

---

## Recommended Next Steps

1. Review phone call conversion events in GTM/GA4 and exclude or deduplicate events that fire on the same CallRail-tracked call.
1. Align UTM tagging and gclid auto-tagging on Google Ads landing pages so GA4 default channel grouping matches paid search attribution.
1. Add UTM parameters to email, social, and partner links pointing at high-traffic landing pages currently showing as direct traffic.
1. Audit GTM triggers for conversion events with unusually high counts and archive deprecated events no longer tied to business outcomes.
1. Publish a UTM naming convention document and enforce lowercase source/medium values in campaign build checklists.


---

*Report generated by [ga4-attribution-audit](https://github.com/example/ga4-attribution-audit).*