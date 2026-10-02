"""Low-level HTTP client for OpenAI-compatible APIs.

Uses only the standard library (``http.client``) so we can measure time-to-
first-byte precisely (``getresponse()`` returns exactly after the response
headers arrive) and read SSE streams incrementally.
"""

import json
import logging
import ssl
import time
from dataclasses import dataclass
from http.client import HTTPConnection, HTTPSConnection, HTTPResponse
from urllib.parse import urlparse

from ai_cost_monitor import constants
from ai_cost_monitor.exceptions import ApiRequestError
from ai_cost_monitor.models import Endpoint

logger = logging.getLogger(__name__)

_SSL_CONTEXT = ssl.create_default_context()
_DEFAULT_PORTS: dict[str, int] = {"https": 443, "http": 80}


@dataclass(frozen=True)
class HttpResponseTiming:
    """Raw timing and payload of a completed HTTP round-trip."""

    status_code: int
    first_byte_seconds: float
    total_seconds: float
    body: bytes


def request_json(
    endpoint: Endpoint,
    method: str,
    url: str,
    payload: dict | None = None,
    timeout_seconds: float = constants.DEFAULT_TIMEOUT_SECONDS,
) -> HttpResponseTiming:
    """Perform an HTTP request and return status, timings and the raw body."""
    response = _send_request(endpoint, method, url, payload, timeout_seconds)
    start_of_body = time.perf_counter()
    body = response.read()
    total_seconds = time.perf_counter() - start_of_body + response.elapsed
    _close_quietly(response)
    return HttpResponseTiming(
        status_code=response.status,
        first_byte_seconds=response.elapsed,
        total_seconds=total_seconds,
        body=body,
    )


def stream_first_token(
    endpoint: Endpoint,
    payload: dict,
    timeout_seconds: float = constants.DEFAULT_TIMEOUT_SECONDS,
) -> HttpResponseTiming:
    """Stream a chat completion (SSE) and stop right after the first content token.

    Reading stops as soon as one token arrives — this keeps the probe cost at
    the minimum the provider bills for while still measuring real TTFT.
    """
    response = _send_request(
        endpoint, "POST", endpoint.chat_completions_url(), payload, timeout_seconds
    )

    total_elapsed = response.elapsed
    try:
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line.startswith("data: ") or line == constants.STREAM_SENTINEL_DONE:
                continue
            chunk = json.loads(line[len("data: ") :])
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta", {})
            if delta.get("content"):
                total_elapsed = time.perf_counter() - response._start  # type: ignore[attr-defined]
                break
    finally:
        _close_quietly(response)

    return HttpResponseTiming(
        status_code=response.status,
        first_byte_seconds=response.elapsed,
        total_seconds=total_elapsed,
        body=b"",
    )


def _close_quietly(response: HTTPResponse) -> None:
    """Close the underlying socket; failures during teardown are irrelevant."""
    try:
        response.close()
    except OSError as error:
        logger.debug("Response close failed (ignored): %s", error)


def _send_request(
    endpoint: Endpoint,
    method: str,
    url: str,
    payload: dict | None,
    timeout_seconds: float,
) -> HTTPResponse:
    """Open a connection, send the request and return the response object.

    ``response.elapsed`` carries seconds-to-first-byte (headers received).
    """
    parsed = urlparse(url)
    if parsed.scheme not in _DEFAULT_PORTS:
        raise ApiRequestError(
            endpoint.name, url, None, f"unsupported URL scheme: {parsed.scheme!r}"
        )

    headers = {
        "Authorization": f"Bearer {endpoint.api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream" if payload is not None else "application/json",
    }
    body = json.dumps(payload).encode("utf-8") if payload is not None else None

    logger.debug("HTTP %s %s (payload=%s)", method, url, body is not None)
    start = time.perf_counter()
    try:
        connection = _open_connection(parsed, timeout_seconds)
        connection.request(method, parsed.path or "/", body=body, headers=headers)
        response = connection.getresponse()
        response.elapsed = time.perf_counter() - start  # type: ignore[attr-defined]
        response._start = start  # type: ignore[attr-defined]
        return response
    except (OSError, ssl.SSLError) as error:
        raise ApiRequestError(endpoint.name, url, None, f"network error: {error}") from error


def _open_connection(parsed, timeout_seconds: float) -> HTTPConnection:  # type: ignore[no-untyped-def]
    """Create an HTTP(S) connection to the parsed URL target."""
    port = parsed.port or _DEFAULT_PORTS[parsed.scheme]
    if parsed.scheme == "https":
        return HTTPSConnection(
            parsed.hostname, port, timeout=timeout_seconds, context=_SSL_CONTEXT
        )
    return HTTPConnection(parsed.hostname, port, timeout=timeout_seconds)
