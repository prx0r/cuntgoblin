# TOOLLOADER — Technical Architecture

*Generated: 2026-08-17T20:18:57Z · Source: `reports/toolloader/report.md` · Version: 1.0*

---

## 0. Status and Provenance — read this first

This specification is **machine-proposed**, derived from the VentureLab toolloader report
(`reports/toolloader/report.md`) and an arXiv verification pass run 2026-08-17T20:18Z. It is
**not** PROVED or CORPORATE-approved. Every load-bearing external claim is marked with its verified
status below. Where the source report could not be verified, this document says so instead of
repeating the claim.

| Claim in source report | Verification result |
|---|---|
| MCP-Zero exists (active tool discovery) | VERIFIED — arXiv 2506.01056v4 |
| "Dynamic Tool Gating and Lazy Schema Loading" exists | VERIFIED — arXiv 2604.21816v1 ("Tool Attention Is All You Need") |
| "Scalable LLM Agent Tool Access in the Cloud", 23.8x token reduction | VERIFIED — arXiv 2607.15593v1; figure is **paper-reported**, not independently reproduced here |
| "SING: Synthetic Intention Graph for Scalable Active Tool" | **NOT VERIFIED — no matching arXiv record found (title search, 2026-08-17). Treated as unconfirmed; nearest real anchors: AnyTool hierarchical retrieval (2402.04253v1), set-level tool retrieval (2607.25718v2).** |
| mcp-gateway ~500 stars | CORRECTED — GitHub API 2026-08-17: 52 stars |
| awesome-mcp-servers ~5,000 stars | CORRECTED — GitHub API 2026-08-17: 92,485 stars |
| 95% tool-token reduction | VERIFIED as paper-internal simulation claim — arXiv 2604.21816v1 (authors explicitly mark end-to-end figures as projections) |

**Design posture derived from the thesis:** the product is not "another vector search wrapper"; it
is a **scoring function** over semantic relevance, historical success, schema-token cost, latency,
health, permissions, auth friction, reliability, and price, feeding a token-budgeted selection and a
lazy schema loader. Everything below serves that one differentiator.

---

## 1. Scope

### 1.1 Goals

1. Given an agentic task (free text + context), return the **minimum token-cost tool set** that can
   plausibly complete it, not the most semantically similar single tool.
2. Make tool selection **learnable**: selection quality improves from logged success/failure
   telemetry, without prompt engineering per server.
3. Eliminate the **MCP/Tools Tax** (eager full-schema injection; measured in the wild at roughly
   10k–60k tokens per turn in multi-server deployments per 2604.21816v1) via lazy schema promotion.
4. Respect operational reality: health, latency, auth friction, permissions, price, and reliability
   are first-class scoring signals, not afterthoughts.
5. Scale to 1,900+ registered tools today and 3,000+ (the verified cloud-scale regime of
   2607.15593v1) without raising per-turn context cost linearly.

### 1.2 Non-goals (v1)

- Not a replacement MCP server registry or transport layer — operates in front of any MCP servers /
  REST APIs.
- Not a code-execution sandbox — execution stays with the agent/MCP runtime; Toolloader only
  **selects and loads**.
- Not an automatic tool authoring service (MCP-Zero-style active discovery is tracked in research,
  not v1 scope).
- No cross-tenant data pooling in v1; feedback telemetry is per-tenant until the data-licensing
  product requirement is designed.

---

## 2. System Overview

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        TOOLLOADER CONTROL PLANE                         │
│                                                                         │
│  ┌──────────┐   ┌───────────────┐   ┌───────────────┐   ┌───────────┐  │
│  │  Task    │──▶│   Retriever   │──▶│    Scorer     │──▶│ Selector  │  │
│  │  Intent  │   │ (server→tool  │   │ (the scoring  │   │ (top-k +  │  │
│  │  Parser  │   │  hybrid, set- │   │  function —   │   │ budget,   │  │
│  │          │   │  level)       │   │  §7)          │   │ knapsack) │  │
│  └──────────┘   └───────────────┘   └───────────────┘   └─────┬─────┘  │
│                                                               │        │
│        ┌──────────────┐        ┌────────────────┐      ┌──────▼─────┐  │
│        │   Registry   │        │ Lazy Loader    │      │ Executor   │  │
│        │ (schemas,    │◀──────▶│ (summary pool  │◀─────│ (MCP /     │  │
│        │  embeddings, │        │  → top-k full  │      │  REST      │  │
│        │  cost, auth, │        │  schema promo) │      │  client)   │  │
│        │  health)     │        └────────────────┘      └─────┬──────┘  │
│        └──────────────┘                                      │         │
│                                                              ▼         │
│        ┌─────────────────────────────────────────────┐ ┌───────────┐  │
│        │  Telemetry + Feedback Loop                   │◀│  Outcomes │  │
│        │  (success/failure → signal updates →         │ │  (result, │  │
│        │   scoring weight drift correction)           │ │  cost,    │  │
│        └─────────────────────────────────────────────┘ │  latency)  │  │
│                                                        └───────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
        ▲                                                          ▲
   POST /toolloader/select                                   events → /feedback
