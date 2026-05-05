"""Data normalization utilities."""

from __future__ import annotations

import re


def normalize_string(value: object) -> str:
    """Normalize a value to a lowercase trimmed string."""
    if value is None or (isinstance(value, float) and str(value) == "nan"):
        return ""
    return str(value).strip().lower()


def normalize_source_medium(source: object, medium: object) -> tuple[str, str]:
    """Return normalized source and medium tuple."""
    return normalize_string(source), normalize_string(medium)


def canonical_utm_value(value: object) -> str:
    """Return a canonical form for UTM comparison."""
    text = normalize_string(value)
    text = re.sub(r"\s+", "_", text)
    return text


def casing_variants(values: list[str]) -> dict[str, list[str]]:
    """Group values by canonical form to detect casing inconsistencies.

    Args:
        values: List of raw UTM parameter values.

    Returns:
        Dict mapping canonical form to list of observed variants.
    """
    groups: dict[str, set[str]] = {}
    for raw in values:
        if not raw or raw in {"(not set)", "(none)", "nan"}:
            continue
        canonical = canonical_utm_value(raw)
        groups.setdefault(canonical, set()).add(str(raw).strip())
    return {k: sorted(v) for k, v in groups.items() if len(v) > 1}
