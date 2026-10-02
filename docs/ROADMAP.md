# AI Cost Monitor — Roadmap

## v1.0.0 (current release)

- [x] Project skeleton, modular architecture (stdlib only, zero dependencies)
- [x] Endpoint configuration via `.env` (multiple OpenAI-compatible providers)
- [x] `probe` command — latency benchmark: TTFB (non-stream) + TTFT (streaming),
      configurable number of runs, `max_tokens=1` to keep probing cost near zero
- [x] `models` command — fetch `/v1/models` catalog with per-model pricing
- [x] `compare` command — side-by-side endpoint comparison table (price + latency)
- [x] Structured logging to `logs/ai-cost-monitor.log`
- [x] Custom exception hierarchy, strict typing, guard clauses
- [x] README in English and Russian

## v1.1.0 (planned)

- [ ] HTML/JSON report export (`--format json|html`)
- [ ] Watch mode: periodic probes with history (SQLite storage)
- [ ] Cost estimator for typical scenarios (chat bot / RAG / coding agent)

## v1.2.0 (ideas)

- [ ] GitHub Actions workflow: nightly probe + badge in README
- [ ] Grafana-friendly Prometheus text endpoint
- [ ] Prompt-cache hit-rate detection

## Maintenance notes

- Every probe request uses `max_tokens=1` by default — cost per run is fractions of a cent.
- API keys are read from environment only; never committed (`.env` is gitignored).
