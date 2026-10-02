"""Application layer: wires configuration, services and presentation together."""

import logging

from ai_cost_monitor import constants
from ai_cost_monitor.config import load_dotenv, load_endpoints, select_endpoint
from ai_cost_monitor.exceptions import CostMonitorError
from ai_cost_monitor.output import console_reporter
from ai_cost_monitor.services import latency_probe, model_catalog

logger = logging.getLogger(__name__)


def run_probe(
    endpoint_name: str | None,
    model_id: str,
    runs: int,
    max_tokens: int,
    timeout_seconds: float,
) -> int:
    """Execute the probe workflow for a single endpoint/model pair."""
    load_dotenv()
    endpoint = select_endpoint(load_endpoints(), endpoint_name)
    print(constants.CLI_PROBE_COST_WARNING.format(
        runs=runs, max_tokens=max_tokens, endpoint=endpoint.name
    ))

    report = latency_probe.probe_latency(
        endpoint=endpoint,
        model_id=model_id,
        runs=runs,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
    )
    console_reporter.print_latency_report(report)
    console_reporter.print_referral_footer()
    return 0 if report.runs > 0 else 1


def run_models(endpoint_name: str | None, limit: int) -> int:
    """Execute the pricing-catalog workflow for a single endpoint."""
    load_dotenv()
    endpoint = select_endpoint(load_endpoints(), endpoint_name)

    catalog = model_catalog.fetch_pricing_catalog(endpoint)
    console_reporter.print_pricing_table(catalog, limit=limit)
    console_reporter.print_referral_footer()
    return 0


def run_cli_safely(main_action) -> int:  # type: ignore[no-untyped-def]
    """Catch domain errors, log them and map to a non-zero exit code."""
    try:
        return main_action()
    except CostMonitorError as error:
        logger.error("Operation failed: %s", error)
        print(f"Error: {error}")
        return 2
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
