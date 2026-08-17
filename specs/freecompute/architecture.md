Yes. The right way to do this is to make each idea a **small independently shippable product with a brutal MVP boundary**, but force all of them to emit the same Oracle-compatible evidence envelope.

Below are **seven agent-ready technical build specs**. Each can be handed to a separate coding agent as its project brief.

The common principle is:

```text
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

Do **not** make seven giant frameworks.

---

# 0. Shared Oracle-compatible substrate

Every project should use the same tiny conceptual kernel.

Do not necessarily extract this into a shared repo immediately. Copy the interface first; consolidate once two products prove it.

## Universal envelope

Every factual observation emitted by a collector:

```json
{
  "subject": {
    "type": "endpoint",
    "id": "openrouter:deepseek-r1:novita"
  },

  "predicate": "endpoint.throughput",

  "value": {
    "number": 67.4,
    "unit": "tokens_per_second"
  },

  "state": "KNOWN",

  "observed_at": "2026-08-18T03:00:00Z",
  "valid_until": "2026-08-18T03:15:00Z",

  "source": {
    "type": "synthetic_probe",
    "id": "endpointtruth-sgp-01"
  },

  "method": {
    "id": "throughput-probe-v1",
    "version": "1.0.0"
  },

  "confidence": 0.98,

  "evidence": [
    {
      "artifact_sha256": "...",
      "selector": "$.metrics.output_tps"
    }
  ]
}
```

Common state enum:

```text
KNOWN
UNKNOWN
ABSENT
NOT_OBSERVED
NOT_APPLICABLE
STALE
CONFLICTED
UNAVAILABLE
```

Common entities:

```text
Resource
ResourceVersion
Capability
Endpoint
Offer
Assertion
Observation
Artifact
Measurement
Relationship
Evaluation
Execution
```

Every repo should expose:

```text
GET /health
GET /v1/stats
GET /v1/coverage
GET /v1/evidence/{id}
```

and produce:

```text
data/runs/<run-id>/
  run.json
  stdout.log
  results.jsonl
  artifacts/
```

---

# PRODUCT 1 — ENDPOINTTRUTH

## Mission

> **Continuously determine what an actual LLM serving endpoint can do right now.**

Not model benchmarking.

Not provider reviews.

The unit of truth is approximately:

```text
model checkpoint
× serving provider
× concrete endpoint/deployment
× region
× time
```

---

## MVP user story

A router asks:

```http
GET /v1/resolve?capability=coding&tools=true&min_context=64000
```

EndpointTruth returns:

```json
{
  "recommended": {
    "endpoint_id": "openrouter:foo:model-x",
    "model_id": "model-x",
    "provider": "foo",

    "observed": {
      "reachable": true,
      "ttft_ms_p50": 438,
      "output_tps_p50": 71.2,
      "success_rate": 0.994,
      "tool_success": 0.96
    },

    "freshness_seconds": 142
  }
}
```

The caller does not need to manually benchmark providers.

---

# MVP scope

Start with **3–5 providers and 10–20 models**.

Enough variety to prove endpoint differences.

Measure only:

```text
endpoint reachability
model actually served
TTFT
output throughput
HTTP error rate
streaming support
JSON mode
tool calling
advertised context
small effective-context sanity test
current price imported from Dell
```

Do not initially build:

```text
full 1M context benchmark
multimodal
every region
energy measurements
100 providers
human quality evaluation
```

---

# Architecture

```text
                 SCHEDULER
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
  discovery       canary        benchmark
  collectors      probes         probes
       │             │             │
       └─────────────┼─────────────┘
                     ▼
                RAW ARTIFACTS
                     │
                     ▼
                 OBSERVATIONS
                     │
                     ▼
                MEASUREMENTS
                     │
                     ▼
              WINDOW AGGREGATOR
                     │
             p50/p90/p95/errors
                     │
                     ▼
                CURRENT STATE
                     │
              ┌──────┴──────┐
              ▼             ▼
             API           MCP
