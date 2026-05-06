"""Load Google Ads data through the Ads API."""

from __future__ import annotations

import os

import pandas as pd

from ga4_audit.config import AuditConfig


def load_ads_api(config: AuditConfig) -> pd.DataFrame:
    """Pull Google Ads conversion data via the Google Ads API.

    Requires GOOGLE_ADS_* environment variables.

    Args:
        config: Audit configuration with customer ID in sources.google_ads.

    Returns:
        DataFrame with conversion records.

    Raises:
        EnvironmentError: If required credentials are missing.
    """
    required = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
    ]
    missing = [var for var in required if not os.environ.get(var)]
    if missing:
        raise OSError(f"Missing Google Ads env vars: {', '.join(missing)}")

    customer_id = config.sources["google_ads"].customer_id or os.environ.get(
        "GOOGLE_ADS_CUSTOMER_ID", ""
    )
    if not customer_id:
        raise OSError("Google Ads customer_id required in config or env")

    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError as exc:
        raise ImportError(
            "google-ads is required for API mode. Install with: pip install google-ads"
        ) from exc

    client = GoogleAdsClient.load_from_dict(
        {
            "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
            "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
            "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
            "login_customer_id": os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            "use_proto_plus": True,
        }
    )

    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            campaign.name,
            segments.conversion_action_name,
            segments.date,
            metrics.conversions,
            metrics.conversions_value,
            click_view.gclid
        FROM campaign
        WHERE segments.date BETWEEN '{config.start_date}' AND '{config.end_date}'
          AND metrics.conversions > 0
    """

    rows: list[dict[str, object]] = []
    response = ga_service.search(customer_id=customer_id.replace("-", ""), query=query)
    for row in response:
        rows.append(
            {
                "campaign_name": row.campaign.name,
                "conversion_action": row.segments.conversion_action_name,
                "conversion_date": row.segments.date,
                "conversion_time": row.segments.date,
                "conversions": row.metrics.conversions,
                "conversion_value": row.metrics.conversions_value,
                "gclid": getattr(row.click_view, "gclid", ""),
            }
        )

    return pd.DataFrame(rows)
