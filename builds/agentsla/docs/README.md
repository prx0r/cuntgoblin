# AgentSLA — Cost-per-Success Profiler

Measure the **real** cost, duration and success rate of completing an agent
task: architecture + model(s) + tools + workload → outcome.

## What it does

Runs real tasks through real LLM endpoints under 3–4 execution
architectures, grades completion with **deterministic** graders (pytest,
patch application, compile, citation checks — never an LLM as the grader),
accounts every model call's tokens and cost (provider-reported when the API
supplies it, otherwise an explicit per-token price-table estimate whose basis
is recorded), and serves SLA statistics plus a cost/success frontier.

## Workloads

- `coding.patch` — produce a minimal unified diff that fixes a buggy library
- `coding.debug` — root-cause and patch a buggy parser
- `research.answer` — answer from a local knowledge base with citations

## Architectures

| id | components |
|----|------------|
| `single_agent` | one worker with tools, up to 6 steps |
| `worker_verifier` | worker + advisory LLM verifier, up to 2 revision rounds |
| `planner_worker` | planner emits a plan, worker executes |
| `parallel_candidates_judge` | N candidate workers → deterministic graded selection |

## Layout

```
app/              runner, graders, evidence envelope, db, metrics, cost, api
tasks/            seed task dataset (content-addressed by environment_hash)
benchmarks/       benchmark manifests
mcp/              stdio MCP server (3 tools)
tests/            deterministic unit tests (no network, no LLM)
data/runs/<id>/   per-run evidence envelope: run.json, stdout.log, results.jsonl, artifacts/
data/agentsla.db  append-only observation store (10 tables)
```

## Run it

```bash
pip install -r requirements.txt
# live runs require the provider credentials
export OPENCODE_GO_BASE_URL=... OPENCODE_GO_API_KEY=...

# full live benchmark (real model calls)
python run_benchmark.py --bench benchmarks/bench_v1.json --live

# one live cell
python run_benchmark.py --cell coding.patch single_agent --model deepseek-v4-flash

# deterministic gate (imports, schema, unit tests, envelopes, nofake)
python check.py

# API (uvicorn on :8790)
python -m app.api          # or: uvicorn app.api:app

# MCP server (stdio JSON-RPC)
python mcp/server.py
```

## API

```
GET /health
GET /v1/stats
GET /v1/coverage
GET /v1/evidence/{run_id}
GET /v1/runs/{run_id}
GET /v1/tasks
GET /v1/architectures
GET /v1/architectures/{id}
GET /v1/architectures/{id}/sla?task_class=...
GET /v1/compare?task_class=...&architectures=a,b
GET /v1/tasks/{class}/frontier?min_success=0.8
POST /v1/profile   {"task_class", "architecture_id", ...}
```

OpenAPI schema is served at `/openapi.json`.

## MCP tools

- `architecture_profile` — SLA summary for one architecture
- `architecture_compare` — side-by-side SLA comparison
- `task_economics` — cost/success frontier with Wilson bounds

## Cost accounting honesty

The provider endpoint may not report billed amounts (`cost: "0"`). Every
`cost_events` row therefore records its `basis`:
`provider_reported` when the API returns a nonzero cost, otherwise
`price_table_estimate` from `app/prices.py` (configurable via
`AGENTSLA_PRICE_TABLE`; models missing from the table account at $0 and can
never fabricate a cost). Never treat an estimate as an invoice.

## Anti-cheat

- Grading is deterministic (patch/pytest/compile/regex), never an LLM.
- Hidden tests are embedded in the grader, not shipped in the task dir.
- Stub/demo runs (scripted clients) are marked `stub=true` and can never be
  presented as observations (`check.py -- nofake`).
- Every run envelope carries a sha256 self-hash of its manifest; every task
  directory carries a reproducible `environment_hash`; every run records the
  git SHA of the build that produced it.