```

**Pipeline (one request):**

```text
task text + context + constraints
  → 1. intent parse (cheap, rule + small model)
  → 2. candidate retrieval (server-level routing, then tool-level, set-aware)     [§4.2]
  → 3. scoring of candidates against task (§7 multi-signal equation)              [§4.3]
  → 4. budgeted selection: top-k maximizing marginal utility under token cap      [§4.4]
  → 5. lazy load: summary descriptions in context, full JSON schemas promoted
       only for selected tools                                                    [§4.5]
  → 6. execution + telemetry capture → feedback loop updates signals & weights    [§4.6]
```

---

## 3. Research Grounding

Verified papers (all fetched from the arXiv API 2026-08-17T20:18Z; IDs below are the versioned
records read) and the design implication each imposes.

| Paper | arXiv ID | Pattern it supplies | Design implication for Toolloader |
|---|---|---|---|
| Toolformer: Language Models Can Teach Themselves to Use Tools | 2302.04761v1 | Self-supervised tool-use learning | (lineage) tool selection can be learned from execution signal; justifies the feedback loop over hand-tuned scoring |
| Gorilla: LLM Connected with Massive APIs | 2305.15334v1 | Retrieval-augmented generation for API documentation | Retrieval over API docs beats pure parametric knowledge; motivates the registry's description corpus |
| API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs | 2304.08244v2 | Benchmark + tool-augmented evaluation | Evaluation harness must test: callable detection, retrieval, correctness — not just selection recall |
| ToolLLM: 16,000+ Real-world APIs | 2307.16789v2 | ToolBench, depth-first decision trees with API retriever | Proves scale to tens of thousands of APIs is plausible; retriever→planner two-stage works |
| AnyTool: Self-Reflective, Hierarchical Agents for Large-Scale API Calls | 2402.04253v1 | **Hierarchical retriever** (category → API), solver, self-reflection | Candidate retrieval must be hierarchical (server → tool) and re-activatable when the first selection fails |
| MCP-Zero: Active Tool Discovery for Autonomous LLM Agents | 2506.01056v4 | Active capability acquisition; MCP Zero dataset | Passive schema injection is a ceiling; Toolloader's selection must be recoverable → surfaces the feedback loop as the "active" component |
| Retrieval Models Aren't Tool-Savvy: Benchmarking Tool Retrieval for LLMs | 2503.01763v2 | Tool retrieval benchmark; IR methods underperform | **Bare vector search underperforms** — the exact gap the report calls out; motivates the multi-signal scorer |
| Tool Attention Is All You Need: Dynamic Tool Gating and Lazy Schema Loading | 2604.21816v1 | ISO overlap score; state-aware gating; two-phase lazy schema loader; documents the MCP Tax (10k–60k tokens/turn) | The loader design (§4.5) directly adopts the summary-pool→top-k-promotion pattern; gating over tools generalizes token attention |
| HumanMCP: Human-Like Query Dataset for Evaluating MCP Tool Retrieval | 2602.23367v1 | 2,800 tools / 308 MCP servers paired with user personas | Offline retrieval eval must use persona-varied queries, not one canonical phrasing per tool |
| PORTS: Preference-Optimized Retrievers for Tool Selection | 2607.05441v1 | Pairwise-preference-trained retrieval for tool selection | Scoring weights can be learned from preference pairs mined from telemetry (winner tool vs. runner-up) |
| Tools Are Not Islands: Set-Level Tool Retrieval via Query-Conditioned Hyperedge Prediction | 2607.25718v2 | **Co-selection**: tools co-occur in task-solving sets; hyperedge prediction | Selection must be **set-aware**, not independent top-k per tool — the marginal-utility loop in §4.4 |
| When Lower Privileges Suffice: Over-Privileged Tool Selection in LLM Agents | 2606.20023v2 | Privilege-aware selection; least-privilege optimum | Permissions + auth friction belong in the score: a tool that works without privileges beats one needing elevated access (also §10) |
| Scalable LLM Agent Tool Access in the Cloud | 2607.15593v1 | Cloud-scale MCP gateway: access control, tool recommendation, session-aware routing; hybrid retrieval 98% Top-15 recall; 3,000+ tools; 8.9× selection-time and 23.8× token reduction (paper-reported) | The target-scale architecture: gateway offloads tool recommendation + access control; hybrid retrieval (semantic + lexical/structural) is the retrieval baseline |

**Unverified source citation (flagged, not used for design):** the report's "SING: Synthetic
Intention Graph for Scalable Active Tool" was not found on arXiv (title search 2026-08-17). Its
claimed role — hierarchical server-then-tool retrieval — is covered by verified work (AnyTool
2402.04253v1; set-level retrieval 2607.25718v2; the gateway's server-level routing 2607.15593v1).
If SING is later located, its graph-based intention structure should be diffed against the
set-level co-retrieval design before adoption.

**Numbers discipline:** the "95.0% token reduction" (47.3k→2.4k) and "23.8×" figures are
**paper-reported simulation/production claims**, not independently reproduced by this project. §8
and §13 mandate our own measurement before any public claim.

---

## 4. Core Components

### 4.1 Tool Registry

**Purpose:** single source of truth for every selectable tool. The registry is what makes scoring
possible — a tool with no metadata is unselectable even if semantically relevant.

Per-tool records: stable id, server origin (MCP server or REST endpoint), name + description
corpus (long form for indexing + short summary for lazy pool), full JSON schema (never injected
eagerly; stored for promotion), embedding(s), cost profile (price per call, token weight of params),
health signals, permission scope / auth requirements, reliability stats, co-selection statistics
(which tools are used together).

Interfaces used by other components:

| Component | Registry read | Registry write |
|---|---|---|
| Retriever | description corpus, embeddings, server memberships | — |
| Scorer | cost, health, auth, reliability, price | — |
| Loader | full schemas, summaries | — |
| Telemetry loop | — | health, reliability, co-selection stats |

Ingestion is incremental: a connector (MCP client or OpenAPI adapter) diffs server manifests on a
schedule, adds new tools, tombstones removed ones, and re-embeds changed descriptions.

### 4.2 Retriever (candidate generation)

**Purpose:** shrink the full corpus (1,900+ tools) to a small candidate set (target ≤ 40–80) that
the expensive scorer can afford to score. Follows the verified two-level hierarchy: **server-level
routing first, then tool-level retrieval inside the shortlisted servers** (AnyTool pattern), plus a
set-aware second pass:

1. **Server routing.** Embed the task; retrieve the top servers by description overlap (server
   summaries are condensed multi-tool descriptions). Cheaper because it runs over ~hundreds of
   servers, not thousands of tools. Aligns with 2607.15593v1's gateway-side server routing.
2. **Tool retrieval within shortlisted servers.** Hybrid retrieval: dense embeddings over
   tool descriptions + lexical (BM25-style) over names/endpoints, fused (reciprocal-rank fusion).
   This matches the verified hybrid-retrieval result (98% Top-15 recall at cloud scale).
3. **Set-aware second pass (optional, v1.5+).** If telemetry shows common task types are solved by
   tool *combinations*, run the hyperedge-style co-retrieval (2607.25718v2) to pull tools that are
   individually mid-ranked but co-occur with already-retrieved tools. Gate: only if the extra pass
   measurably improves task success beyond independent retrieval (eval in §13), because it costs
   latency.

Retrieval output: candidate list, each with its relevance evidence (matched server, matched fields)
so the scorer can explain its inputs.

### 4.3 Scorer — the product differentiator

**Purpose:** score fitness of each candidate for the *specific* task. This is the component named in
the thesis: "make the scoring function that considers semantic relevance, historical success,
schema-token cost, latency, health, permissions, auth friction, reliability, and price."

The scorer evaluates nine signals (full math in §7):

1. Semantic relevance (embedding + lexical overlap + intent-schema overlap, ISO-style from
   2604.21816v1).
2. Historical success (smoothed success rate from telemetry; cold-start priors).
3. Schema-token cost (how many tokens the schema/summary would consume if loaded; small = better).
4. Latency (expected p50/p95 call latency).
5. Health (registry health score; unhealthy tools heavily discounted or hard-excluded).
6. Permissions (privilege level required; least-privilege tools preferred — 2606.20023v2).
7. Auth friction (orders of magnitude: no auth < stored token < interactive/OAuth challenge).
8. Reliability (error-rate, flakiness, timeout rate, 7-day and 30-day windows).
9. Price (per-call cost; zero-cost local tools beat paid APIs all else equal).

Hard constraints (from the request's `constraints` block) are applied **before** soft scoring:
`max_tokens` caps the total loadable payload; `require_auth: false` excludes any tool whose auth
friction exceeds the allowed level.

Signals are normalized to [0,1], combined with a learned weight vector (see §7.4), and the top
candidates proceed to the selector with their per-tool signal vector attached (so downstream
tooling can explain any decision — every score is decomposable, never a mushy single number).

### 4.4 Selector (budgeted top-k with marginal utility)

**Purpose:** choose the final small set (report default: load 3 tools; request `max_tools` up to
configurable cap) under the token budget — **as a set, not as independent top-k** (2607.25718v2).

Algorithm (greedy submodular approximation):

```text
selected = {}
remaining_budget = min(request.max_tokens, global_cap) - fixed_overhead
loop until selected.size == request.max_tools or remaining_budget <= 0:
    for tool in candidates - selected:
        marginal = score(tool) + Σ co_selection_bonus(selected, tool)
        cost = schema_token_cost(tool) if (summary already in pool) else full_schema_cost(tool)
        utility[tool] = marginal / cost            # efficiency frontier
    pick tool with max utility where cost <= remaining_budget
    remaining_budget -= cost(tool); selected += tool