```

---

# Database

Postgres eventually; SQLite is acceptable for MVP.

## `endpoints`

```sql
endpoint_id
provider_id
model_id
provider_model_name
base_url
region
deployment_variant
quantization_state
discovered_at
retired_at
```

## `probe_runs`

```sql
probe_run_id
endpoint_id
probe_type
started_at
completed_at
probe_region
method_version
status
artifact_id
```

## `probe_measurements`

```sql
measurement_id
probe_run_id
metric
value_numeric
value_text
unit
state
observed_at
```

## `endpoint_windows`

Derived projection:

```sql
endpoint_id
window_start
window_end
samples
success_rate
ttft_p50
ttft_p95
tps_p50
tps_p95
tool_success_rate
json_success_rate
```

Never overwrite raw probe measurements.

---

# Probe interface

Every probe:

```python
class Probe:
    id: str
    version: str

    async def run(endpoint, credentials) -> ProbeResult:
        ...
```

`ProbeResult`:

```python
{
    "status": "SUCCESS",
    "measurements": [],
    "raw_artifacts": [],
    "errors": []
}
```

---

# Probes

### `reachability-v1`

Very small inference request.

### `ttft-v1`

Streaming request; measure request start → first token.

### `throughput-v1`

Generate controlled number of output tokens.

### `json-v1`

Request deterministic JSON schema.

Validate parser success.

### `tools-v1`

Give one trivial deterministic tool:

```text
add(a,b)
```

Test whether correct tool call occurs.

### `context-smoke-v1`

Don't immediately binary-search 1M tokens.

Test buckets:

```text
8K
32K
64K
128K
```

until failure.

---

# API

```text
GET /v1/endpoints
GET /v1/endpoints/{id}
GET /v1/endpoints/{id}/measurements
GET /v1/endpoints/{id}/history

GET /v1/resolve

GET /v1/models/{model}/endpoints
GET /v1/providers/{provider}/endpoints

GET /v1/leaderboard?metric=ttft
GET /v1/leaderboard?metric=tool_success
```

MCP:

```text
endpoint_search
endpoint_compare
endpoint_resolve
endpoint_history
```

---

# Resolution scoring

Initially:

```text
hard constraints first
    ↓
remove stale
remove unavailable
remove unsupported capability
    ↓
Pareto rank
    ↓
weighted preference
```

Never mix eligibility with ranking.

```python
eligible = hard_filter(...)
ranked = pareto_rank(eligible)
```

---

# Tests

Required:

```text
provider says model exists but inference 404s
HTTP 200 but malformed stream
tool capability advertised but fails
endpoint switches model alias
one outlier TTFT doesn't destroy p50
stale benchmark removed from current ranking
provider outage
rate limit response distinguished from outage
```

Target MVP completion:

```text
>=10 endpoints
>=4 probe types
>=1000 historical observations
API/MCP live
dashboard optional
```

---

# PRODUCT 2 — AGENTSLA

## Mission

> **Measure the real cost, duration and success rate of completing an agent task.**

The primitive is no longer:

```text
model benchmark
```

It is:

```text
architecture + model(s) + tools + workload → outcome
```

---

# MVP

Support three workloads:

```text
coding.patch
coding.debug
research.answer
```

Support 3–4 execution architectures:

```text
single_agent
worker_verifier
planner_worker
parallel_candidates_judge
```

Record:

```text
success
cost
tokens
duration
tool calls
retries
model calls
failure reason
```

---

# Architecture

```text
                 TASK DATASET
                     │
                     ▼
                RUN MANIFEST
                     │
           ┌─────────┼───────────┐
           ▼         ▼           ▼
      architecture architecture architecture
           A         B            C
           │         │            │
           └─────────┼────────────┘
                     ▼
                  RUNNER
                     │
               execution trace
                     │
                     ▼
                  GRADER
                     │
             success / failure
                     │
                     ▼
              COST ACCOUNTING
                     │
                     ▼
               SLA DATABASE
