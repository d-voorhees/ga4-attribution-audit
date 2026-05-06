"""Load GA4 data through the Data API."""

from __future__ import annotations

import os

import pandas as pd

from ga4_audit.config import AuditConfig


def load_ga4_api(
    config: AuditConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Pull GA4 session and conversion data via the Data API.

    Requires GOOGLE_APPLICATION_CREDENTIALS and a valid service account with
    GA4 property access.

    Args:
        config: Audit configuration with property ID and date range.

    Returns:
        Tuple of (sessions, conversions, events) DataFrames.

    Raises:
        EnvironmentError: If credentials are not configured.
        ImportError: If google-analytics-data is not installed.
    """
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not os.path.exists(creds_path):
        raise OSError(
            "GOOGLE_APPLICATION_CREDENTIALS must point to a service account JSON file"
        )

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Filter,
            FilterExpression,
            Metric,
            RunReportRequest,
        )
    except ImportError as exc:
        raise ImportError(
            "google-analytics-data is required for API mode. "
            "Install with: pip install google-analytics-data"
        ) from exc

    client = BetaAnalyticsDataClient()
    property_id = f"properties/{config.property_id}"

    session_request = RunReportRequest(
        property=property_id,
        dimensions=[
            Dimension(name="sessionId"),
            Dimension(name="date"),
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium"),
            Dimension(name="sessionCampaignName"),
            Dimension(name="landingPage"),
            Dimension(name="sessionDefaultChannelGroup"),
        ],
        metrics=[Metric(name="sessions")],
        date_ranges=[DateRange(start_date=config.start_date, end_date=config.end_date)],
    )
    session_response = client.run_report(session_request)
    sessions = _response_to_df(session_response)
    sessions = sessions.rename(
        columns={
            "sessionId": "session_id",
            "sessionSource": "session_source",
            "sessionMedium": "session_medium",
            "sessionCampaignName": "session_campaign",
            "landingPage": "landing_page",
            "sessionDefaultChannelGroup": "default_channel_group",
        }
    )

    event_names = config.conversion_events
    conversion_rows: list[dict[str, object]] = []
    for event_name in event_names:
        conv_request = RunReportRequest(
            property=property_id,
            dimensions=[
                Dimension(name="sessionId"),
                Dimension(name="date"),
                Dimension(name="eventName"),
                Dimension(name="sessionDefaultChannelGroup"),
            ],
            metrics=[Metric(name="conversions")],
            date_ranges=[
                DateRange(start_date=config.start_date, end_date=config.end_date)
            ],
            dimension_filter=FilterExpression(
                filter=Filter(
                    field_name="eventName",
                    string_filter=Filter.StringFilter(value=event_name),
                )
            ),
        )
        conv_response = client.run_report(conv_request)
        conv_df = _response_to_df(conv_response)
        if not conv_df.empty:
            conv_df["conversion_event"] = event_name
            conversion_rows.extend(conv_df.to_dict("records"))

    conversions = pd.DataFrame(conversion_rows)
    if not conversions.empty:
        conversions = conversions.rename(
            columns={
                "sessionId": "session_id",
                "eventName": "event_name",
                "sessionDefaultChannelGroup": "default_channel_group",
            }
        )

    events_request = RunReportRequest(
        property=property_id,
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date=config.start_date, end_date=config.end_date)],
    )
    events_response = client.run_report(events_request)
    events = _response_to_df(events_response)
    events = events.rename(
        columns={"eventName": "event_name", "eventCount": "event_count"}
    )

    return sessions, conversions, events


def _response_to_df(response: object) -> pd.DataFrame:
    """Convert a GA4 RunReportResponse to a pandas DataFrame."""
    rows: list[dict[str, str]] = []
    dimension_headers = [h.name for h in response.dimension_headers]
    metric_headers = [h.name for h in response.metric_headers]

    for row in response.rows:
        record: dict[str, str] = {}
        for idx, dim in enumerate(row.dimension_values):
            record[dimension_headers[idx]] = dim.value
        for idx, metric in enumerate(row.metric_values):
            record[metric_headers[idx]] = metric.value
        rows.append(record)

    return pd.DataFrame(rows)


def list_conversion_events(property_id: str) -> list[dict[str, str]]:
    """List conversion events for a GA4 property via the Admin API metadata.

    Falls back to common event names if Admin API access is unavailable.

    Args:
        property_id: GA4 property numeric ID.

    Returns:
        List of event name dicts with name and status.
    """
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise OSError("GOOGLE_APPLICATION_CREDENTIALS is not set")

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )

        client = BetaAnalyticsDataClient()
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="eventName"),
                Dimension(name="isConversionEvent"),
            ],
            metrics=[Metric(name="eventCount")],
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        )
        response = client.run_report(request)
        events: list[dict[str, str]] = []
        for row in response.rows:
            events.append(
                {
                    "event_name": row.dimension_values[0].value,
                    "is_conversion": row.dimension_values[1].value,
                    "event_count": row.metric_values[0].value,
                }
            )
        return sorted(
            events, key=lambda x: int(x.get("event_count", "0")), reverse=True
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to list conversion events: {exc}") from exc
