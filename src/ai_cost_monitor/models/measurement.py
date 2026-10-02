"""Measurement and pricing result types."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LatencyMeasurement:
    """Result of one probe run against an endpoint."""

    endpoint_name: str
    model_id: str
    streaming: bool
    first_byte_seconds: float
    total_seconds: float
    status_code: int


@dataclass(frozen=True)
class ModelPricing:
    """Per-million-token pricing extracted from a model catalog entry."""

    model_id: str
    input_per_million_usd: float | None
    output_per_million_usd: float | None
    context_length: int | None
    provider: str | None
    discount_percent: float | None


@dataclass
class EndpointLatencyReport:
    """Aggregated latency statistics for one endpoint and one model."""

    endpoint_name: str
    model_id: str
    runs: int = 0
    non_stream_first_byte: list[float] = field(default_factory=list)
    stream_first_token: list[float] = field(default_factory=list)
    total_seconds: list[float] = field(default_factory=list)
    failed_runs: int = 0
    error_messages: list[str] = field(default_factory=list)
