"""Custom exception hierarchy for precise failure handling."""


class CostMonitorError(Exception):
    """Base error for every failure raised by the application."""


class ConfigurationError(CostMonitorError):
    """Raised when .env / environment configuration is missing or malformed."""


class ApiRequestError(CostMonitorError):
    """Raised when an HTTP request to a provider fails (network, status, auth)."""

    def __init__(self, endpoint_name: str, url: str, status_code: int | None, detail: str) -> None:
        self.endpoint_name = endpoint_name
        self.url = url
        self.status_code = status_code
        self.detail = detail
        super().__init__(
            f"[{endpoint_name}] request to {url} failed "
            f"(status={status_code if status_code is not None else 'n/a'}): {detail}"
        )


class ProbeError(CostMonitorError):
    """Raised when a latency probe cannot produce a measurement."""
