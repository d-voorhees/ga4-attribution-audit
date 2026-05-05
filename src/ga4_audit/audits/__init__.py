"""Shared audit result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditResult:
    """Standardized output from an audit module.

    Attributes:
        name: Human-readable audit name.
        summary: Plain-English summary for report readers.
        findings: List of finding records (dicts) for tabular display.
        severity: Overall severity: critical, warning, info, or pass.
        methodology: Explanation of how the check works.
        issue_count: Number of issues flagged.
    """

    name: str
    summary: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    severity: str = "info"
    methodology: str = ""
    issue_count: int = 0

    def __post_init__(self) -> None:
        if self.issue_count == 0 and self.findings:
            self.issue_count = len(self.findings)
