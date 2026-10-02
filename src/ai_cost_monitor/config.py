"""Configuration loading: parses `.env` (NAME__URL / NAME__KEY / NAME__REF) into Endpoint objects."""

import logging
import os
from pathlib import Path

from ai_cost_monitor import constants
from ai_cost_monitor.exceptions import ConfigurationError
from ai_cost_monitor.models import Endpoint

logger = logging.getLogger(__name__)


def load_dotenv(env_file: Path | None = None) -> None:
    """Populate ``os.environ`` from a project-local `.env` file.

    Existing environment variables always win over the file, so users can
    override values per invocation without editing `.env`.
    """
    env_path = env_file or (constants.PROJECT_ROOT / constants.ENV_FILE_NAME)
    if not env_path.is_file():
        logger.debug("No .env file found at %s — relying on process environment", env_path)
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if _is_skippable_line(line):
            continue
        key, separator, value = line.partition("=")
        if separator == "" or not key:
            logger.warning("Skipping malformed .env line: %r", raw_line)
            continue
        normalized_key = key.strip()
        if normalized_key not in os.environ:
            os.environ[normalized_key] = value.strip().strip("'\"")
    logger.info("Loaded environment from %s", env_path)


def _is_skippable_line(line: str) -> bool:
    """Blank lines and comments carry no configuration."""
    return line == "" or line.startswith("#")


def load_endpoints() -> dict[str, Endpoint]:
    """Collect all configured endpoints from environment variables.

    A block is valid when both ``NAME__URL`` and ``NAME__KEY`` are present;
    ``NAME__REF`` is optional and only used for display.

    Raises:
        ConfigurationError: if no valid endpoint block exists at all.
    """
    env = os.environ
    endpoint_names = sorted(
        {
            key[: -len(constants.ENV_URL_SUFFIX)]
            for key in env
            if key.endswith(constants.ENV_URL_SUFFIX)
        }
    )

    endpoints: dict[str, Endpoint] = {}
    for name in endpoint_names:
        base_url = env.get(f"{name}{constants.ENV_URL_SUFFIX}", "").strip()
        api_key = env.get(f"{name}{constants.ENV_KEY_SUFFIX}", "").strip()
        if not base_url or not api_key:
            logger.warning(
                "Endpoint '%s' is incomplete: URL or KEY missing — skipped", name
            )
            continue
        referral_url = env.get(f"{name}{constants.ENV_REF_SUFFIX}", "").strip() or None
        endpoints[name] = Endpoint(
            name=name.lower(),
            base_url=base_url,
            api_key=api_key,
            referral_url=referral_url,
        )
        logger.info("Configured endpoint '%s' -> %s", name, base_url)

    if not endpoints:
        raise ConfigurationError(
            "No usable endpoints configured. Copy .env.example to .env and fill "
            "in NAME__URL + NAME__KEY, or export the variables directly."
        )
    return endpoints


def select_endpoint(endpoints: dict[str, Endpoint], requested_name: str | None) -> Endpoint:
    """Return the requested endpoint, or the single configured one, or fail fast."""
    if requested_name is not None:
        normalized = requested_name.lower()
        if normalized not in endpoints:
            available = ", ".join(sorted(endpoints)) or "(none)"
            raise ConfigurationError(
                f"Unknown endpoint '{requested_name}'. Available: {available}"
            )
        return endpoints[normalized]

    if len(endpoints) == 1:
        return next(iter(endpoints.values()))

    available = ", ".join(sorted(endpoints))
    raise ConfigurationError(
        f"Multiple endpoints configured ({available}) — pass --endpoint explicitly."
    )