```

---

# Core object

```json
{
  "architecture_id": "worker-verifier-v1",

  "components": [
    {
      "role": "worker",
      "model": "..."
    },
    {
      "role": "verifier",
      "model": "..."
    }
  ],

  "task_id": "repo-bugfix-0182",

  "result": {
    "success": true,
    "cost_usd": 0.084,
    "duration_seconds": 92,
    "input_tokens": 44192,
    "output_tokens": 8092,
    "tool_calls": 13,
    "retries": 2
  }
}
```

---

# Tables

```text
tasks
task_versions
architectures
architecture_versions
runs
run_components
model_calls
tool_calls
evaluations
cost_events
```

`runs` must record:

```text
git SHA
architecture version
task version
model IDs
provider endpoint IDs
environment image/hash
random seed if applicable
```

---

# Success grading

Coding:

```text
tests pass
hidden tests
lint/typecheck
patch applies
no forbidden modifications
```

Research:

```text
reference-backed factual rubric
coverage
citation correctness
```

Do not use another LLM as the only grader.

---

# Metrics

Core:

```text
success_rate
cost_per_attempt
cost_per_success
duration_per_success
tokens_per_success
tool_calls_per_success
retry_rate
```

Derived:

```text
efficiency = success_probability / expected_cost
```

But retain raw data.

---

# API

```text
POST /v1/profile
GET /v1/architectures
GET /v1/architectures/{id}
GET /v1/architectures/{id}/sla
GET /v1/compare
GET /v1/tasks/{class}/frontier
```

MCP:

```text
architecture_profile
architecture_compare
task_economics
```

---

# MVP success condition

You should be able to truthfully say something like:

```text
On benchmark repo-bugfix-v1:

single strong agent
74% success
$0.24 / success

cheap worker + strong verifier
81% success
$0.11 / success
```

That observation becomes useful to Knee and ArchOracle.

---

# PRODUCT 3 — KNEE

Build this **after AgentSLA has real runs**.

## Mission

> **Find the cheapest model or architecture that remains above a required empirical quality threshold.**

This is the optimization API.

---

# Input

```json
{
  "task_class": "coding.patch",

  "constraints": {
    "minimum_success": 0.9,
    "max_duration_seconds": 300,
    "tools_required": true
  },

  "objective": "min_cost"
}
```

---

# Output

```json
{
  "recommended": {
    "architecture_id": "worker-verifier-v4",
    "expected_success": 0.923,
    "expected_cost_usd": 0.081
  },

  "quality_cliff": {
    "next_cheaper": {
      "architecture_id": "single-cheap-v8",
      "expected_cost_usd": 0.044,
      "expected_success": 0.711
    },

    "success_drop": 0.212
  }
}
```

---

# Architecture

Knee itself should be thin.

```text
Dell economics ──────────┐
EndpointTruth ───────────┤
AgentSLA ────────────────┤
                         ▼
                  CANDIDATE BUILDER
                         │
                  hard constraints
                         │
                         ▼
                   PARETO FRONTIER
                         │
                         ▼
                    KNEE FINDER
                         │
                         ▼
                    explanation
```

---

# Core algorithm v1

Given candidates:

```text
(cost, measured_success)
```

1. Remove candidates below minimum sample count.
2. Compute confidence interval for success.
3. Apply hard constraints.
4. Sort ascending cost.
5. Find first candidate whose **lower confidence bound** exceeds required success.
6. Compute cheaper-neighbor drop.

Do not claim 90% from `9/10`.

Use uncertainty.

Example:

```python
candidate_is_valid =
    wilson_lower_bound(successes, trials) >= minimum_success
```

---

# Important feature

Knee must tell caller:

```text
INSUFFICIENT_EVIDENCE
```

when it doesn't know.

This is extremely important.

---

# API

```text
POST /v1/knee
POST /v1/frontier
GET /v1/task-classes
GET /v1/frontiers/{task}
```

MCP:

```text
find_cheapest_sufficient
compare_cost_quality
get_task_frontier
```

---

# PRODUCT 4 — MCPTRUTH

## Mission

> **Continuously test whether an MCP server actually works and characterize the cost/quality of its interface.**

Not another directory.

---

# MVP

Track ~50 MCP servers but deeply test perhaps 10–20.

Observe:

```text
server exists
transport
reachable
initialize succeeds
tools/list succeeds
schema valid
tool count
schema token cost
auth requirements
tool latency
basic invocation success
schema changes
```

---

# Architecture

```text
registries/github/npm/etc
        │
        ▼
    DISCOVERY
        │
        ▼
 MCP SERVER IDENTITY
        │
        ▼
   SAFE TEST HARNESS
        │
 ┌──────┼─────────┐
 ▼      ▼         ▼