```

- Co-selection bonus is its own learned signal, seeded from telemetry (tools used together in
  successful tasks) — the hyperedge idea.
- If no tool fits the remaining budget, stop (never overspend the constraint).
- Output includes per-tool `context_cost` (exactly what the report's response shape shows) so the
  caller sees the total context price before any tool executes.

### 4.5 Lazy Loader (context injection without the MCP tax)

**Purpose:** deliver tool definitions to the model **only as needed**, eliminating eager
full-schema injection (the verified 10k–60k tokens/turn tax; 2604.21816v1).

Two phase loader:

- **Phase 1 — summary pool (always in context):** every *selected* tool contributes its short
  summary (75–150 tokens) plus name/id. The model can reason and plan against the pool.
- **Phase 2 — schema promotion (on first call):** when the model issues the first call for a tool,
  the loader promotes the full JSON schema for that one tool into context for the remainder of the
  turn. Fallback: if the model's call is malformed because it lacked the schema, the runtime
  returns a `SCHEMA_REQUIRED` retry signal instead of failing the task.

Token accounting is central: the loader tracks (a) summary pool size, (b) promoted schemas, (c)
per-turn total, and feeds both to the selector's cost model (next request benefits) and to the
observability dashboard (so the MCP tax is measured per deployment, not assumed).

Alternative injection strategies (interfaces, not v1 commitments): JSON-schema compression /
pruned-parameter schemas, tool-call token-allowance tuning, and KV-cache-aware placement if the
runtime exposes it.

### 4.6 Execution, Telemetry, and Feedback Loop

**Purpose:** close the loop so the scorer and retriever improve from real outcomes — the component
that makes "scoring function" honest.

- On every executed tool call, capture: tool id, task type, outcome (success / failure / timeout /
  malformed-call), latency, token cost, auth path used, caller tenant (v1: single-tenant).
- The Telemetry Store (see §6) drives:
  - success-rate updates (signal 2) with exponential time-decay windows;
  - reliability windows (signal 8);
  - co-selection statistics (selector bonus);
  - preference-pair extraction for weight learning (PORTS-style: successful selection pair vs. the
    runner-up that would have been chosen), consumed by the weight tuner (§7.4).
- **Drift guard:** if a tool's health or reliability collapses (e.g. 7-day success < 0.5), the
  scorer is expected to down-weight it *before* the caller hits failures — checked by a scheduled
  job, not lazily at request time.
- Feedback is asynchronous and non-blocking: the select endpoint returns immediately; telemetry
  arrives via `POST /toolloader/feedback` or an event bus.

### 4.7 Access Control and Auth Friction Layer

- Credential/auth handling remains with the MCP server or gateway — Toolloader scores and orders,
  never stores secrets (v1).
- Auth friction is derived from registry metadata (none / bearer token / OAuth interactive),
  not probed at selection time.
- Least-privilege bias (2606.20023v2): when two tools accomplish the same task class, the lower
  privilege tool wins the tie. This is a scoring *preference*, applied after hard constraint
  filtering.

---

## 5. API Contract

### 5.1 `POST /toolloader/select` — the core endpoint

Input (matching the report, extended):

```json
{
  "task": "create_github_issue",
  "context": "repo: foo/bar",
  "max_tools": 5,
  "constraints": {
    "max_tokens": 10000,
    "require_auth": false,
    "required_servers": ["github"],
    "excluded_servers": []
  }
}
```

Response:

```json
{
  "request_id": "sel_01J...",
  "selected": [
    {
      "tool": "github/create_issue",
      "server": "github",
      "score": 0.94,
      "signal_breakdown": {
        "semantic": 0.98, "success": 0.99, "cost": 0.72,
        "latency": 0.61, "health": 1.0, "permissions": 0.8,
        "auth_friction": 1.0, "reliability": 0.99, "price": 0.9
      },
      "context_cost": 847,
      "schema_cost_if_full": 2410,
      "latency_ms": 120,
      "success_rate": 0.99
    }
  ],
  "total_context_tokens": 847,
  "estimated_cost": 0.002,
  "budget_remaining": 9153,
  "retrieval_stats": { "candidates": 47, "servers_shortlisted": 4, "retrieval_ms": 31 }
}
```

Error semantics:

| Code | When | Caller action |
|---|---|---|
| 422 | malformed request / unknown constraint | fix request |
| 404 (tool not found) vs 200 empty | explicit tool requested but absent vs. nothing selected | retry with different task wording |
| 429 | rate limit | respect `Retry-After` |
| 503 | registry unhealthy / scorer unavailable | fall back to caller's static tool list (degraded mode documented in §9) |

Guidelines: idempotent under identical input (same request body → deterministic selection when
telemetry is frozen); request ids for audit; `task` free-text max length documented (e.g. 4k chars).

### 5.2 Supporting endpoints

| Endpoint | Purpose |
|---|---|
| `POST /toolloader/registry/sync` | trigger incremental registry refresh from connected servers |
| `POST /toolloader/feedback` | submit telemetry (outcome, latency, tokens) for a request_id |
| `GET  /toolloader/tools/{id}` | inspect a tool record (schema, signals, health) |
| `GET  /toolloader/stats` | per-server/tool token tax + success-rate dashboard data |
| `GET  /toolloader/health` | liveness: registry, scorer, loader, budget gate |

---

## 6. Data Model

PostgreSQL (prod) / SQLite (MVP). Core tables:

```text
servers(id, name, protocol[mcp|rest], base_url, auth_mode, status, synced_at)
tools(id, server_id FK, name, long_description, short_summary, json_schema,
      embedding vector, slot_cost_tokens, price_per_call, created_at, updated_at)
