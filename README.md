# AI Cost Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/frost13ru-svg/ai-cost-monitor)](https://github.com/frost13ru-svg/ai-cost-monitor/releases)
[![Python](https://img.shields.io/badge/python-3.10%2B-informational)](pyproject.toml)
[![Dependencies](https://img.shields.io/badge/dependencies-0-success)](#features)

**EN** · [RU version](README.ru.md)

A zero-dependency CLI that benchmarks **latency (TTFB / time-to-first-token)** and
**pricing** across OpenAI-compatible AI API providers. Know exactly which provider
and model responds fastest and costs least — before you wire it into production.

## Why

AI API marketplaces often have unstable time-to-first-token (TTFT): the same model
can answer in 1.5 s or hang for 18 s depending on the provider's cold-worker queue.
This tool measures it for you with tiny, near-free probe requests (`max_tokens=1`).

## Features

- `probe` — repeated streaming requests to one endpoint/model, reports best / median / worst TTFT
- `models` — fetch a provider's `/v1/models` catalog with per-million pricing and discounts
- **Zero dependencies** — pure Python standard library (3.10+)
- Multiple endpoints configured side by side via a single `.env` file
- Structured logging to `logs/ai-cost-monitor.log`

## Quick start

```bash
git clone https://github.com/frost13ru-svg/ai-cost-monitor.git
cd ai-cost-monitor
cp .env.example .env      # fill in your URL + KEY
./run.sh probe --model gpt-6-luna --runs 3
```

Or without the launcher:

```bash
PYTHONPATH=src python3 -m ai_cost_monitor probe --model gpt-6-luna
PYTHONPATH=src python3 -m ai_cost_monitor models --limit 15
```

Or install properly:

```bash
pip install -e .
ai-cost-monitor probe --model gpt-6-luna
```

## Configuration

Every endpoint is one block in `.env`:

```ini
CHEAPERINFERENCE__URL=https://api.cheaperinference.com/v1
CHEAPERINFERENCE__KEY=ci_live_...
CHEAPERINFERENCE__REF=https://cheaperinference.com/?ref=9mQjzQYhrL   # optional, shown in reports
```

Environment variables override the file — handy for CI.

## Example output

```
[cheaperinference] model=gpt-6-luna
  Successful runs: 3 (failed: 0)
  First token — best: 1464 ms | median: 4190 ms | worst: 5 s

💡 Want these prices too? Sign up with our referral link: https://cheaperinference.com/?ref=9mQjzQYhrL
```

## Cost safety

Probes send `max_tokens=1` with a one-word prompt. At marketplaces like
CheaperInference a full benchmark run costs fractions of a cent. The tool prints
a warning before spending anything.

## Architecture

```
src/ai_cost_monitor/
├── cli.py            # argument parsing and dispatch
├── app.py            # workflow orchestration
├── config.py         # .env parsing -> Endpoint objects
├── constants.py      # all timeouts/defaults/system strings
├── exceptions.py     # custom error hierarchy
├── models/           # domain types (Endpoint, LatencyMeasurement, ModelPricing)
├── services/         # api_client, latency_probe, model_catalog
├── output/           # console reporters
└── utils/            # logger, formatting
```

## License

MIT

---

💡 **Powered by [Cheaper Inference](https://cheaperinference.com/?ref=9mQjzQYhrL)** —
OpenAI-compatible marketplace with up to 80% off list prices across OpenAI,
Anthropic, DeepSeek, Z.ai and more. Fund from $5, no monthly commitment.
Signing up through the link supports this project.
