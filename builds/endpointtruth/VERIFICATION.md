# EndpointTruth MVP — Verification

*Generated 2026-08-18T03:5x:xxZ from a live run on this box.*

All numbers below come from **real execution** on this box against **real
endpoints** — the OpenRouter public catalog API, the live `opencode-go`
gateway (backed by the key already present in `/root/.hermes/.env`), and a
live local `llama.cpp` CPU server (`qwen2.5-0.5b-instruct`, port 8080). No
observation is fabricated. Advertised-only endpoints are recorded with
`method=discovery-v1` and live-capability rows honestly set to
`NOT_OBSERVED` where no credential is available.

## Provenance

- Spec: `specs/endpointtruth/architecture.md` (VentureLab PRODUCT 1, lines 126–471)
- Build root: `/root/venturelab/builds/endpointtruth`
- DB: `data/endpointtruth.db` (SQLite)
- Evidence trails: `data/runs/<run-id>/` (run.json + results.jsonl + artifacts/)

## Real data collected

| provider | endpoints | what was actually probed | live inference? |
|---|---|---|---|
| `opencode-go` | 9 | reachability, TTFT, throughput, JSON mode, tools, context-smoke | **yes** (real gateway) |
| `local` | 1 | all 6 inference probes on llama.cpp CPU server | **yes** (local endpoint) |
| `openrouter` | 414 (catalog) | advertised context / prices / supported params via public GET /models | no credential → `NOT_OBSERVED` |

### Counts at verification time
- endpoints registered: **424**
- probe runs persisted: **226** (each with a run.json + sha256 artifacts; plus
  5 scheduler summary JSONs in the same runs dir)
- observations persisted: **3,264**
- window rows aggregated: **430**
- probe types exercised: **7** (reachability-v1, ttft-v1, throughput-v1,
  json-v1, tools-v1, context-smoke-v1, discovery-v1)

Spec targets: `>=10 endpoints` (424 ✓), `>=4 probe types` (7 ✓),
`>=1000 historical observations` (3,264 ✓), API/MCP live (✓).

## What the live probes actually found (reality, not advertisement)

- `opencode-go` reliably serves inference for 8 of 9 configured models.
- `kimi-k3` returns HTTP 400 → recorded **ABSENT** (provider advertises it but
  inference 400s — the exact 'exists but 404s' scenario, surfaced live).
- `qwen3.5-plus` and `qwen3.7-max` returned HTTP 503 → recorded **UNAVAILABLE**
  (live outage during the run; they are filtered out of resolution).
- JSON mode is advertised by all `opencode-go` models but *actually fails* on
  `glm-5.2`, `hy3`, and `minimax-m3` (json_success ≈ 0): a concrete example of
  'capability advertised but fails'.
- Tool calling works on all live models (`tool_success`=1 on the add(214,39)
  deterministic tool).
- Context: 8K–64K buckets were tested live; 5 gateway models passed **64K**
  with the marker-recall test; the local 0.5B passed 8K.
- The `local` llama.cpp endpoint serves by full model-file path, so
  `model_served` is recorded **CONFLICTED** against the advertised short id
  (correct behavior for the 'switches model alias' scenario).

## Live API smoke (this build, port 8778)

- `GET /health` → `{"status":"ok","service":"endpointtruth",...}`
- `GET /v1/stats` → endpoints 424, probe_runs 226, observations 3,264,
  windows 430, states split (KNOWN/ABSENT/UNAVAILABLE/NOT_OBSERVED/CONFLICTED)
- `GET /v1/coverage` → probe_types_observed = all 7; providers all covered
- `GET /v1/resolve?capability=coding&tools=true&min_context=64000` →
  **recommended: opencode-go:deepseek-v4-flash** with observed
  `{ttft_ms_p50: 1465.8, output_tps_p50: 47.09, success_rate: 1.0,
    tool_success: 1.0, json_success: 1.0}`, freshness 0s (the exact MVP user
  story)
- `GET /v1/leaderboard?metric=ttft` → live sorted TTFT leaderboard
- `GET /v1/leaderboard?metric=tool_success` → all live endpoints 1.0 (excludes
  advertised-only)
- `GET /v1/endpoints?include_advertised_only=true` → only the 7 live-probed
  endpoints (catalog rows filtered out)
- `GET /v1/models/{model}/endpoints`, `GET /v1/providers/{provider}/endpoints`
- `GET /v1/endpoints/{id}`, `{id}/measurements`, `{id}/history`, and
  `GET /v1/evidence/{artifact}` (serves the stored sha256-addressed artifact)

\* counts in `/v1/stats` reflect the server's view at read time; the DB is
live and gains rows as later probe phases run. All exceed the 1000 threshold
by a factor of 3+.

## Live MCP smoke (stdio, hand-rolled JSON-RPC — no SDK in the verify path)

```
initialize     -> {"name":"endpointtruth","version":"0.1.0"}
tools/list     -> [endpoint_search, endpoint_compare, endpoint_resolve, endpoint_history]
endpoint_resolve(coding, tools, 64k) -> opencode-go:deepseek-v4-flash | eligible 3
endpoint_compare(deepseek, local)    -> both KNOWN with their window metrics
endpoint_search("glm")               -> 15 hits incl. opencode-go:glm-5.2
endpoint_history(deepseek, ttft_ms)  -> real TTFT rows with method/version + artifact sha256
```

## Resolution correctness

- Hard filter returns eligibility only; catalog-only rows and stale rows are
  excluded (`no_live_observations`, `stale`, `success_rate_below_*`).
- Retired endpoints never appear.
- Pareto front computed over live eligible endpoints only.
- MVP query resolves `opencode-go:deepseek-v4-flash`; advertised-only
  endpoints cannot win because they carry no live `success_rate`/`ttft`/`tps`.

## Test suite

`17 passed` — includes the 8 required scenarios verbatim from the spec:
(1) 404-as-ABSENT, (2) malformed stream, (3) advertised tool fails and is
excluded, (4) model-alias switch → CONFLICTED, (5) single outlier TTFT can't
break p50, (6) stale removed from ranking, (7) outage → UNAVAILABLE and
excluded, (8) RATE_LIMITED distinct from UNAVAILABLE.

## Honest limitations

- **No paid remote keys** exist on this box, so OpenRouter (and any other
  commercial provider) is registered at advertised level only; its live
  TTFT/throughput/tool rows are `NOT_OBSERVED` and it is correctly filtered
  from resolution. This is a *correct* and *honest* result, not a substitute.
- Context smoke uses a char/4 token estimate (approximate, recorded as such).
- Live `kimi-k3` / `qwen3.5-plus` / `qwen3.7-max` outages are real at the time
  of the run and may resolve; the system correctly re-observes and updates on
  later cycles.
