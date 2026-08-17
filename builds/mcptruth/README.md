# MCPTruth

> **Continuously test whether an MCP server actually works and characterize the
> cost/quality of its interface.**

Not another directory. A probe harness that tells you, per tracked server:
does it exist, is it reachable, does initialize succeed, does tools/list
succeed, is the schema valid, how big is the schema token footprint, what auth
does it need, how fast is it, does a read-only invocation actually work, and
when did its schema break?

MVP scope (specs/mcptruth/architecture.md, PRODUCT 4): track ~50 MCP servers,
deeply test ~10-20; observe existence, transport, reachability, initialize,
tools/list, schema validity, tool count, schema token cost, auth requirements,
tool latency, basic invocation success, schema changes.

## Quick start

```bash
pip install -r requirements.txt

# 1. Seed the tracked-server registry (~50 servers, curated deep-test set)
python -m app.runner seed

# 2. Probe the deterministic local mock end-to-end (real stdio JSON-RPC)
python -m app.runner probe --server mock:mock-mcp

# 3. Probe real npm servers (npx; needs network, can take a while)
python -m app.runner probe --deep --limit 5 --timeout-ms 25000

# 4. Recompute derived windows / current state
python -m app.runner reduce --minutes 15

# 5. Serve the API
python -m app.api            # http://localhost:8000/health
```

One-command demo:

```bash
python -m app.runner demo
```

## API (spec §API)

```
GET /health
GET /v1/stats
GET /v1/coverage
GET /v1/evidence/{observation_id}
GET /v1/servers
GET /v1/servers/{server_id}
GET /v1/servers/{server_id}/tools
GET /v1/servers/{server_id}/history
GET /v1/tools?server_id=&capability=&safety=
GET /v1/capabilities
GET /v1/capabilities/{capability}/implementations
GET /v1/healthiest?limit=&fresh_seconds=&require_deep=
GET /v1/schema-changes?change_type=&limit=
```

MCP interface (our own MCP server, so agents can query MCPTruth):

```bash
python -m app.mcp_gateway
```

Tools: `mcp_search`, `mcp_health`, `healthiest`, `capability_search`,
`tool_get`, `schema_changes`.

## Product decisions encoded

- **SERVER != TOOL != CAPABILITY** — three separate entity planes;
  `tools` carries schema fingerprints, `tool_capabilities` the M:N mapping.
- **Schema fingerprint** — canonical `{name, description, inputSchema}` JSON
  hashed with sha256; stored with token count and `first_seen`/`last_seen`;
  changed fingerprints land in `schema_changes` (BREAKING when required props
  vanish or types change).
- **Safe testing** — tools classified READ_ONLY / REVERSIBLE / MUTATING /
  UNKNOWN. The harness invokes only READ_ONLY tools and only with curated safe
  args; everything else is a NOT_APPLICABLE observation. Public probes never
  execute destructive tools.
- **Immutable observations** — raw `probe_measurements` are append-only; every
  observation is an Oracle-compatible envelope content-addressed by sha256.
- **Eligibility ≠ ranking** — `healthiest` first hard-filters (retired, stale,
  init failure, tools/list failure), then Pareto/weighted ranks by invocation
  success, p50 latencies, schema breaks.
- **Outlier-proof p50/p95** — percentile-rank from the actual distribution; a
  single 60s outlier cannot destroy a 1s p50.

## Layout

```
data/runs/<run-id>/run.json        run metadata
data/runs/<run-id>/results.jsonl   raw measurements + envelopes
data/runs/<run-id>/artifacts/      tool schemas + invocation payloads
data/runs/<run-id>/evidence.json   artifact sha256 index
data/runs/agent-steps.jsonl        content-addressed agent step log
data/mcptruth.db                   SQLite (WAL)
```

## Tests

```bash
python -m pytest tests/ -v
```

The suite probes the real local mock MCP server over stdio, so the harness,
schema fingerprinting, safety classification and invocation path are exercised
with genuine JSON-RPC traffic — not mocks of our own client.

## Status

MVP 0.1.0. Deterministic reality on the local plane (mock server probe +
aggregation + API), registry of 50+ tracked servers, deep-test harness for
npx-installable npm servers, API + MCP gateway. Live third-party probing needs
credentials for most real endpoints; those servers are tracked and classified
but not deep-tested until a controlled account exists.

*Build date: 2026-08-17. See docs/README.md for the engineering doc.*