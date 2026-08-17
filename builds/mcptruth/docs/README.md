# MCPTruth — engineering notes

*Built 2026-08-17 from specs/mcptruth/architecture.md (Product 4).*

## What is real in this MVP

The build follows the venturelab STANDARD: nothing counts as evidence unless it
is machine-produced, logged, content-addressed and reproducible. The unit test
suite runs a real probe cycle against a real local MCP server over stdio
JSON-RPC; the probe artifacts it produces are on disk under data/runs/ and
row-for-row in SQLite. The API serves those rows.

## Layering

```
DISCOVERY (app/discovery.py: ~50 curated servers, deep-test subset)
      |
      v
MCP SERVER IDENTITY (app/db.py servers + server_versions + auth_schemes)
      |
      v
SAFE TEST HARNESS (app/harness.py: init -> tools/list -> invocation)
      |                | mcp SDK client over stdio / streamable-http
      v
OBSERVATIONS (immutable probe_measurements + Oracle envelopes, content-addressed)
      |
      v
CURRENT STATE (app/reducer.py: server_windows p50/p95/success rates, staleness)
      |
      v
API (app/api.py)  +  MCP (app/mcp_gateway.py)
```

## Why these files

- `app/db.py` — single SQLite schema; append-only measurements; fingerprint +
  schema-change detection at the tool upsert point.
- `app/oracle.py` — the universal evidence envelope (spec §0) + content
  addressing (observation_id = sha256 of canonical envelope).
- `app/harness.py` — probes via the real `mcp` SDK. Safety gate is structural:
  invocation only for READ_ONLY classified tools with curated safe args.
- `app/discovery.py` — tracked registry; deep-test ids configured so the
  deterministic local mock is always first.
- `app/capabilities.py` — normalized capability map, curated (confidence 1.0)
  + keyword heuristic (0.5-0.8), never a single number.
- `app/reducer.py` — windowing, percentile p50/p95, freshness, eligibility
  filter separate from Pareto/weighted ranking.
- `app/api.py` / `app/mcp_gateway.py` — same DB, two surfaces.

## Operational notes

- Set `MCPTRUTH_DB` to relocate the database.
- Set `MCPTRUTH_TOKEN` for bearer/api-key http servers (never persisted).
- npx probes download packages on first run; give them `--timeout-ms` headroom
  or run them as background jobs. The mock server is the deterministic path.
- `server_windows` is a derived projection: `python -m app.runner reduce` can
  rebuild it any time from raw measurements; raw rows are never rewritten.

## Known boundaries (honest)

- Live probing of real npm servers depends on outbound network + npm; many
  real servers also need API keys/host accounts, so they are tracked but marked
  deep_test=0 with auth_scheme recorded. That is the correct MVP shape: the
  harness proves they exist and classifies them, and stops at the safety line.
- Capability mapping is curated + keyword-heuristic. LLM-assisted review is a
  documented future step, not claimed here.
- `README_ONLY` classification is heuristic; a misclassified tool is guarded by
  the curated SAFE_ARGS gate (no args -> no invocation).

## Required test scenarios (spec) — coverage

| scenario | test |
|---|---|
| server advertised but unreachable | test_unreachable_server_classified_connection_error |
| wire-level garbage (malformed stream) | test_garbage_stdio_server_recorded_failed |
| tool capability advertised but fails | test_failed_invocation_recorded |
| schema fingerprint switches (alias swap) | test_breaking_schema_change_detected |
| one outlier doesn't destroy p50 | test_outlier_does_not_destroy_p50 |
| stale benchmark removed from ranking | test_stale_server_excluded_from_healthiest |
| provider outage | test_init_failure_excluded_but_ranked_separated |
| rate limit ≠ outage | test_rate_limit_distinguished_from_outage |
| MUTATING never invoked | test_safe_args_only_read_only_invoked |
| content addressing holds | test_observation_ids_are_real_sha256 |