tool_sigs(tool_id FK, latency_p50, latency_p95, success_7d, success_30d,
          reliability_7d, reliability_30d, health, last_seen_ok)
auth_meta(tool_id FK, friction_level[none|token|oauth], privilege_level, scopes)
co_occurrence(tool_a FK, tool_b FK, success_count, fail_count, updated_at)
selections(request_id PK, task_hash, task_text, selected_json, context_tokens,
           cost_estimate, created_at)
telemetry(id PK, request_id FK, tool_id FK, outcome[ok|fail|timeout|malformed],
          latency_ms, tokens_used, error_class, created_at)
weights(signal_name PK, weight, confidence, updated_at)   -- learned weight vector
```

Notes:

- `tools.embedding` uses pgvector (or a side vector store in MVP); re-embedding is a
  registry-sync side effect.
- `selections` + `telemetry` are append-only; retention policy per tenant (keeps the data-licensing
  path open, §1.2).
- No credentials stored. Ever. `auth_meta` is metadata only.

---

## 7. Scoring Function (specification)

### 7.1 Signals

Let `t` be a candidate tool and `q` the task (text + context + constraints). Define nine normalized
signals `f_i(t, q) ∈ [0,1]`:

| i | Signal | Definition |
|---|---|---|
| 1 | semantic relevance | `w_e·cos(emb(q), emb(t)) + w_l·lexical_overlap(q, t)` with ISO-style intent-schema overlap (2604.21816v1) as a secondary term |
| 2 | historical success | smoothed success rate: `successes/(successes+failures)` with Laplace prior `α`; cold start `f_2 = prior` |
| 3 | schema-token cost | `1 − min(1, schema_tokens / token_normalizer)` — the *inverse* of token weight (smaller is better) |
| 4 | latency | `clip((p95_up − latency) / (p95_up − p50_lo))` truncated to [0,1] |
| 5 | health | registry health score; if `health < HARD_MIN` the tool is excluded, not just down-weighted |
| 6 | permissions | `1` if least-privilege class for the task class, else scaled by privilege delta (2606.20023v2 bias) |
| 7 | auth friction | `1` if none, `0.6` if stored token, `0.2` if interactive challenge (configurable) |
| 8 | reliability | `1 − error_rate` over the 7/30-day windows, floored at 0 |
| 9 | price | `1 − min(1, price_per_call / price_normalizer)`; zero-cost local tools score 1 |

### 7.2 Composition

```text
score(t, q) = Σ_i w_i · f_i(t, q)           with Σ_i w_i = 1, w_i ≥ 0
```

Weights default to a principled seed (semantic 0.30, success 0.20, cost 0.15, health 0.10,
latency/reliability 0.10, permissions/auth/price 0.15 split) and are **learned** thereafter (§7.4).

Hard constraints are applied first (they can zero-out a candidate regardless of score):

```text
eligible(t) =  schema_cost(t) ≤ remaining_budget
            ∧ (require_auth ? auth_ok(t) : true)
            ∧ server ∈ required_servers if specified
            ∧ server ∉ excluded_servers
            ∧ health(t) ≥ HARD_MIN