init  tools/list  invocation
 │      │          │
 └──────┼──────────┘
        ▼
   OBSERVATIONS
        │
        ▼
 CURRENT MCP STATE
        │
    ┌───┴────┐
    ▼        ▼
   API      MCP
```

---

# Entity model

```text
MCPServer
MCPServerVersion
Transport
Tool
ToolVersion
Capability
AuthScheme
InvocationProbe
```

Important:

```text
SERVER != TOOL
TOOL != CAPABILITY
```

---

# Schema fingerprint

Canonicalize each MCP tool schema:

```json
{
  "name": "...",
  "description": "...",
  "inputSchema": {}
}
```

then hash canonical JSON.

Store:

```text
schema_sha256
schema_token_count
first_seen
last_seen
```

This makes breaking API evolution visible.

---

# Capabilities

Introduce normalized capabilities separately:

```text
web.search
repository.issue.create
browser.navigate
database.query
filesystem.read
```

A tool may implement multiple capabilities.

Initially mappings can be curated + LLM-assisted + reviewed.

---

# API

```text
GET /v1/servers
GET /v1/servers/{id}
GET /v1/servers/{id}/tools
GET /v1/servers/{id}/history

GET /v1/tools
GET /v1/capabilities/{capability}/implementations

GET /v1/healthiest
GET /v1/schema-changes
```

MCP:

```text
mcp_search
mcp_health
capability_search
tool_get
```

---

# Safe testing

Never let public MCP probes arbitrarily execute destructive tools.

Tool classifications:

```text
READ_ONLY
REVERSIBLE
MUTATING
UNKNOWN
```

MVP invocation testing only for:

```text
READ_ONLY
```

or controlled test accounts.

---

# Important measurements

```text
initialization success
tools/list success
p50 connection latency
p50 invocation latency
schema token footprint
tool invocation success
uptime
breaking schema changes
```

---

# PRODUCT 5 — TOOLLOADER

Build on MCPTruth.

## Mission

> **Give an agent the smallest, best toolset for its current task rather than mounting every available tool.**

---

# User experience

Agent only gets two permanent tools:

```text
tool_search
tool_invoke
```

Potentially:

```text
tool_expand_schema
```

Everything else is virtual.

---

# Runtime

```text
agent intent
    │
    ▼
task embedding/classification
    │
    ▼
candidate capabilities
    │
    ▼
candidate implementations
    │
    ▼
hard constraints
    │
    ▼
reranker
    │
    ▼
choose 3–5 tools
    │
    ▼
lazy schema load
    │
    ▼
invoke
    │
    ▼
record success
```

---

# Tool score

Start explicit:

```text
score =
  relevance
× historical_success
× health
× compatibility

minus

schema_context_cost
latency_penalty
monetary_cost
auth_friction
```

Do not train a complex model initially.

---

# Request

```json
{
  "task": "find the latest issues in this repo and label bugs",
  "agent_context": {
    "platform": "opencode"
  },
  "constraints": {
    "max_tools": 4,
    "noninteractive_auth": true
  }
}
```

Response:

```json
{
  "tools": [
    {
      "tool_id": "github-mcp:list_issues",
      "why": "..."
    },
    {
      "tool_id": "github-mcp:update_issue",
      "why": "..."
    }
  ],

  "schema_tokens": 1312
}
```

---

# Tool telemetry

Every invocation:

```text
task fingerprint
tool chosen
alternatives
latency
success
error
result usefulness if measurable
```

This creates the ranking moat.

---

# MCP surface

This project should itself be an MCP server:

```text
tool_search
tool_get_schema
tool_invoke
tool_feedback
```

The calling agent never needs to mount downstream MCP servers directly if Toolloader can proxy them.

---

# MVP test

Create corpus of 100 tool-choice tasks.

Example:

```text
"open a GitHub issue"
"search the web"
"read SQLite DB"
"browse page"
"send message"
```

Metrics:

```text
top-1 correct capability
top-3 correct tool
schema tokens loaded
invocation success
```

Target:

```text
top-3 recall > 95%
mean loaded tools <= 5
```

---

# PRODUCT 6 — FALLBACKGRAPH

## Mission

> **Represent which machine resources can replace one another and how to translate between them.**

This is one of the most strategically important later primitives.

---

# Core abstraction

Do not start from vendors.

Start from capabilities:

```text
Capability:
  web.search
