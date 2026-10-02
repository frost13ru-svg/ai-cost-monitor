"""Command-line interface: argument parsing and dispatch into the app layer."""

import argparse
import sys

from ai_cost_monitor import __version__, app, constants
from ai_cost_monitor.utils.logger import setup_logging

_DESCRIPTION = (
    "Benchmark latency (TTFB/TTFT) and pricing across OpenAI-compatible AI providers."
)
_EPILOG = f"Sponsor this project's pricing knowledge: {constants.SPONSOR_REFERRAL_URL}"


def build_parser() -> argparse.ArgumentParser:
    """Assemble the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="ai-cost-monitor", description=_DESCRIPTION, epilog=_EPILOG
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="increase log verbosity"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    probe_parser = subparsers.add_parser(
        "probe", help="measure time-to-first-token for one endpoint/model"
    )
    probe_parser.add_argument("--endpoint", help="endpoint name from .env (NAME__URL)")
    probe_parser.add_argument("--model", required=True, help="model id, e.g. gpt-6-luna")
    probe_parser.add_argument(
        "--runs", type=int, default=constants.DEFAULT_RUNS, help="number of probe runs"
    )
    probe_parser.add_argument(
        "--max-tokens",
        type=int,
        default=constants.DEFAULT_MAX_TOKENS,
        help="max_tokens per probe (default: 1 — near-zero cost)",
    )
    probe_parser.add_argument(
        "--timeout", type=float, default=constants.DEFAULT_TIMEOUT_SECONDS, help="request timeout, s"
    )

    models_parser = subparsers.add_parser(
        "models", help="list model catalog with per-million pricing"
    )
    models_parser.add_argument("--endpoint", help="endpoint name from .env (NAME__URL)")
    models_parser.add_argument(
        "--limit", type=int, default=20, help="how many cheapest models to show"
    )

    return parser


def dispatch(args: argparse.Namespace) -> int:
    """Route parsed arguments into the corresponding app-layer workflow."""
    if args.command == "probe":
        return app.run_cli_safely(
            lambda: app.run_probe(
                endpoint_name=args.endpoint,
                model_id=args.model,
                runs=args.runs,
                max_tokens=args.max_tokens,
                timeout_seconds=args.timeout,
            )
        )
    if args.command == "models":
        return app.run_cli_safely(
            lambda: app.run_models(endpoint_name=args.endpoint, limit=args.limit)
        )
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 2


def main() -> int:
    """CLI entry point."""
    args = build_parser().parse_args()
    setup_logging(args.verbose)
    return dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())
