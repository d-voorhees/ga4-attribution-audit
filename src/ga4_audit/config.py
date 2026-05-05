"""Configuration loading and validation for GA4 attribution audits."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SourceConfig:
    """Configuration for a single data source."""

    mode: str  # "csv" or "api"
    path: str | None = None
    customer_id: str | None = None


@dataclass
class AuditConfig:
    """Validated audit configuration."""

    property_id: str
    date_range: dict[str, str]
    conversion_events: list[str]
    channel_groupings: list[str]
    duplicate_window_minutes: int = 5
    attribution_window_days: int = 30
    high_value_landing_page_threshold: int = 50
    suspicious_event_count_threshold: int = 100
    sources: dict[str, SourceConfig] = field(default_factory=dict)
    client_name: str = "Client"
    utm_standard_mediums: list[str] = field(
        default_factory=lambda: [
            "cpc",
            "ppc",
            "paid",
            "organic",
            "email",
            "referral",
            "social",
            "display",
            "affiliate",
            "none",
            "(none)",
            "(not set)",
        ]
    )

    @property
    def start_date(self) -> str:
        """Return the audit start date."""
        return self.date_range["start"]

    @property
    def end_date(self) -> str:
        """Return the audit end date."""
        return self.date_range["end"]


class ConfigError(Exception):
    """Raised when configuration is invalid."""


def _parse_source(raw: dict[str, Any]) -> SourceConfig:
    """Parse a source block from YAML."""
    mode = raw.get("mode", "csv")
    if mode not in {"csv", "api"}:
        raise ConfigError(f"Invalid source mode: {mode}. Use 'csv' or 'api'.")
    return SourceConfig(
        mode=mode,
        path=raw.get("path"),
        customer_id=raw.get("customer_id"),
    )


def load_config(path: str | Path) -> AuditConfig:
    """Load and parse a YAML configuration file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Parsed AuditConfig instance.

    Raises:
        ConfigError: If the file is missing required fields or has invalid values.
        FileNotFoundError: If the config file does not exist.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open(encoding="utf-8") as handle:
        raw: dict[str, Any] = yaml.safe_load(handle) or {}

    errors: list[str] = []

    property_id = raw.get("property_id")
    if not property_id:
        errors.append("property_id is required")

    date_range = raw.get("date_range", {})
    if not date_range.get("start") or not date_range.get("end"):
        errors.append("date_range.start and date_range.end are required")

    conversion_events = raw.get("conversion_events", [])
    if not conversion_events:
        errors.append("conversion_events must contain at least one event name")

    channel_groupings = raw.get("channel_groupings", [])
    if not channel_groupings:
        errors.append("channel_groupings must contain at least one grouping name")

    sources_raw = raw.get("sources", {})
    sources: dict[str, SourceConfig] = {}
    for name, source_data in sources_raw.items():
        try:
            sources[name] = _parse_source(source_data)
        except ConfigError as exc:
            errors.append(str(exc))

    for source_name in ("ga4", "callrail", "google_ads"):
        if source_name not in sources:
            errors.append(f"sources.{source_name} is required")

    duplicate_window = raw.get("duplicate_window_minutes", 5)
    if not isinstance(duplicate_window, int) or duplicate_window < 1:
        errors.append("duplicate_window_minutes must be a positive integer")

    if errors:
        raise ConfigError("Configuration errors:\n  - " + "\n  - ".join(errors))

    return AuditConfig(
        property_id=str(property_id),
        date_range={"start": str(date_range["start"]), "end": str(date_range["end"])},
        conversion_events=list(conversion_events),
        channel_groupings=list(channel_groupings),
        duplicate_window_minutes=int(duplicate_window),
        attribution_window_days=int(raw.get("attribution_window_days", 30)),
        high_value_landing_page_threshold=int(
            raw.get("high_value_landing_page_threshold", 50)
        ),
        suspicious_event_count_threshold=int(
            raw.get("suspicious_event_count_threshold", 100)
        ),
        sources=sources,
        client_name=str(raw.get("client_name", "Client")),
        utm_standard_mediums=list(
            raw.get(
                "utm_standard_mediums",
                [
                    "cpc",
                    "ppc",
                    "paid",
                    "organic",
                    "email",
                    "referral",
                    "social",
                    "display",
                    "affiliate",
                    "none",
                    "(none)",
                    "(not set)",
                ],
            )
        ),
    )


def validate_config(path: str | Path) -> tuple[bool, list[str]]:
    """Validate a configuration file without running an audit.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Tuple of (is_valid, list of error messages).
    """
    messages: list[str] = []
    try:
        config = load_config(path)
    except FileNotFoundError as exc:
        return False, [str(exc)]
    except ConfigError as exc:
        return False, [str(exc)]
    except yaml.YAMLError as exc:
        return False, [f"YAML parse error: {exc}"]

    config_dir = Path(path).parent.resolve()

    for name, source in config.sources.items():
        if source.mode == "csv" and source.path:
            csv_path = (config_dir / source.path).resolve()
            if not csv_path.exists():
                messages.append(f"sources.{name}.path not found: {csv_path}")
        elif source.mode == "api" and name == "google_ads" and not source.customer_id:
            messages.append("sources.google_ads.customer_id required for api mode")

    if messages:
        return False, messages

    messages.append(
        f"Config valid: property {config.property_id}, "
        f"{config.start_date} to {config.end_date}, "
        f"{len(config.conversion_events)} conversion events"
    )
    return True, messages