```

Implementations:

```text
exa.search
brave.search
tavily.search
bing.search
```

Each relationship:

```json
{
  "resource": "exa.search",
  "implements": "web.search",

  "compatibility": {
    "functional": 0.97,
    "input_adapter": "exa_to_common_v1",
    "output_adapter": "common_from_exa_v1"
  }
}
```

---

# Graph

```text
             web.search
           /      |      \
          /       |       \
        Exa     Brave    Tavily

          ↑      fallback      ↑
          └────────────────────┘
```

But this generalizes:

```text
model capability
database
MCP tool
API
memory backend
agent harness
inference provider
video model
compute
```

---

# Tables

```text
resources
capabilities
resource_capabilities
equivalence_edges
substitution_edges
adapters
compatibility_tests
compatibility_measurements
```

---

# Edge semantics

Avoid one meaningless `equivalent=true`.

Use:

```text
FULL
FUNCTIONAL
PARTIAL
LOSSY
CONDITIONAL
INCOMPATIBLE
UNKNOWN
```

and dimensions:

```text
input compatibility
output compatibility
semantic compatibility
auth compatibility
latency delta
cost delta
quality delta
```

---

# API

```text
GET /v1/resource/{id}/fallbacks
GET /v1/capability/{id}/implementations

POST /v1/resolve-fallback
POST /v1/translate
```

Input:

```json
{
  "resource": "tavily.search",
  "reason": "unavailable",

  "constraints": {
    "max_cost": 0.01,
    "minimum_functional_compatibility": 0.9
  }
}
```

---

# Output

```json
{
  "replacement": "exa.search",

  "compatibility": 0.96,

  "adapter": {
    "input": "tavily_to_exa_v2",
    "output": "exa_to_common_v1"
  },

  "expected_changes": {
    "cost_delta": -0.002,
    "latency_delta_ms": 71
  }
}
```

---

# MVP

Do not attempt all software.

Choose three capabilities:

```text
web.search
repository.issue.create
llm.chat_completion
```

Implement 3–5 providers each.

Prove automatic substitution.

---

# Killer integration

Combine with ArchOracle:

```text
architecture requires:
capability:web.search
```

not:

```text
architecture requires:
Tavily
```

Then architectures become portable.

---

# PRODUCT 7 — STACKGRAPH

## Mission

> **Build a historical dependency/adoption graph of what the agent ecosystem actually uses together.**

Essentially:

```text
BuiltWith + npm dependency graph
for agent infrastructure
```

---

# MVP sources

Only public GitHub initially.

Find repos containing signals such as:

```text
AGENTS.md
CLAUDE.md
.mcp.json
mcpServers
langgraph
crewai
autogen
litellm
openrouter
opencode
skills/
```

Then identify normalized components.

---

# Pipeline

```text
GitHub discovery
      │
      ▼
repository snapshot
      │
      ▼
config/file detector
      │
      ▼
component extractor
      │
      ▼
identity normalization
      │
      ▼
co-occurrence graph
      │
      ▼
architecture motif miner
      │
      ▼
historical snapshots
```

---

# Entities

```text
Repository
Component
ComponentVersion
Framework
MCPServer
ModelProvider
AgentHarness
Skill
ArchitectureMotif
```

Edges:

```text
USES
DEPENDS_ON
CONFIGURES
CO_OCCURS_WITH
MIGRATED_FROM
MIGRATED_TO
```

---

# Initial data

For each repository:

```json
{
  "repo": "...",
  "observed_at": "...",

  "components": [
    "opencode",
    "openrouter",
    "playwright-mcp"
  ],

  "signals": [
    {
      "file": ".mcp.json",
      "artifact_hash": "..."
    }
  ]
}
```

Don't infer usage from README mentions alone.

Different confidence levels:

```text
DEPENDENCY
CONFIGURED
IMPORT
DOCUMENTATION_ONLY
UNKNOWN
```

---

# API

```text
GET /v1/components/{id}
GET /v1/components/{id}/commonly-used-with
GET /v1/components/{id}/adoption
GET /v1/components/{id}/migrations

