"""Model catalog service: fetch /v1/models and extract pricing details."""

import json
import logging
from decimal import Decimal, InvalidOperation

from ai_cost_monitor import constants
from ai_cost_monitor.exceptions import ApiRequestError
from ai_cost_monitor.models import Endpoint, ModelPricing
from ai_cost_monitor.services import api_client

logger = logging.getLogger(__name__)


def fetch_pricing_catalog(endpoint: Endpoint) -> list[ModelPricing]:
    """Download the model catalog and map raw entries into ``ModelPricing``.

    Broken or non-standard entries are skipped with a warning instead of
    failing the whole catalog fetch.
    """
    timing = api_client.request_json(endpoint, "GET", endpoint.models_url())
    if timing.status_code != 200:
        raise ApiRequestError(
            endpoint.name,
            endpoint.models_url(),
            timing.status_code,
            timing.body.decode("utf-8", errors="replace")[:200],
        )

    try:
        catalog = json.loads(timing.body)
    except json.JSONDecodeError as error:
        raise ApiRequestError(
            endpoint.name, endpoint.models_url(), timing.status_code, f"invalid JSON: {error}"
        ) from error

    pricing_entries: list[ModelPricing] = []
    for raw_model in catalog.get("data", []):
        parsed = _parse_model_entry(raw_model)
        if parsed is not None:
            pricing_entries.append(parsed)
    logger.info("Fetched %d priced models from '%s'", len(pricing_entries), endpoint.name)
    return pricing_entries


def _parse_model_entry(raw_model: dict) -> ModelPricing | None:
    """Extract pricing from one catalog entry; return None when unusable."""
    model_id = raw_model.get("id")
    if not isinstance(model_id, str):
        logger.warning("Skipping catalog entry without an id: %r", raw_model)
        return None

    pricing = raw_model.get("pricing") or {}
    return ModelPricing(
        model_id=model_id,
        input_per_million_usd=_parse_decimal(pricing.get("input_per_million")),
        output_per_million_usd=_parse_decimal(pricing.get("output_per_million")),
        context_length=_parse_optional_int(raw_model.get("context_length")),
        provider=raw_model.get("provider"),
        discount_percent=_parse_decimal(pricing.get("discount_percent")),
    )


def _parse_decimal(value) -> float | None:  # type: ignore[no-untyped-def]
    """Convert a possibly-string decimal to float, tolerating junk."""
    if value is None:
        return None
    try:
        return float(Decimal(str(value)))
    except (InvalidOperation, ValueError):
        return None


def _parse_optional_int(value) -> int | None:  # type: ignore[no-untyped-def]
    """Convert a possibly-string integer to int, tolerating junk."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def estimate_request_cost(pricing: ModelPricing, input_tokens: int, output_tokens: int) -> float | None:
    """Estimate the USD cost of one request, or None when prices are unknown."""
    if pricing.input_per_million_usd is None or pricing.output_per_million_usd is None:
        return None
    input_cost = (input_tokens / constants.TOKENS_PER_MILLION) * pricing.input_per_million_usd
    output_cost = (output_tokens / constants.TOKENS_PER_MILLION) * pricing.output_per_million_usd
    return input_cost + output_cost
