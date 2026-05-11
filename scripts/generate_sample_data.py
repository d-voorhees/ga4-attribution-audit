#!/usr/bin/env python3
"""Generate realistic Harbor Goods sample data for the attribution audit toolkit."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "examples" / "sample_data"
START = datetime(2026, 5, 1)
END = datetime(2026, 5, 30)

CHANNELS = [
    ("google", "cpc", "Paid Search", "spring-sale-search"),
    ("facebook", "paid", "Paid Social", "spring-sale-social"),
    ("newsletter", "email", "Email", "may-newsletter"),
    ("instagram", "social", "Organic Social", "organic-social"),
    ("(direct)", "(none)", "Direct", ""),
    ("bing", "cpc", "Paid Search", "spring-sale-bing"),
    ("partnerco", "referral", "Referral", "partner-q2"),
]

LANDING_PAGES = [
    "https://www.harborgoods.com/",
    "https://www.harborgoods.com/collections/outdoor",
    "https://www.harborgoods.com/products/harbor-chair",
    "https://www.harborgoods.com/products/coastal-table",
    "https://www.harborgoods.com/pages/contact",
    "https://www.harborgoods.com/collections/sale",
]

GCLIDS = [
    "CjwKCAjw123abc",
    "CjwKCAjw456def",
    "CjwKCAjw789ghi",
    "CjwKCAjw012jkl",
    "CjwKCAjw345mno",
    "CjwKCAjw678pqr",
    "CjwKCAjw901stu",
]


def random_date() -> datetime:
    delta = (END - START).days
    day_offset = random.randint(0, delta)
    hour = random.randint(8, 20)
    minute = random.randint(0, 59)
    return START + timedelta(days=day_offset, hours=hour - 8, minutes=minute)


def generate_ga4() -> None:
    rows: list[dict] = []
    session_count = 220

    for i in range(1, session_count + 1):
        sid = f"S{i:04d}"
        session_start = random_date()
        source, medium, channel, campaign = random.choice(CHANNELS)
        landing = random.choice(LANDING_PAGES)
        gclid = random.choice(GCLIDS) if channel == "Paid Search" else ""

        if i % 17 == 0:
            source, medium = "(direct)", "(none)"
            channel = "Direct"

        if i % 23 == 0:
            source = random.choice(["Facebook", "facebook", "FaceBook"])

        if i % 29 == 0:
            medium = random.choice(["CPC", "cpc", "Cpc"])

        rows.append(
            {
                "session_id": sid,
                "date": session_start.strftime("%Y-%m-%d %H:%M:%S"),
                "session_start": session_start.strftime("%Y-%m-%d %H:%M:%S"),
                "session_source": source,
                "session_medium": medium,
                "session_campaign": campaign,
                "default_channel_group": channel,
                "landing_page": landing + (f"?utm_source={source}&utm_medium={medium}" if i % 3 == 0 else ""),
                "gclid": gclid,
                "conversion_event": "",
                "event_name": "page_view",
                "event_timestamp": "",
            }
        )

    conversion_specs = [
        ("S0042", "purchase", 0),
        ("S0058", "purchase", 2),
        ("S0071", "generate_lead", 1),
        ("S0093", "phone_call_conversion", 0),
        ("S0105", "phone_call_conversion", 3),
        ("S0120", "purchase", 0),
        ("S0133", "generate_lead", 0),
        ("S0147", "phone_call_conversion", 4),
        ("S0156", "purchase", 1),
        ("S0168", "generate_lead", 2),
        ("S0182", "purchase", 0),
        ("S0195", "phone_call_conversion", 0),
        ("S0201", "purchase", 0),
        ("S0210", "generate_lead", 0),
        ("S0215", "phone_call_conversion", 2),
        ("S0218", "purchase", 0),
        ("S0220", "generate_lead", 0),
    ]

    for sid, event, minute_offset in conversion_specs:
        base = next(r for r in rows if r["session_id"] == sid)
        conv_time = datetime.strptime(base["session_start"], "%Y-%m-%d %H:%M:%S") + timedelta(
            minutes=minute_offset
        )
        conv_row = base.copy()
        conv_row["conversion_event"] = event
        conv_row["event_name"] = event
        conv_row["event_timestamp"] = conv_time.strftime("%Y-%m-%d %H:%M:%S")
        rows.append(conv_row)

    direct_conversions = ["S0067", "S0112", "S0178", "S0209"]
    for sid in direct_conversions:
        base = next(r for r in rows if r["session_id"] == sid)
        base["session_source"] = "(direct)"
        base["session_medium"] = "(none)"
        base["default_channel_group"] = "Direct"
        conv_time = datetime.strptime(base["session_start"], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=5)
        conv_row = base.copy()
        conv_row["conversion_event"] = "purchase"
        conv_row["event_name"] = "purchase"
        conv_row["event_timestamp"] = conv_time.strftime("%Y-%m-%d %H:%M:%S")
        rows.append(conv_row)

    late_session = next(r for r in rows if r["session_id"] == "S0033")
    late_conv = late_session.copy()
    late_conv["conversion_event"] = "purchase"
    late_conv["event_name"] = "purchase"
    late_conv["event_timestamp"] = (
        datetime.strptime(late_session["session_start"], "%Y-%m-%d %H:%M:%S")
        + timedelta(days=35)
    ).strftime("%Y-%m-%d %H:%M:%S")
    rows.append(late_conv)

    for event, count in [("page_view", 850), ("scroll", 420), ("view_item", 310), ("add_to_cart", 95), ("purchase", 22), ("phone_call_conversion", 18), ("generate_lead", 14), ("click", 1200)]:
        for _ in range(min(count // 50, 3)):
            sid = f"S{random.randint(1, session_count):04d}"
            base = next(r for r in rows if r["session_id"] == sid)
            extra = base.copy()
            extra["event_name"] = event
            extra["conversion_event"] = event if event in {"purchase", "phone_call_conversion", "generate_lead"} else ""
            rows.append(extra)

    df = pd.DataFrame(rows)

    duplicate_pairs = [
        ("CjwKCAjw123abc", "2026-05-08 14:32:02", "phone_call_conversion"),
        ("CjwKCAjw456def", "2026-05-12 10:15:01", "phone_call_conversion"),
        ("CjwKCAjw012jkl", "2026-05-22 15:30:03", "phone_call_conversion"),
        ("CjwKCAjw345mno", "2026-05-26 17:55:02", "phone_call_conversion"),
    ]
    for gclid, conv_time, event in duplicate_pairs:
        match = df[(df["gclid"] == gclid) & (df["conversion_event"] == "")]
        if match.empty:
            continue
        base = match.iloc[0].to_dict()
        base["conversion_event"] = event
        base["event_name"] = event
        base["event_timestamp"] = conv_time
        df = pd.concat([df, pd.DataFrame([base])], ignore_index=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DIR / "ga4_sample.csv", index=False)
    conv_count = df["conversion_event"].astype(bool).sum()
    print(f"GA4: {session_count} sessions, {conv_count} conversion rows")


def generate_callrail() -> None:
    calls = [
        {
            "call_id": "CR-1001",
            "call_start": "2026-05-08 14:32:00",
            "duration_seconds": 245,
            "caller_number": "+15551234001",
            "tracking_number": "+18885551001",
            "landing_page": "https://www.harborgoods.com/pages/contact",
            "gclid": "CjwKCAjw123abc",
            "source": "google",
            "medium": "cpc",
            "campaign": "spring-sale-search",
        },
        {
            "call_id": "CR-1002",
            "call_start": "2026-05-12 10:15:00",
            "duration_seconds": 180,
            "caller_number": "+15551234002",
            "tracking_number": "+18885551001",
            "landing_page": "https://www.harborgoods.com/products/harbor-chair",
            "gclid": "CjwKCAjw456def",
            "source": "google",
            "medium": "cpc",
            "campaign": "spring-sale-search",
        },
        {
            "call_id": "CR-1003",
            "call_start": "2026-05-15 16:45:00",
            "duration_seconds": 320,
            "caller_number": "+15551234003",
            "tracking_number": "+18885551002",
            "landing_page": "https://www.harborgoods.com/promo/mailers-may",
            "gclid": "",
            "source": "facebook",
            "medium": "paid",
            "campaign": "spring-sale-social",
        },
        {
            "call_id": "CR-1004",
            "call_start": "2026-05-18 09:22:00",
            "duration_seconds": 95,
            "caller_number": "+15551234004",
            "tracking_number": "+18885551001",
            "landing_page": "https://www.harborgoods.com/",
            "gclid": "CjwKCAjw789ghi",
            "source": "google",
            "medium": "cpc",
            "campaign": "spring-sale-search",
        },
        {
            "call_id": "CR-1005",
            "call_start": "2026-05-20 11:08:00",
            "duration_seconds": 410,
            "caller_number": "+15551234005",
            "tracking_number": "+18885551003",
            "landing_page": "https://www.harborgoods.com/store-visit-qrcode",
            "gclid": "",
            "source": "direct",
            "medium": "none",
            "campaign": "",
        },
        {
            "call_id": "CR-1006",
            "call_start": "2026-05-22 15:30:00",
            "duration_seconds": 155,
            "caller_number": "+15551234006",
            "tracking_number": "+18885551001",
            "landing_page": "https://www.harborgoods.com/pages/contact",
            "gclid": "CjwKCAjw012jkl",
            "source": "google",
            "medium": "cpc",
            "campaign": "spring-sale-search",
        },
        {
            "call_id": "CR-1007",
            "call_start": "2026-05-24 13:17:00",
            "duration_seconds": 275,
            "caller_number": "+15551234007",
            "tracking_number": "+18885551002",
            "landing_page": "https://www.harborgoods.com/collections/sale",
            "gclid": "",
            "source": "bing",
            "medium": "cpc",
            "campaign": "spring-sale-bing",
        },
        {
            "call_id": "CR-1008",
            "call_start": "2026-05-26 17:55:00",
            "duration_seconds": 190,
            "caller_number": "+15551234008",
            "tracking_number": "+18885551001",
            "landing_page": "https://www.harborgoods.com/products/harbor-chair",
            "gclid": "CjwKCAjw345mno",
            "source": "google",
            "medium": "cpc",
            "campaign": "spring-sale-search",
        },
        {
            "call_id": "CR-1009",
            "call_start": "2026-05-28 08:40:00",
            "duration_seconds": 130,
            "caller_number": "+15551234009",
            "tracking_number": "+18885551004",
            "landing_page": "https://www.harborgoods.com/offline-flyer-landing",
            "gclid": "",
            "source": "offline",
            "medium": "print",
            "campaign": "store-flyer-may",
        },
        {
            "call_id": "CR-1010",
            "call_start": "2026-05-29 12:03:00",
            "duration_seconds": 340,
            "caller_number": "+15551234010",
            "tracking_number": "+18885551001",
            "landing_page": "https://www.harborgoods.com/pages/contact",
            "gclid": "CjwKCAjw678pqr",
            "source": "google",
            "medium": "cpc",
            "campaign": "spring-sale-search",
        },
        {
            "call_id": "CR-1011",
            "call_start": "2026-05-14 14:32:05",
            "duration_seconds": 200,
            "caller_number": "+15551234011",
            "tracking_number": "+18885551001",
            "landing_page": "https://www.harborgoods.com/pages/contact",
            "gclid": "CjwKCAjw123abc",
            "source": "google",
            "medium": "cpc",
            "campaign": "spring-sale-search",
        },
        {
            "call_id": "CR-1012",
            "call_start": "2026-05-19 10:15:03",
            "duration_seconds": 160,
            "caller_number": "+15551234012",
            "tracking_number": "+18885551001",
            "landing_page": "https://www.harborgoods.com/products/harbor-chair",
            "gclid": "CjwKCAjw456def",
            "source": "google",
            "medium": "cpc",
            "campaign": "spring-sale-search",
        },
    ]

    df = pd.DataFrame(calls)
    df.to_csv(OUTPUT_DIR / "callrail_sample.csv", index=False)
    print(f"CallRail: {len(calls)} calls")


def generate_ads() -> None:
    conversions = [
        {
            "campaign_name": "HG | Search | Spring Sale",
            "conversion_action": "Purchase",
            "conversion_date": "2026-05-08",
            "conversion_time": "2026-05-08 14:30:00",
            "conversions": 1,
            "conversion_value": 289.99,
            "gclid": "CjwKCAjw123abc",
        },
        {
            "campaign_name": "HG | Search | Spring Sale",
            "conversion_action": "Purchase",
            "conversion_date": "2026-05-12",
            "conversion_time": "2026-05-12 10:12:00",
            "conversions": 1,
            "conversion_value": 459.00,
            "gclid": "CjwKCAjw456def",
        },
        {
            "campaign_name": "HG | Search | Brand",
            "conversion_action": "Lead Form",
            "conversion_date": "2026-05-15",
            "conversion_time": "2026-05-15 16:40:00",
            "conversions": 1,
            "conversion_value": 50.00,
            "gclid": "CjwKCAjw789ghi",
        },
        {
            "campaign_name": "HG | Search | Spring Sale",
            "conversion_action": "Purchase",
            "conversion_date": "2026-05-18",
            "conversion_time": "2026-05-18 09:20:00",
            "conversions": 1,
            "conversion_value": 189.50,
            "gclid": "CjwKCAjw012jkl",
        },
        {
            "campaign_name": "HG | Search | Spring Sale",
            "conversion_action": "Phone Call",
            "conversion_date": "2026-05-22",
            "conversion_time": "2026-05-22 15:28:00",
            "conversions": 1,
            "conversion_value": 75.00,
            "gclid": "CjwKCAjw345mno",
        },
        {
            "campaign_name": "HG | PMax | All Products",
            "conversion_action": "Purchase",
            "conversion_date": "2026-05-24",
            "conversion_time": "2026-05-24 13:15:00",
            "conversions": 1,
            "conversion_value": 329.00,
            "gclid": "CjwKCAjw678pqr",
        },
        {
            "campaign_name": "HG | Search | Spring Sale",
            "conversion_action": "Purchase",
            "conversion_date": "2026-05-26",
            "conversion_time": "2026-05-26 17:52:00",
            "conversions": 1,
            "conversion_value": 512.00,
            "gclid": "CjwKCAjw901stu",
        },
    ]

    df = pd.DataFrame(conversions)
    df.to_csv(OUTPUT_DIR / "ads_sample.csv", index=False)
    print(f"Google Ads: {len(conversions)} conversions")


if __name__ == "__main__":
    generate_ga4()
    generate_callrail()
    generate_ads()
    print("Sample data written to", OUTPUT_DIR)