GET /v1/trending
GET /v1/stacks
GET /v1/motifs
```

MCP:

```text
stack_search
component_adoption
component_neighbors
architecture_patterns
```

---

# Architecture motif extraction

This is where StackGraph becomes more than analytics.

Try to infer patterns like:

```text
planner
  ↓
workers[]
  ↓
verifier
```

from:

```text
configuration
prompts
workflow definitions
agent source code
```

Initially heuristic/LLM-assisted.

Mark:

```text
INFERRED
```

not measured truth.

Eventually compare motif prevalence with AgentSLA results.

---

# PRODUCT 8 — FREECOMPUTE

This should probably live extremely close to Dell rather than as a totally separate company.

## Mission

> **Answer how much useful zero/low-cost machine intelligence capacity is actually available right now.**

Not:

```text
list of free APIs
```

but:

```text
usable capacity
```

---

# Input

```json
{
  "task": "coding",
  "requests": 500,
  "avg_input_tokens": 4000,
  "avg_output_tokens": 1500,

  "requirements": {
    "tools": true,
    "context": 64000
  }
}
```

---

# Output

```json
{
  "possible": true,

  "estimated_free_fraction": 0.91,

  "routes": [
    {
      "endpoint": "...",
      "estimated_requests": 300,
      "quota_window": "rolling_5h"
    },
    {
      "endpoint": "...",
      "estimated_requests": 155
    }
  ],

  "remaining_paid_requests": 45
}
```

---

# Inputs

From Dell:

```text
offer
economic access
quota
rate limit
promotion
eligibility
```

From EndpointTruth:

```text
availability
throughput
capabilities
```

Optional user-side state:

```text
remaining account quota
balances
subscription
```

---

# Planner

This is a constrained allocation problem.

Routes:

```text
r1...rn
```

Each has:

```text
capacity
cost
task suitability
availability
rate limit
```

Goal initially:

```text
maximize free workload completion
```

Then:

```text
minimize expected paid remainder
```

A straightforward linear/greedy solver is sufficient for MVP.

Do not need sophisticated optimization.

---

# Privacy

User account quotas should remain:

```text
local
```

where possible.

Architecture:

```text
public Dell facts
       +
local user quota state
       ↓
local/freecompute planner
```

Offer SDK:

```bash
pip install freecompute
```

---

# The one I would add: AGENTIC SECURITY INTELLIGENCE

Because it fits the same architecture extremely well.

# PRODUCT 9 — AGENTSEC / agenticaisecurity.org

## Mission

> **Tell agents whether a tool/MCP/API/resource is safe enough to load and what permissions it actually implies.**

Not vulnerability scanning broadly.

Start with **agent resource risk intelligence**.

---

# Resource profile

```json
{
  "resource": "example-mcp",

  "risk": {
    "score": 0.63,
    "state": "ELEVATED"
  },

  "permissions": [
    "filesystem.read",
    "filesystem.write",
    "shell.execute",
    "network.outbound"
  ],

  "observations": {
    "signed_release": false,
    "maintainer_count": 1,
    "last_commit": "...",
    "dependency_alerts": 2
  }
}
```

---

# Sources

```text
GitHub repo
package metadata
dependency graph
release signatures
MCP schemas
permissions requested
static code analysis
known vulnerability databases
runtime sandbox observations
```

Separate:

```text
FACT
HEURISTIC
SECURITY_FINDING
```

religiously.

---

# MCP tools

```text
security_check_resource
security_compare
security_explain_permission
security_find_safer_alternative
```

And then the killer integration:

```text
Toolloader
   ↓
candidate tools
   ↓
AgentSec filter
   ↓
