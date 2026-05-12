# Interpreting the Report

This guide helps marketing managers and analysts understand audit output without reading Python code.

## Executive Summary

The top section lists total issues found, grouped by severity:

- **Critical**: Likely double-counting or major tracking gaps that affect budget decisions.
- **Warning**: Attribution mismatches or hygiene issues that skew channel reporting.
- **Info**: Minor inconsistencies worth documenting but not urgent.
- **Pass**: Check completed with no issues.

## Duplicate Conversion Detection

**What it means:** A GA4 conversion fired within minutes of a CallRail phone call, or a CallRail call has no matching GA4 session.

**Why it matters:** Phone call conversions often fire in both CallRail and GA4, inflating ROAS. Calls without GA4 sessions indicate broken dynamic number insertion or missing GTM tags.

**What to do:** Deduplicate phone events in GTM, verify CallRail swap script on all pages, and confirm gclid passthrough on paid landing pages.

## Channel Discrepancy Report

**What it means:** Google Ads recorded a conversion, but GA4 assigned the session to a different channel (often Direct or Organic).

**Why it matters:** Paid search budget decisions rely on GA4 channel reports. Misattributed conversions hide true paid performance.

**What to do:** Verify auto-tagging in Google Ads, check UTM parameters on final URLs, and review GA4 channel grouping rules.

## Attribution Gap Detection

**What it means:** Conversions appear as Direct traffic, high-traffic pages lack UTM tags, or conversions fall outside the attribution window.

**Why it matters:** Direct traffic is often a catch-all for untagged campaigns. Missing UTMs on key landing pages make channel ROI impossible to calculate.

**What to do:** Tag all paid, email, and partner links. Add UTMs to QR codes and offline campaigns. Review conversion window settings in GA4.

## Conversion Event Hygiene

**What it means:** Some events fire too often (misconfigured triggers) or not at all (deprecated events still marked as conversions).

**Why it matters:** Inflated conversion counts break bidding algorithms and client reporting.

**What to do:** Audit GTM triggers, remove scroll or timer events marked as conversions, and archive unused events.

## UTM Consistency

**What it means:** The same campaign source appears with different casing (Facebook vs facebook) or non-standard medium values (print, flyer).

**Why it matters:** GA4 treats casing variants as separate sources, fragmenting campaign reports.

**What to do:** Publish a UTM style guide and enforce lowercase values in campaign build templates.

## Recommended Next Steps

The report ends with prioritized actions based on findings. Address critical items before the next reporting cycle.