```

### 7.3 Selection objective (set-level, not per-tool)

Because tools co-operate (2607.25718v2), the selector maximizes total utility of the *set* S under
budget B:

```text
maximize  Σ_{t∈S} w·f(t,q) + Σ_{(a,b)∈S²} β(a,b)
subject to Σ_{t∈S} injected_tokens(t) ≤ B,  |S| ≤ max_tools
```

Greedy approximation (each step picks argmax marginal-utility-per-token) is the v1 algorithm;
exact knapsack is only warranted if evals show greedy leaves >5% of utility on the table.

### 7.4 Weight learning (the "learnable" guarantee)

- **Offline (batch):** daily job mines telemetry for preference pairs — for a task that succeeded
  with tool set S vs. the runner-up set S′ that would have been chosen at that time — and updates
  weights with a pairwise-ranking objective (PORTS-style, 2607.05441v1).
- **Online (optional, v1.5):** weight updates are **not** applied per request; they land through
  the same scheduled job to keep selection deterministic within a window (auditability over
  adaptivity).
- **Discipline:** weight drift is logged; any weight change beyond its confidence bound triggers a
  review event (no silent retraining drift). The Knee optimizer (sibling `specs/knee/architecture.md`)
  is the designated engine for the quality/cost optimization loop.

---

## 8. Token Cost Model

### 8.1 The tax we are removing

Per 2604.21816v1: eager full-schema injection in multi-server workflows costs roughly **10k–60k
tokens/turn** (MCP/Tools Tax), inflates KV cache, degrades reasoning near ~70% context utilization,
and turns token budgets into recurring cost.

### 8.2 Our per-turn budget equation

```text
per_turn_tokens = base_prompt + Σ_{t∈S} summary_tokens(t) + Σ_{t∈called} schema_tokens(t)
                  + execution transcript tokens