safe eligible tools
```

FallbackGraph can locate safer substitutes.

---

# BUILD ORDER ACROSS ALL PROJECTS

I would **not** parallel-build all nine.

This is the dependency structure I'd use:

```text
                 DELL
              /        \
             ▼          ▼
      EndpointTruth   FreeCompute
             │
             ▼
          AgentSLA
             │
             ▼
            Knee


         MCPTruth
             │
             ▼
         Toolloader
             │
             ▼
        FallbackGraph


         StackGraph
             │
             ▼
         ArchOracle
```

AgentSec can join:

```text
MCPTruth → AgentSec → Toolloader
```

The eventual system:

```text
                            ARCHORACLE
                         architecture.resolve
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
          StackGraph         AgentSLA        research corpus
          adoption            outcomes           papers
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                        architecture choice
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
               Knee         Toolloader       Memory
                 │              │
                 ▼              ▼
          EndpointTruth      MCPTruth
                 │              │
                 └──────┬───────┘
                        ▼
                  FallbackGraph
                        │
                        ▼
                     EXECUTE
                        │
                        ▼
                    TELEMETRY
                        │
                        └────────────→ AgentSLA
```

---

# Common repository layout

I'd force every agent building these to use roughly:

```text
repo/
├── README.md
├── AGENTS.md
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
│
├── app/
│   ├── domain/
│   ├── ingest/
│   ├── evidence/
│   ├── reconcile/
│   ├── measurements/
│   ├── services/
│   ├── api/
│   └── mcp/
│
├── migrations/
│
├── tests/
│   ├── unit/
│   ├── fixtures/
│   ├── integration/
│   ├── adversarial/
│   └── contract/
│
├── data/
│   ├── fixtures/
│   └── runs/
│
└── docs/
    ├── ARCHITECTURE.md
    ├── DATA-MODEL.md
    ├── API.md
    ├── TESTING.md
    └── MVP-CERTIFICATE.md
```

For MVP, FastAPI + SQLite/Postgres is perfectly adequate.

Don't optimize the web framework.

The valuable engineering is in **identity, evidence, measurements and semantics**.

---

# Universal MVP completion contract

Give every coding agent this final requirement:

```text
MVP is NOT complete merely because endpoints respond.

MVP completion requires:

1. Clean install from empty database
2. Deterministic fixtures
3. End-to-end ingestion
4. Immutable observation/evidence storage
5. Current-state projection
6. REST API
7. MCP API where relevant
8. OpenAPI schema
9. Unit tests
10. Integration tests
11. Adversarial tests
12. Example real-world dataset
13. Coverage report
14. README quickstart
15. AGENTS.md
16. Machine-readable MVP certificate
```

Final command:

```bash
python -m app.certify
```

Expected:

```text
PROJECT MVP CERTIFICATION

clean_bootstrap        PASS
schema                 PASS
unit                   PASS
fixtures               PASS
integration            PASS
provenance             PASS
api_contract           PASS
mcp_contract           PASS
adversarial            PASS

critical_failures=0

MVP CERTIFICATE: PASS
```

---

# If I were allocating agents right now

I would hand out work in this order:

### Agent A — **Finish Dell**

No distraction.

### Agent B — **EndpointTruth**

This is probably the most commercially useful new repo and gives Dell empirical teeth.

### Agent C — **MCPTruth**

Best second Oracle vertical and prerequisite for Toolloader.

### Agent D — **AgentSLA**

Create the task/run/evaluation substrate.

Once those three produce data:

### Agent E — **Knee**

Mostly an optimizer over existing evidence.

### Agent F — **Toolloader**

Consumes MCPTruth.

### Agent G — **StackGraph**

Can quietly collect data for months.

Then:

### Agent H — **ArchOracle**

Consume everything rather than inventing speculative architecture metadata.

That last dependency is important. **ArchOracle becomes much more valuable if its recommendations are based on actual AgentSLA executions, real ecosystem patterns from StackGraph, real endpoint behavior from EndpointTruth, and real tool behavior from MCPTruth.**

Then the MCP call:

```text
architecture.resolve(project)
```

doesn't mean:

> “An LLM guessed a cool multi-agent setup.”

It means:

> “Across comparable projects, this graph pattern has the best observed cost/success frontier; these endpoints are currently healthy; these tools are currently working; here is the evidence; I can instantiate it now.”

**That finished system is genuinely new and useful.**
