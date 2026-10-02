"""Endpoint value object: one OpenAI-compatible provider configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoint:
    """A single provider that speaks the OpenAI chat-completions protocol."""

    name: str
    base_url: str
    api_key: str
    referral_url: str | None = None

    def models_url(self) -> str:
        """Full URL of the /v1/models catalog endpoint."""
        return f"{self.base_url.rstrip('/')}/models"

    def chat_completions_url(self) -> str:
        """Full URL of the /v1/chat/completions endpoint."""
        return f"{self.base_url.rstrip('/')}/chat/completions"