```

Where the first two terms are the selector's responsibility (`total_context_tokens` in the
response) and schema promotions are the loader's. Target (stretch, measured): summary pool ≤ 500
tokens for a 3-tool selection; schemas promoted only on actual calls.

### 8.3 What we must measure ourselves (§13 gates this)

- Per-deployment baseline eager-injection cost vs. Toolloader lazy cost on the same workload
  (mirror test: same prompts, instrumented counting of tokens actually in context).
- KV-cache / context-utilization effect only if the runtime exposes it; otherwise report the
  token-level delta, not a projected utilization number.
- The paper-reported figures (95.0%, 23.8×) are **aspirational targets for our own harness**, not
  pre-endorsed claims.

---

## 9. Reliability, Availability, and Ops

| Concern | Design |
|---|---|
| Scorer failure | 503 with fallback mode: caller uses its static tool list; degraded mode is a first-class API behavior, not an emergency |
| Registry staleness | incremental sync + heartbeat; tools not seen in 2× expected interval are marked `stale`, health decays |
| Health collapse | drift guard job down-weights before callers suffer (disabled only if the guard itself is down) |
| Latency budget | retrieval ≤ 100ms p95, scoring ≤ 100ms p95 for ≤ 80 candidates, select ≤ 20ms; total select p95 ≤ 250ms (matched against the report's per-tool 120ms example) |
| Circuit breaker | per-server failure count triggers backoff; the breaker is *input* to the health signal (§4.3) so selection itself avoids it |
| Fallback chains | a tool that fails may be replaced by the next-best eligible candidate **within the same request budget** if the caller opts in; chain configurable per server class (aligns with the sibling `specs/fallbackgraph` design) |
| Cache | retrieval embeddings + server routing cached (Redis) with TTL; scoring never cached (must react to live signals) |
| Observability | `GET /toolloader/stats` reports the measured MCP tax per server — the number we actually own |

---

## 10. Security Posture

1. **Least privilege by default** — scoring prefers the minimum-privilege tool that satisfies the
   task (2606.20023v2); constraint `require_auth` is enforced as a hard filter.
2. **No secret storage** — credentials stay at the MCP server/gateway; Toolloader persists only
   `auth_meta` metadata.
3. **Description-as-prompt-injection risk** — tool descriptions and summaries are third-party
   content that will be injected into model context. v1: strip executable-looking content from
   summaries at ingest; document the residual risk; adversarial eval in §13.
4. **Audit trail** — every selection records request_id, task hash, chosen set, and per-signal
   breakdown (explainability + misuse detection).
5. **Tenant isolation** (when multi-tenant lands) — telemetry and selection history partitioned;
   the data-licensing product gets only aggregated, de-identified statistics.

---

## 11. Technology Stack

| Layer | Choice | Why (and verified constraints) |
|---|---|---|
| API | FastAPI (async) | report direction; async needed for parallel candidate scoring |
| Storage | PostgreSQL + pgvector (MVP: SQLite + in-memory vectors) | relational core + embeddings co-located |
| Cache | Redis | retrieval/summary pool
 caching |
| Embeddings | sentence-transformer / embedding API (registry re-embed) | ISO-style overlap (2604.21816v1) is sentence-embedding based |
| Lexical | BM25 index (pg FTS or tantivy) | hybrid retrieval baseline (2607.15593v1 hybrid recall) |
| Rerank/scoring | in-process Python (numpy) for v1; Rust/compiled only if p95 slips past 250ms | scoring latency is our SLO |
| MCP client | std MCP client / gateway-side integration | protocol consolidation lives at the gateway per 2607.15593v1 |
| Optimizer | Knee (sibling spec) | quality/cost optimization oracle per the report |
| Deploy | containerized; control plane stateless behind the API | selection is horizontally scalable; registry/telemetry stateful |

---

## 12. Implementation Phases (aligned with the report's path to market)

### Phase 1 — MVP (weeks 1–2): "50 tools, honest numbers"
- SQLite registry + embeddings; retriever (server→tool hybrid) over 50 hand-picked tools.
- Scorer with the nine signals at seed weights; selector greedy with token budget.
- Lazy loader: summary pool + top-k schema promotion (subsumes the report's 3-loader split into
  `retrieve/score/load` — internal service boundaries, single deployable).
- `POST /toolloader/select` + `/feedback`; SQLite telemetry.
- **Gate:** local mirror test on 50 real tasks shows per-turn token reduction ≥ 10× vs eager
  injection, measured by our own counter (§8.3). No public claim before this.

### Phase 2 — Core (weeks 3–4): "MCP gateway integration"
- PostgreSQL + pgvector; Redis; incremental registry sync across real MCP servers; access-control
  metadata ingestion.
- Feedback loop job (weight learning offline); health drift guard.
- **Gate:** retrieval eval on HumanMCP (2,800 tools / 308 servers) + Tool-Savvy-style recall
  (target: ≥ 85% Top-15 recall before shipping the gateway adapter).

### Phase 3 — Public API (month 2)
- Multi-tenant isolation, rate limiting, billing metering (report's $0.0001/selection pricing
  assumes per-request cost accounting — `selections.estimated_cost` is the metering unit).
- **Gate:** a/b service-level experiment with a coding-agent partner; success = task success not
  worse (non-inferiority ±2%) while context tokens drop ≥ 10×.

### Phase 4 — Integrations & enterprise (months 3–6)
- Set-level co-retrieval (hyperedge) if evals justify; online-but-gated weight adaptation;
  enterprise scoring functions (per-tenant weight sets, custom signal plugins).

---

## 13. Evaluation Plan and Gates

The venturelab norm (from AGENTS.md): a claim is real only behind a reproducible, logged gate on
fixed harnesses. Toolloader's gates:

| Gate | Harness | Metric | Bar |
|---|---|---|---|
| G1 retrieval quality | HumanMCP + Tool-Savvy-style eval on fixed query sets | recall@Top-15, nDCG@10 | ≥ 85% (Top-15) |
| G2 token economics | mirror test on 50 real tasks (Phase 1) / 200 (Phase 2) | measured per-turn context tokens with/without loader | ≥ 10× reduction |
| G3 selection quality | AnyToolBench-style protocol + in-house task suite | task success / pass rate | non-inferior to full-schema baseline (±2%) while G2 holds |
| G4 cost quality | Knee optimizer on the selection log | realized $/successful-task | decreasing across the weight-learning windows |
| G5 safety | adversarial eval: injected-description prompts, over-privilege queries | injection success rate, privilege escalation attempts | 0 high-severity incidents in the fixed suite |
| G6 determinism | replay: same frozen telemetry + input → identical selection | exact match | 100% within a weight window |

Every gate run writes a content-addressed record (hash of harness + data snapshot + result) so a
later diff is auditable. Figures like 23.8× are only referenced as paper-reported until G2 on our
own deployment reproduces the magnitude.

---

## 14. Risks and Open Questions

1. **SING unverified** — the report's headline retrieval citation does not exist on arXiv (as of
   2026-08-17). Design already covers its claimed role with verified alternatives; if SING resurfaces
   with a graph-only advantage, re-open §4.2.
2. **Source-report number reliability** — star counts in the report were materially wrong (52 vs
   "500"; 92,485 vs "5,000") and we corrected them from the live API. Treat the report's other
   quantitative claims as unverified until G-gated.
3. **Projection vs. measurement** — 95.0% and 23.8× are paper-reported; our G2 gate exists
   precisely so we never repeat them as our own results without measurement.
4. **Embedding choice drift** — re-embedding policy must be pinned (model version in registry
   records) or retrieval evals and production diverge.
5. **Cold start** — new tools without telemetry lean on priors; mis-selection early costs the
   caller. Mitigation: conservative prior + explicit `require_auth`/budget constraints the caller
   can impose.
6. **Co-selection data sparsity** — hyperedge stats need volume; Phase 4 explicitly gates on
   coverage before enabling the set-aware pass.
7. **Prompt-injection via tool metadata** — permanent residual risk; G5 owns it and §10.3 sets the
   baseline posture.

---

## 15. References (verified via arXiv API / GitHub API, 2026-08-17T20:18Z)

1. Schick et al. — *Toolformer: Language Models Can Teach Themselves to Use Tools*, arXiv:2302.04761v1.
2. Patil et al. — *Gorilla: Large Language Model Connected with Massive APIs*, arXiv:2305.15334v1.
3. Li et al. — *API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs*, arXiv:2304.08244v2.
4. Qin et al. — *ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs*, arXiv:2307.16789v2.
5. Qin et al. — *AnyTool: Self-Reflective, Hierarchical Agents for Large-Scale API Calls*, arXiv:2402.04253v1.
6. MCP-Zero authors — *MCP-Zero: Active Tool Discovery for Autonomous LLM Agents*, arXiv:2506.01056v4.
7. *Retrieval Models Aren't Tool-Savvy: Benchmarking Tool Retrieval for Large Language Models*, arXiv:2503.01763v2.
8. *Tool Attention Is All You Need: Dynamic Tool Gating and Lazy Schema Loading for Eliminating the MCP/Tools Tax in Scalable Agentic Workflows*, arXiv:2604.21816v1.
9. *HumanMCP: A Human-Like Query Dataset for Evaluating MCP Tool Retrieval Performance*, arXiv:2602.23367v1.
10. *PORTS: Preference-Optimized Retrievers for Tool Selection with Large Language Models*, arXiv:2607.05441v1.
11. *Tools Are Not Islands: Set-Level Tool Retrieval for LLM Agents via Query-Conditioned Hyperedge Prediction*, arXiv:2607.25718v2.
12. *When Lower Privileges Suffice: Investigating Over-Privileged Tool Selection in LLM Agents*, arXiv:2606.20023v2.
13. *Scalable LLM Agent Tool Access in the Cloud*, arXiv:2607.15593v1.
14. GitHub — MikkoParkkola/mcp-gateway (stars: 52, fetched 2026-08-17).
15. GitHub — punkpeye/awesome-mcp-servers (stars: 92,485, fetched 2026-08-17).
16. (Unverified) "SING: Synthetic Intention Graph for Scalable Active Tool" — no arXiv record found 2026-08-17; retained here only as the report's citation.

*End of architecture spec. Machine-proposed from the source report + verified external anchors;
not yet human-reviewed. Next action: Phase 1 MVP + G2 gate.*