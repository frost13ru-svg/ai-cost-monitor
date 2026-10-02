"""Console reporters: latency and pricing tables plus the referral footer."""

import logging
from statistics import median

from ai_cost_monitor import constants
from ai_cost_monitor.models import EndpointLatencyReport, ModelPricing
from ai_cost_monitor.utils.formatting import (
    format_percent,
    format_seconds,
    format_usd,
    render_table,
)

logger = logging.getLogger(__name__)


def print_referral_footer() -> None:
    """Print the referral block — the only advertising surface in the CLI."""
    print()
    print(f"💡 {constants.SPONSOR_REFERRAL_NOTE}")


def print_latency_report(report: EndpointLatencyReport) -> None:
    """Print one endpoint's aggregated latency statistics."""
    header = f"[{report.endpoint_name}] model={report.model_id}"
    print(f"\n{header}")

    if not report.stream_first_token:
        print("  No successful runs.")
        for message in report.error_messages:
            print(f"  ✗ {message}")
        return

    best = min(report.stream_first_token)
    median_value = median(report.stream_first_token)
    worst = max(report.stream_first_token)
    print(f"  Successful runs: {report.runs} (failed: {report.failed_runs})")
    print(f"  First token — best: {format_seconds(best)} | median: "
          f"{format_seconds(median_value)} | worst: {format_seconds(worst)}")


def print_pricing_table(entries: list[ModelPricing], limit: int) -> None:
    """Print the cheapest models sorted by blended output price."""
    priced = [entry for entry in entries if entry.output_per_million_usd is not None]
    priced.sort(key=lambda entry: entry.output_per_million_usd or 0.0)
    selected = priced[:limit]

    headers = ["model", "input /1M", "output /1M", "discount", "ctx"]
    rows = [
        [
            entry.model_id,
            format_usd(entry.input_per_million_usd),
            format_usd(entry.output_per_million_usd),
            format_percent(entry.discount_percent),
            str(entry.context_length) if entry.context_length else "n/a",
        ]
        for entry in selected
    ]
    print(render_table(headers, rows))
    if not selected:
        print("No models expose per-million pricing in this catalog.")
