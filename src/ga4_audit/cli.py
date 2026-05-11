"""Command-line interface for the GA4 attribution audit toolkit."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from ga4_audit import __version__
from ga4_audit.audits.attribution_gaps import run as run_attribution_gaps
from ga4_audit.audits.channel_discrepancy import run as run_channel_discrepancy
from ga4_audit.audits.duplicate_conversions import run as run_duplicate_conversions
from ga4_audit.audits.event_hygiene import run as run_event_hygiene
from ga4_audit.audits.utm_consistency import run as run_utm_consistency
from ga4_audit.config import ConfigError, load_config, validate_config
from ga4_audit.report.renderer import render_report, write_report
from ga4_audit.sources import load_all_data

console = Console()

AUDIT_MODULES = [
    run_duplicate_conversions,
    run_channel_discrepancy,
    run_attribution_gaps,
    run_event_hygiene,
    run_utm_consistency,
]

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = PACKAGE_ROOT / "examples"
SAMPLE_CONFIG = EXAMPLES_DIR / "config.yaml"


def _run_audits(config_path: Path, output: Path, output_format: str) -> None:
    """Execute all audits and write the report."""
    load_dotenv()
    config = load_config(config_path)
    config_dir = str(config_path.parent)

    with console.status("[bold green]Loading data sources..."):
        data = load_all_data(config, config_dir=config_dir)

    with console.status("[bold green]Running audits..."):
        results = [module(data) for module in AUDIT_MODULES]

    content = render_report(config, data, results, output_format=output_format)
    written = write_report(content, output)

    total_issues = sum(r.issue_count for r in results)
    console.print(f"\n[bold green]Report written to[/bold green] {written}")
    console.print(f"Total issues found: [bold]{total_issues}[/bold]")


@click.group()
@click.version_option(version=__version__, prog_name="ga4-audit")
def main() -> None:
    """GA4 Attribution Audit Toolkit.

    Pull GA4 data, cross-reference CallRail and Google Ads exports, and
    surface duplicate conversions, attribution gaps, and channel discrepancies.
    """


@main.command("run")
@click.option(
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to the YAML configuration file.",
)
@click.option(
    "--output",
    "output_path",
    required=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output file path (e.g. report.md or report.html).",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "html"], case_sensitive=False),
    default="markdown",
    help="Report output format.",
)
def run_cmd(config_path: Path, output_path: Path, output_format: str) -> None:
    """Run a full attribution audit and generate a report."""
    try:
        _run_audits(config_path, output_path, output_format)
    except (OSError, ConfigError, FileNotFoundError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        sys.exit(1)


@main.command("sample")
@click.option(
    "--output",
    "output_path",
    default=str(EXAMPLES_DIR / "sample_report.md"),
    show_default=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Where to write the sample report.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "html"], case_sensitive=False),
    default="markdown",
    help="Report output format.",
)
def sample_cmd(output_path: Path, output_format: str) -> None:
    """Run the audit against bundled Harbor Goods sample data."""
    if not SAMPLE_CONFIG.exists():
        console.print(f"[bold red]Sample config not found:[/bold red] {SAMPLE_CONFIG}")
        sys.exit(1)

    console.print("[bold]Running sample audit for Harbor Goods...[/bold]")
    _run_audits(SAMPLE_CONFIG, output_path, output_format)


@main.command("validate-config")
@click.argument(
    "config_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def validate_config_cmd(config_path: Path) -> None:
    """Validate a configuration file without running an audit."""
    is_valid, messages = validate_config(config_path)
    for message in messages:
        if is_valid:
            console.print(f"[green]{message}[/green]")
        else:
            console.print(f"[red]{message}[/red]")
    sys.exit(0 if is_valid else 1)


@main.command("list-conversions")
@click.option(
    "--property-id",
    required=True,
    help="GA4 property numeric ID (e.g. 123456789).",
)
def list_conversions_cmd(property_id: str) -> None:
    """List conversion events for a GA4 property via the Data API."""
    load_dotenv()
    try:
        from ga4_audit.sources.ga4_api import list_conversion_events

        events = list_conversion_events(property_id)
    except (OSError, RuntimeError, ImportError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        sys.exit(1)

    table = Table(title=f"Conversion Events for Property {property_id}")
    table.add_column("Event Name")
    table.add_column("Is Conversion")
    table.add_column("Event Count (30d)")

    for event in events:
        table.add_row(
            event.get("event_name", ""),
            event.get("is_conversion", ""),
            event.get("event_count", ""),
        )

    console.print(table)


if __name__ == "__main__":
    main()
