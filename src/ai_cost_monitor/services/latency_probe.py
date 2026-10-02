"""Latency probing service: repeated tiny requests, aggregated into a report."""

import logging

from ai_cost_monitor import constants
from ai_cost_monitor.exceptions import ApiRequestError
from ai_cost_monitor.models import Endpoint, EndpointLatencyReport
from ai_cost_monitor.services import api_client

logger = logging.getLogger(__name__)


def build_probe_payload(model_id: str, max_tokens: int) -> dict:
    """Minimal chat payload: one ping, one token — cheapest possible probe."""
    return {
        "model": model_id,
        "messages": [{"role": "user", "content": constants.PROBE_PROMPT}],
        "max_tokens": max_tokens,
        "stream": True,
    }


def probe_latency(
    endpoint: Endpoint,
    model_id: str,
    runs: int,
    max_tokens: int,
    timeout_seconds: float = constants.DEFAULT_TIMEOUT_SECONDS,
) -> EndpointLatencyReport:
    """Run ``runs`` streaming probes and aggregate first-token timings.

    Failures are recorded per-run and do not abort the whole benchmark, so a
    single flaky request never hides the overall picture.
    """
    report = EndpointLatencyReport(endpoint_name=endpoint.name, model_id=model_id)
    payload = build_probe_payload(model_id, max_tokens)

    for run_index in range(1, runs + 1):
        try:
            timing = api_client.stream_first_token(
                endpoint, payload, timeout_seconds=timeout_seconds
            )
            report.stream_first_token.append(timing.total_seconds)
            report.total_seconds.append(timing.total_seconds)
            report.runs += 1
            logger.info(
                "Run %d/%d on '%s': first token in %.2fs",
                run_index,
                runs,
                endpoint.name,
                timing.total_seconds,
            )
        except ApiRequestError as error:
            report.failed_runs += 1
            report.error_messages.append(str(error))
            logger.error("Run %d/%d failed: %s", run_index, runs, error)

    return report
