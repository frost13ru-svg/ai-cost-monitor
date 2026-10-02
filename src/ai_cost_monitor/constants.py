"""Central place for all timeouts, defaults and system strings (no magic numbers)."""

from pathlib import Path

# --- Network ---------------------------------------------------------------
DEFAULT_TIMEOUT_SECONDS: float = 30.0
DEFAULT_RUNS: int = 3
DEFAULT_MAX_TOKENS: int = 1
PROBE_PROMPT: str = "ping"
STREAM_SENTINEL_DONE: str = "data: [DONE]"

# --- Reporting -------------------------------------------------------------
MILLIS_PER_SECOND: float = 1000.0
TOKENS_PER_MILLION: int = 1_000_000

# --- Paths -----------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
LOGS_DIR: Path = PROJECT_ROOT / "logs"
LOG_FILE_NAME: str = "ai-cost-monitor.log"

# --- Env layout ------------------------------------------------------------
ENV_FILE_NAME: str = ".env"
ENV_URL_SUFFIX: str = "__URL"
ENV_KEY_SUFFIX: str = "__KEY"
ENV_REF_SUFFIX: str = "__REF"

# --- Branding (affiliate block shown in CLI output and README) -------------
SPONSOR_REFERRAL_URL: str = "https://cheaperinference.com/?ref=9mQjzQYhrL"
SPONSOR_REFERRAL_NOTE: str = (
    "Want these prices too? Sign up with our referral link: " + SPONSOR_REFERRAL_URL
)

# --- CLI strings -----------------------------------------------------------
CLI_PROBE_COST_WARNING: str = (
    "Note: probes send {runs} tiny request(s) with max_tokens={max_tokens} "
    "to endpoint '{endpoint}' — real but near-zero cost."
)
