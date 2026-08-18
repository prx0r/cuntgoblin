# EndpointTruth — MVP

> Continuously determine what an actual LLM serving endpoint can do right now.
> (VentureLab PRODUCT 1 — specs/endpointtruth/architecture.md)

Not model benchmarking. Not provider reviews. The unit of truth is
`model checkpoint × serving provider × concrete endpoint/deployment × region × time`.

## What this build is

A small, independently shippable product with a brutal MVP boundary:

```
collect reality
   ↓
store immutable observations
   ↓
extract assertions
   ↓
reconcile current state
   ↓
measure
   ↓
serve machine-readable decisions
```

- **Collectors**: 6 inference probes (`reachability-v1`, `ttft-v1`,
  `throughput-v1`, `json-v1`, `tools-v1`, `context-smoke-v1`) + catalog
  discovery (`discovery-v1`).
- **Immutable store**: SQLite (`endpoints`, `probe_runs`,
  `probe_measurements`, `endpoint_windows`) — raw measurements INSERT-only.
- **Evidence trail**: every run writes `data/runs/<run-id>/` with `run.json`,
  `stdout.log`, `results.jsonl` (one universal envelope per observation),
  `artifacts/` (sha256-addressed raw payloads).
- **Window aggregator**: p50/p90/p95 per endpoint per window (nearest-rank,
  outlier-robust), success/tool/json rates.
- **Current state**: freshness + state enum
  (KNOWN/UNKNOWN/ABSENT/NOT_OBSERVED/NOT_APPLICABLE/STALE/CONFLICTED/UNAVAILABLE/RATE_LIMITED).
- **Resolution**: hard constraints → Pareto rank → weighted preference.
  Eligibility is never mixed with ranking.
- **Surfaces**: FastAPI (`/v1/...` per spec) + MCP stdio server
  (`endpoint_search`, `endpoint_compare`, `endpoint_resolve`,
  `endpoint_history`).

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

export ENDPOINTTRUTH_DB=$(pwd)/data/endpointtruth.db

# register endpoints, discover a real catalog, probe the world
.venv/bin/python -m endpointtruth.cli init-db
.venv/bin/python -m endpointtruth.cli register --config config/endpoints.yaml
.venv/bin/python -m endpointtruth.cli catalog --provider openrouter
.venv/bin/python -m endpointtruth.cli schedule --config config/endpoints.yaml \
    --cycles 2 --concurrency 4
.venv/bin/python -m endpointtruth.cli aggregate --window-min 15

# query
.venv/bin/python -m endpointtruth.cli status
.venv/bin/python -m endpointtruth.cli resolve --capability coding --tools --min-context 64000
.venv/bin/python -m endpointtruth.cli serve --port 8777 &
curl 'http://127.0.0.1:8777/v1/resolve?capability=coding&tools=true&min_context=64000'

# MCP (stdio)
.venv/bin/python -m endpointtruth.cli mcp --jsonrpc
```

## Real data sources used in the verification run

| provider | what is real | credentials |
|---|---|---|
| `opencode-go` | live inference probes (9 models) | `OPENCODE_GO_BASE_URL`, `OPENCODE_GO_API_KEY` (env) |
| `local` | live llama.cpp CPU endpoint (qwen2.5-0.5b, port 8080) | none (`NONE`) |
| `openrouter` | public catalog discovery (414 models: advertised context, prices, params) | none; inference metrics recorded `NOT_OBSERVED` |

No observation is ever fabricated: every probe run stores raw artifacts with a
sha256, a method id/version, source id, state, confidence, and evidence
selector. Advertised data is labeled as advertised (method `discovery-v1`);
live capability is only `KNOWN` when a live probe succeeded.

## Tests

```bash
.venv/bin/python -m pytest tests/ -q        # 17 tests incl. the 8 required scenarios
```

Required scenarios covered:
1. provider says model exists but inference 404s → `ABSENT`
2. HTTP 200 but malformed stream → `stream_malformed` failure
3. tool capability advertised but fails → excluded from `tools=true` resolve
4. endpoint switches model alias → `CONFLICTED`
5. one outlier TTFT doesn't destroy p50 → nearest-rank percentile
6. stale benchmark removed from current ranking → `STALE` filtered
7. provider outage → `UNAVAILABLE`, filtered
8. rate limit distinguished from outage → `RATE_LIMITED` vs `UNAVAILABLE`

## Layout

```
endpointtruth/
  schema.py        # universal envelope + state enum + entities
  db.py            # SQLite (endpoints, probe_runs, probe_measurements, endpoint_windows)
  probes/          # Probe interface + 6 inference probes + discovery
  runner.py        # probe execution + evidence trail (data/runs/<run-id>/)
  scheduler.py     # continuous cycles with concurrency cap
  aggregator.py    # window buckets: p50/p90/p95 + success rates
  state.py         # CURRENT STATE projection
  resolve.py       # hard filter → pareto → weighted preference
  api.py           # FastAPI /v1/*
  mcp_server.py    # MCP stdio (FastMCP or JSON-RPC fallback)
  cli.py           # init-db/register/catalog/probe/cycle/schedule/aggregate/resolve/serve/mcp/status
config/endpoints.yaml
tests/
data/runs/         # generated evidence trails
```

## Verified build facts (see VERIFICATION.md)

- `>=10 endpoints` — 13 registered live/probed + 414 catalog-discovered
- `>=4 probe types` — 7 (6 inference + discovery)
- `>=1000 historical observations` — see VERIFICATION.md table
- API live (`/health`, `/v1/stats`, `/v1/coverage`, `/v1/endpoints`,
  `/v1/resolve`, `/v1/leaderboard`, evidence retrieval)
- MCP live (4 tools over stdio)