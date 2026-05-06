"""Data source loaders for GA4, CallRail, and Google Ads."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ga4_audit.config import AuditConfig


@dataclass
class AuditData:
    """Container for all loaded audit datasets."""

    ga4_sessions: pd.DataFrame
    ga4_conversions: pd.DataFrame
    ga4_events: pd.DataFrame
    callrail: pd.DataFrame
    google_ads: pd.DataFrame
    config: AuditConfig
    source_modes: dict[str, str]


def load_all_data(config: AuditConfig, config_dir: str | None = None) -> AuditData:
    """Load all data sources according to configuration.

    Args:
        config: Validated audit configuration.
        config_dir: Directory containing the config file for relative CSV paths.

    Returns:
        AuditData with all loaded frames.
    """
    from ga4_audit.sources.ads_api import load_ads_api
    from ga4_audit.sources.ads_csv import load_ads_csv
    from ga4_audit.sources.callrail_csv import load_callrail_csv
    from ga4_audit.sources.ga4_api import load_ga4_api
    from ga4_audit.sources.ga4_csv import load_ga4_csv

    base = config_dir or "."
    source_modes: dict[str, str] = {}

    ga4_source = config.sources["ga4"]
    source_modes["ga4"] = ga4_source.mode
    if ga4_source.mode == "api":
        ga4_sessions, ga4_conversions, ga4_events = load_ga4_api(config)
    else:
        path = ga4_source.path or ""
        ga4_sessions, ga4_conversions, ga4_events = load_ga4_csv(
            f"{base}/{path}" if not path.startswith("/") else path,
            config,
        )

    callrail_source = config.sources["callrail"]
    source_modes["callrail"] = callrail_source.mode
    callrail_path = callrail_source.path or ""
    callrail = load_callrail_csv(
        f"{base}/{callrail_path}"
        if not callrail_path.startswith("/")
        else callrail_path
    )

    ads_source = config.sources["google_ads"]
    source_modes["google_ads"] = ads_source.mode
    if ads_source.mode == "api":
        google_ads = load_ads_api(config)
    else:
        ads_path = ads_source.path or ""
        google_ads = load_ads_csv(
            f"{base}/{ads_path}" if not ads_path.startswith("/") else ads_path
        )

    return AuditData(
        ga4_sessions=ga4_sessions,
        ga4_conversions=ga4_conversions,
        ga4_events=ga4_events,
        callrail=callrail,
        google_ads=google_ads,
        config=config,
        source_modes=source_modes,
    )
