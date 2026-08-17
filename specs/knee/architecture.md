# KNEE — Technical Architecture

*Generated: 2026-08-17T20:24:00Z · Source: `reports/knee/report.md` · Version: 1.0*

---

## 0. Status and Provenance — read this first

This specification is **machine-proposed**, derived from the VentureLab KNEE report
(`reports/knee/report.md`) and an arXiv verification pass run 2026-08-17T20:2xZ. It is
**not** PROVED or human-adjudicated. Every load-bearing external claim carries its verified
status below. Where the source report could not be verified, this document says so instead of
repeating the claim.

| Claim in source report | Verification result |
|---|---|
| "Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey" (2026) exists | **VERIFIED** — arXiv 2603.04445v2 (submitted 2026-02-23); systematic survey of routing paradigms (difficulty, preferences, clustering, UQ, RL, cascading) |
| "Towards Cost-effective LLMs Routing with Batch Prompting" (SeqRoute) exists | **NOT VERIFIED** — no matching arXiv record found (title search 2026-08-17, arXiv API + Semantic Scholar both attempted). Treated as unconfirmed; nearest real anchors: budget-aware routing covered in 2502.00409, FrugalGPT 2305.05176, RouteLLM 2406.18665 |
| "The Capability Frontier: Benchmarks Miss 82% of Model" exists | **VERIFIED with title correction** — arXiv 2606.26836v1, "The Capability Frontier: Benchmarks Miss 82% of Model Performance" (2026-06-25). 82% is error-rate reduction from oracle-selection across models+generations; SOTA accuracy matched at 85% cost reduction. The paper's core construct is a Pareto frontier over models at each cost level — the same construct KNEE operationalizes per task |
| Competitor "LiteLLM routing, load-balancing" | **PLAUSIBLE** — BerriAI/litellm is a real gateway project; no quality-cliff analysis feature is documented in its public feature set |
| Competitor "RouteLLM cost-aware routing" | **VERIFIED as real research project** — arXiv 2406.18665v4 (Ong et al. 2024); routers trained on preference data, >2x cost reduction at equal quality. It routes between a strong/weak pair; it does not publish per-task cost-quality curves or cliff locations |
| Monopolization risk from OpenRouter/Artificial Analysis adding this feature | **REAL, LOW probability in v1** — OpenRouter is a broker without an optimization layer (report's own gap analysis); Artificial Analysis publishes aggregate benchmarks, not per-task cliffs |

**Design posture derived from the thesis:** the product is not "another router". Routers
(Prae: RouteLLM, Hybrid LLM, FrugalGPT cascades, LiteLLM passthrough) decide *which model to
call given a budget or quality bar*; KNEE answers the question routers take as input: **where
does the success-vs-cost curve for this task actually cliff, and which model is the cheapest
one that clears the user's success bar with confidence?** Everything below serves that one
differentiator.

**Research posture that constrains the design:**
- **Routing only pays when a cliff exists and failure is predictable** (2608.06607): the paper
  shows routing helps only if (a) the cheaper model fails often enough and (b) those failures
  are predictable from observable signals. KNEE must therefore *detect* whether a cliff exists
  for a task and **abstain** when it does not — an honest "no cliff / insufficient data" answer
  is a feature, not a failure.
- **Static routing can beat cascades** (2602.09902): in the provider-user game analysis, the
  optimal routing policy is frequently static — a fixed model choice per task class. This
  validates KNEE's core output (a single recommended model per task+bar) rather than a cascade
  policy; cascades remain an opt-in mode.
- **Single-model, single-run evaluation understates capability** (2606.26836): KNEE must
  normalize evaluation protocol (sample count, generation budget, temperature, tool budget)
  per (task, model) or its curve estimates are protocol artifacts, not model facts.
- **Evaluation is protocol-dependent** (2606.17930): performance varies strongly with
  inference compute. KNEE's eval harness must fix and record the protocol per observation.

---

## 1. Scope

### 1.1 Goals

1. Given a task and a minimum success bar, return the **cheapest model whose estimated success
   clears the bar with confidence** — the "knee" of the task's cost-quality curve.
2. Report the **cliff**: how much success is lost by stepping one model cheaper, so the user
   can consciously accept or reject the trade.
3. Make the curve **empirical and compounding**: every opted-in real execution becomes an
   observation that tightens the estimate.
4. Be **honest under uncertainty**: abstain (or degrade confidence) when observations are too
   sparse to distinguish models — never fabricate a recommendation from noise.
5. Stay **universal**: task taxonomy and model registry are data, not code; any model, any
   provider, any task type slots in without a release.
6. Operate as the **intelligence layer routers consume**: expose curve snapshots, cliff
   metrics, and per-threshold recommendations as machine-readable outputs that LiteLLM,
   OpenRouter proxies, and agent runtimes can ingest.

### 1.2 Non-goals (v1)

- Not a routing gateway — KNEE does not execute the call; integration adapters (INI LiteLLM
  hook) execute and optionally report outcomes.
- Not a benchmark suite — it consumes eval results; the task-type golden sets are curated data
  assets, not the product.
- Not a billing/credit broker — pricing is ingested from provider catalogs.
- No cross-tenant pooling of *details* in v1; anonymous aggregate curve statistics are
  explicitly the data-licensing asset and must be designed as such from day one.
- No multi-provider failover orchestration; that belongs to FallbackGraph (sibling spec).

---

## 2. System Overview

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                            KNEE CONTROL PLANE                              │
│                                                                            │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐                  │
│  │   Task      │──▶│   Model      │──▶│   Evaluation    │                  │
│  │  Classifier │   │   Registry   │   │    Engine       │                  │
│  │  (task_type │   │  (models,    │   │  (probes →      │                  │
│  │   + aliases)│   │   pricing,   │   │   observations) │                  │
│  └──────┬──────┘   │   versions,  │   └────────┬────────┘                  │
│         │          │   health)    │            │                           │
│         │          └──────┬───────┘            ▼                           │
│         │                 │          ┌─────────────────┐                   │
│         └─────────────────┴─────────▶│   Knee Engine    │                   │
│                                      │  (curve fit +   │                   │
│                                      │   knee/cliff    │                   │
│                                      │   detection)    │                   │
│                                      └────────┬────────┘                   │
│                                               │                           │
│        ┌──────────────────────┐        ┌──────▼──────┐   ┌──────────────┐  │
│        │  Feedback Ingest     │◀───────│  History &   │◀──│  Admin /     │  │
│        │  (opted-in outcomes  │        │  Compare API │   │  Governance  │  │
│        │   from real runs)    │        └──────────────┘   │  (staleness, │  │
│        └──────────────────────┘                          │   drift,      │  │
│                                                          │   pricing     │  │
│                                                          │   sweeps)     │  │
│        ┌──────────────────────┐                           └──────────────┘  │
│        │  Batch Orchestrator  │  evaluates budgets across task types        │
│        └──────────────────────┘                                             │
└────────────────────────────────────────────────────────────────────────────┘
        ▲                                                      
   POST /knee                     events → /knee/feedback · hooks → LiteLLM
```

**Pipeline for one request:**
1. `POST /knee` → Task Classifier resolves `task_type` (or user supplies it explicitly).
2. Knee Engine loads the current observation set for `(task_type, model_set)` from the
   observation store, applies freshness/currency rules, recomputes or fetches the curve
   snapshot.
3. Curve estimator sorts models by cost, estimates success with CIs, detects the knee and the
   threshold-specific cliff.
4. Response returns recommendation + next-cheaper + cliff + confidence, or an explicit
   `insufficient_data` / `no_cliff` status.
5. Every response is written to the recommendation audit log (inputs, estimate version,
   model versions, params).

---

## 3. Core Components

### 3.1 Task Classifier

**Purpose:** resolve a free-text task description into a canonical `task_type` (the unit at
which KNEE maintains curves).

**Interface:**
```
POST /classify
```
**Input:**
```json
{
  "task_description": "fix the segfault in our auth service and add a regression test",
  "context": {"repo_language": "rust", "agent": "coding-agent-v2"}
}
```
**Output:**
```json
{
  "task_type": "repo_bugfix",
  "confidence": 0.91,
  "aliases": ["bugfix", "se_repo_bugfix"],
  "suggested_eval_suite": "se-metrics-v1"
}
```

**Implementation:**
- Deterministic first: alias map + keyword/embedding classifier (small embedding model) with
  cache; LLM-assisted fallback with a strict JSON schema for novel long-tail tasks.
- Task types are first-class rows in `task_types` with: canonical name, description, owner,
  golden eval suite id, default eval sample budget, default `minimum_success` suggestion,
  freshness TTL. Users may register custom task types (tenant-scoped).
- Classification failure → 422 with the nearest candidate types, never a silent guess.

### 3.2 Model Registry

**Purpose:** canonical, versioned catalog of every model (and model+provider+version
offering) KNEE can reason about.

**Interface:**
```
GET  /models
GET  /models/{id}
POST /models            (admin: manual add)
POST /models/sync       (admin: pull from provider catalogs)
```
**Output (GET /models/{id}):**
```json
{
  "id": "openrouter:deepseek/deepseek-v3",
  "provider": "openrouter",
  "model": "deepseek-v3",
  "version": "b2026-07",
  "pricing": {"input_per_mtok": 0.25, "output_per_mtok": 1.25},
  "capabilities": ["tool_use", "json_mode", "context_128k"],
  "health": {"status": "ok", "latency_p50_ms": 1800, "last_checked": "2026-08-17T19:00:00Z"},
  "status": "active"
}
```

**Implementation:**
- SQLite (MVP) → PostgreSQL (production) `models` + `model_versions` + `pricing_snapshots`.
- Source-of-truth sync: Dell/LLMDeals + OpenRouter catalog (`GET /models`), merged with
  manual overrides; hourly price sync job bumps `pricing_snapshots` and invalidates curve
  caches touched by the changed model.
- **Version pinning is load-bearing:** every recommendation references
  `models.id` (which embeds provider+model+version) so curve estimates stay reproducible when
  a provider silently updates a model. Deprecated models never serve recommendations; they
  remain queryable in history.

### 3.3 Evaluation Engine (the measurement plant)

**Purpose:** produce the raw (task, model, outcome, cost, protocol) observations that feed the
Knee Engine. This is the component that makes KNEE *empirical* instead of benchmark-advisory.

**Interface (internal):**
```
POST /internal/evals/run        (schedule a probe batch)
GET  /internal/evals/status/{batch_id}
```
**Observation record produced:**
```json
{
  "id": "obs_9f3c",
  "task_type": "repo_bugfix",
  "model_id": "openrouter:deepseek/deepseek-v3",
  "success": true,
  "cost_usd": 0.017,
  "latency_ms": 2100,
  "tokens": {"in": 1200, "out": 340},
  "protocol": {"temperature": 0.2, "max_tokens": 2048, "attempts": 1, "suite": "se-metrics-v1"},
  "source": "eval_run:eval_0421" ,
  "observed_at": "2026-08-17T19:40:00Z"
}
```

**Implementation:**
- Golden eval suites per task type: seed sets with human-labeled ground truth (from the
  curated task-type onboarding), plus protocol metadata. Samples are small (n≈10–20 per
  (task,model) per eval cycle in MVP; budgets scale with confidence needs).
- Scheduler: a worker pool executes probe batches across providers with per-provider rate
  limits; spends the per-tenant/per-task eval budget where uncertainty is highest
  (uncertainty-directed sampling — same principle as active learning).
- Protocol is recorded per observation (2606.17930) so curve comparisons never mix
  protocols silently.
- Cost is measured from actual token usage × the *pricing snapshot at call time*, not the
  current price — historical curves stay comparable when prices move.

### 3.4 Knee Engine (the computational core)

**Purpose:** given observations for a (task_type, model_set), return the curve, the knee, the
recommendation under a success bar, and the cliff.

**Interface (the product's core endpoint):**
```
POST /knee
```
**Input:**
```json
{
  "task": "repo_bugfix",                 // or free text w/ classifier fallback
  "models": "auto",                       // or explicit list,
  "minimum_success": 0.90,                // required
  "constraints": {"max_cost": 1.00, "max_latency_ms": 60000},  // optional
  "confidence_level": 0.95                // optional, default 0.95
}
```
**Output:**
```json
{
  "task_type": "repo_bugfix",
  "recommended": "cheap-model-x",
  "success_rate": 0.923,
  "success_rate_ci": [0.89, 0.95],
  "cost_per_task": 0.017,
  "next_cheaper": {"model": "tiny-model-y", "success_rate": 0.694},
  "cliff": 0.229,
  "cliff_confidence": "high",
  "curve": [{"model": "tiny-model-y", "cost": 0.009, "success": 0.694},
            {"model": "cheap-model-x", "cost": 0.017, "success": 0.923}],
  "status": "ok"
}
```
Abstention statuses: `"status": "insufficient_data"` (zero/too-few observations for the
decision) or `"status": "no_cliff"` (cheaper model clears the bar too — recommendation is the
cheapest candidate; cliff=0).

**Algorithm (specified — §4 below):** curve estimation with Wilson confidence intervals →
monotone cost ordering → constrained argmin over the success lower bound → Kneedle knee
detection cross-checked by trade-off utility → cliff = success drop to the next cheaper model
→ confidence/abstention decision.

### 3.5 Feedback Ingest

**Purpose:** the compounding-data flywheel — opted-in consumers report the real outcome of
routed calls.

**Interface:**
```
POST /knee/feedback
```
```json
{
  "recommendation_id": "rec_f8a1",
  "model_id": "openrouter:deepseek/deepseek-v3",
  "success": false,
  "cost_usd": 0.021,
  "latency_ms": 3100,
  "protocol": {"temperature": 0.2, "attempts": 3},
  "reporter": "tenant_x",     // tenant-scoped; never raw prompts in v1
  "observed_at": "2026-08-17T20:01:00Z"
}
```

**Implementation:**
- LiteLLM hook adapter captures calls made *because of* a KNEE recommendation and posts
  outcomes; SDK integration for native users.
- Validation: `recommendation_id` must exist in the audit log; success semantics per task type
  (some suites define success = verifier passed, others = user-judged); per-tenant rate caps.
- Aggregation tier: per-tenant stats are private; only anonymous aggregate curves feed the
  shared model-selection intelligence (the licensing asset).

### 3.6 Batch Orchestrator

**Purpose:** amortize evaluation budgets across many task types at once, and answer
batch planning questions ("which model for each of these 300 tasks under a total budget?").

**Interface:**
```
POST /knee/batch
```
```json
{
  "tasks": [{"task": "repo_bugfix", "minimum_success": 0.90}, ...],
  "constraints": {"max_total_cost": 50.0}
}
```
**Output:** per-task recommendations + aggregate projected cost, or a budget-feasible
assignment when `max_total_cost` binds (knapsack over task priorities).

### 3.7 History & Compare

**Purpose:** make the curve a first-class, inspectable, licensable artifact.

```
GET /knee/{task_type}                          → current curve + knee + latest snapshot
GET /knee/compare?models=a,b,c&task=repo_bugfix→ per-model estimates under one protocol
GET /knee/history/{task_type}?since=...        → versioned curve snapshots, drift deltas
```

### 3.8 Admin / Governance

**Purpose:** keep estimates honest over time — the silent killer of cliff-prediction products.

- **Staleness sweeper:** per (task, model) freshness TTL; expired estimates are marked
  `stale`, excluded from recommendations, and re-evaluated on the next budget cycle.
- **Drift detection:** when fresh observations diverge from a published snapshot beyond the
  CI, the snapshot is flagged, the curve version bumps, and subscribers get a webhook.
- **Price-change recompute:** hourly sync bumps `pricing_snapshots`; any touched curve cache is
  invalidated; recommendations are re-computed lazily at read time (curve is stored as
  success-estimates + model ids; cost is joined at read time so price changes never corrupt
  stored math).
- **Audit:** every recommendation is logged with the exact input, estimate version, model
  versions, params, and the curve snapshot id it was computed from.

---

## 4. The Knee Algorithm

### 4.1 Curve estimation

Let candidates for (task_type, model_set) be the set of active models with ≥ 1 observation.
For each model `m` with `n_m` observations and `k_m` successes:

- Point estimate: `p̂_m = k_m / n_m`.
- Interval: **Wilson score interval** at confidence `z` (default 95%):
  `LB_m = (p̂ + z²/2n − z·sqrt(p̂(1−p̂)/n + z²/4n²)) / (1 + z²/n)`.
  Wilson is chosen over a normal approximation because small-n success rates are common in
  cold start and are badly biased by Wald intervals.
- Cost per task: mean observed cost across the eval protocol's sample (or mean per real
  feedback report), deflated against the pricing snapshot at observation time.
- **Recommendation rule:** sort models by cost ascending; find the cheapest `m*` such that
  `LB_m* ≥ minimum_success` and (if given) `cost ≤ max_cost` and `latency ≤ max_latency`.
  Using the lower bound, not the point estimate, is the honesty gate: a model whose point
  estimate is 0.92 but whose LB is 0.87 must not be recommended against a 0.90 bar.

### 4.2 Knee detection

The curve is `{(cost_m, p̂_m)}` sorted by cost. KNEE uses two complementary detectors:

- **Kneedle (Satopää et al., ICCCN 2011 — the canonical knee detector, not on arXiv):**
  normalize both axes to [0,1], then for each point compute the signed perpendicular distance
  from the point to the chord joining the endpoints of the curve; the knee candidate is the
  point of maximum distance, with the sensitivity parameter `S` (default 1.0) trading
  left/right bias on where the knee sits. KNEE runs Kneedle on (cost, success) and also on
  (cost, LB-success) so noise in small samples cannot manufacture a cliff.
- **Trade-off utility (KPITU, 2005.11600):** a model is a knee iff it has the best trade-off
  utility among its neighbors — the largest quality-loss-per-cost-unit-saved (or smallest
  quality-gain-per-cost-unit-added) locally. Used as a cross-check: if KPITU disagrees with
  Kneedle, KNEE reports lower `cliff_confidence`.

The public cliff metric (the product's "cliff"):
```
cliff = p̂_{m*} − p̂_{m_next-cheaper}     if m* is not the cheapest model
cliff = 0                               if m* IS the cheapest model
```
A cliff is **actionable** only when: (a) `LB_{m*} − UB_{m_next-cheaper} > δ_min` (the CIs do
not overlap beyond a small tolerance), and (b) `p̂_{m*} ≥ minimum_success` while
`UB_{m_next-cheaper} < minimum_success`. Otherwise the status is `insufficient_data` (CIs
overlap) or `no_cliff` (the next-cheaper model also clears the bar — recommending the cheaper
one is just correct).

### 4.3 Abstention and honesty rules

1. If no model has `n_m ≥ n_min` (default 5 evaluations) → `insufficient_data`; the response
   includes the partial curve with wide CIs and a clear "needs measurement" signal.
2. If every candidate's CI overlaps the bar → `insufficient_data` (do not pick by point
   estimate alone).
3. If the cheapest candidate clears the bar → `no_cliff`; recommendation = cheapest candidate,
   cliff = 0. This is the honest mode that makes the product trustworthy in exactly the
   regimes where routing does not pay (2608.06607).
4. `cliff_confidence ∈ {high, medium, low}` derived from CI separation; low/medium responses
   carry a machine-readable advisory that the recommendation should be spot-checked.

### 4.4 Cold start and priors

- Onboarding a new task type seeds priors from: (a) published benchmark/leaderboard
  aggregates (Artificial Analysis-class sources, ingested as data with provenance), (b)
  transfer from structurally similar task types (embedding-similarity of task descriptions),
  (c) the provider capability matrix in the Model Registry.
- Priors are explicit Bayesian priors (Beta(α₀, β₀)) whose weight decays as real
  observations accumulate; the eval scheduler spends the first budget cycles on the cheap
  models first (cheapest-first saturation) so early users get a usable `no_cliff` or
  `insufficient_data` signal cheaply.
- VP supply rule of the whole product: **a curve with no recorded protocol is not a curve.**

---

## 5. Data Model

```sql
-- Core: models and offerings (version-pinned)
CREATE TABLE providers (
    id TEXT PRIMARY KEY,            -- 'openrouter', 'dell', 'anthropic', ...
    display_name TEXT NOT NULL,
    sync_source TEXT                -- 'catalog_url' or 'manual'
);

CREATE TABLE models (
    id TEXT PRIMARY KEY,            -- 'openrouter:deepseek/deepseek-v3'
    provider_id TEXT NOT NULL REFERENCES providers(id),
    model_name TEXT NOT NULL,
    version TEXT NOT NULL,          -- pinned version/commit/date tag
    capabilities JSONB NOT NULL DEFAULT '[]',  -- tool_use, json_mode, context tokens
    status TEXT NOT NULL DEFAULT 'active',     -- active|deprecated|suspended
    UNIQUE (provider_id, model_name, version)
);

CREATE TABLE pricing_snapshots (
    id BIGSERIAL PRIMARY KEY,
    model_id TEXT NOT NULL REFERENCES models(id),
    input_per_mtok NUMERIC(12,6) NOT NULL,
    output_per_mtok NUMERIC(12,6) NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL,
    source TEXT NOT NULL            -- 'dell-catalog' | 'openrouter' | 'manual'
);

-- Task taxonomy (the unit of curves)
CREATE TABLE task_types (
    id TEXT PRIMARY KEY,            -- 'repo_bugfix'
    description TEXT NOT NULL,
    eval_suite_id TEXT NOT NULL,    -- golden suite def (in object store / suite table)
    default_min_success REAL NOT NULL DEFAULT 0.90,
    eval_sample_budget INT NOT NULL DEFAULT 100,
    freshness_ttl_hours INT NOT NULL DEFAULT 168,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE task_type_aliases (
    alias TEXT PRIMARY KEY,
    task_type_id TEXT NOT NULL REFERENCES task_types(id),
    source TEXT NOT NULL DEFAULT 'manual'   -- manual|learned|user
);

-- Observations: the fuel
CREATE TABLE observations (
    id TEXT PRIMARY KEY,            -- 'obs_9f3c' (uuid7)
    task_type_id TEXT NOT NULL REFERENCES task_types(id),
    model_id TEXT NOT NULL REFERENCES models(id),
    success BOOLEAN NOT NULL,
    cost_usd NUMERIC(12,6) NOT NULL,
    latency_ms INT,
    tokens_in INT,
    tokens_out INT,
    protocol JSONB NOT NULL,        -- temperature, max_tokens, attempts, suite, verifier
    source TEXT NOT NULL,           -- 'eval_run'|'feedback'|'seed_prior'
    batch_id TEXT,                  -- eval run id when source='eval_run'
    recommendation_id TEXT,         -- when source='feedback'
    tenant TEXT,                    -- null for eval runs; tenant id for feedback
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (source IN ('eval_run', 'feedback', 'seed_prior'))
);
CREATE INDEX idx_obs_lookup ON observations (task_type_id, model_id, observed_at DESC);
CREATE INDEX idx_obs_rec ON observations (recommendation_id) WHERE recommendation_id IS NOT NULL;

-- Eval runs (measurement plant batch metadata)
CREATE TABLE eval_runs (
    id TEXT PRIMARY KEY,
    task_type_id TEXT NOT NULL REFERENCES task_types(id),
    model_ids JSONB NOT NULL,
    protocol JSONB NOT NULL,
    budget_usd NUMERIC(12,6) NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled',   -- scheduled|running|done|failed
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ
);

-- Published curves (versioned, inspectable, licensable)
CREATE TABLE curve_snapshots (
    id TEXT PRIMARY KEY,            -- 'curve_snap_0001'
    task_type_id TEXT NOT NULL REFERENCES task_types(id),
    model_set_hash TEXT NOT NULL,   -- sha256 over sorted model ids
    params JSONB NOT NULL,          -- confidence level, n_min, S, delta_min
    snapshot JSONB NOT NULL,        -- per-model: p_hat, LB, UB, n, cost mean
    status TEXT NOT NULL DEFAULT 'current',   -- current|stale|superseded
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_curve_task ON curve_snapshots (task_type_id, computed_at DESC);

-- Recommendation audit (every public answer, input-for-output reproducible)
CREATE TABLE recommendations (
    id TEXT PRIMARY KEY,            -- 'rec_f8a1'
    task_type_id TEXT NOT NULL REFERENCES task_types(id),
    input JSONB NOT NULL,           -- exact request payload
    response JSONB NOT NULL,        -- exact response payload
    curve_snapshot_id TEXT REFERENCES curve_snapshots(id),
    model_ids JSONB NOT NULL,       -- model versions used in the decision
    status TEXT NOT NULL,           -- ok|insufficient_data|no_cliff
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Drift / staleness events
CREATE TABLE drift_events (
    id BIGSERIAL PRIMARY KEY,
    task_type_id TEXT NOT NULL,
    curve_snapshot_id TEXT,
    kind TEXT NOT NULL,             -- stale|drift|price_change|model_deprecated
    detail JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

All numbers that touch money or probability carry their provenance (`source`, `batch_id`,
`pricing_snapshots.effective_from`, `protocol`). A claim without a provenance chain is not
publishable — same discipline as the venturelab audit standard.

---

## 6. API Endpoints

| Endpoint | Method | Purpose | Input | Output |
|---|---|---|---|---|
| /knee | POST | Find knee/cliff + recommend | task, models, minimum_success, constraints | recommendation, curve, cliff, confidence, status |
| /knee/{task_type} | GET | Current curve + knee for a task type | - | curve snapshot + knee + cliff |
| /knee/compare | GET | Per-model estimates under one protocol | models, task | estimates + CIs |
| /knee/history/{task_type} | GET | Versioned snapshots / drift | since, limit | snapshot list + deltas |
| /knee/batch | POST | Multi-task planning under budget | tasks, constraints | per-task recommendations + aggregate cost |
| /knee/feedback | POST | Report real outcome (opted-in) | recommendation_id, success, cost, protocol | ack |
| /knee/webhooks | POST | Register drift/pricing-change hooks | url, events | webhook id |
| /classify | POST | Resolve task text → task_type | task_description | task_type, confidence |
| /models | GET | List registry | filter | model list |
| /models/sync | POST | Pull provider catalogs (admin) | - | sync summary |
| /internal/evals/* | POST/GET | Schedule/inspect eval runs (internal) | batch spec | run id / status |
| /healthz | GET | Liveness | - | ok |
| /metrics | GET | Prometheus scrape | - | metrics |

Per-query billing (from the report): $0.001 per `/knee` query after a free tier; batch and
compare count the same; history/feedback/webhooks free (they feed the moat).

---

## 7. Deployment

```text
MVP (weeks 1-4): single VM (2 vCPU / 4GB), Docker Compose:
  knee-api (FastAPI, uvicorn)  → Postgres 15 (or SQLite → Pg), Redis 7
  eval-worker (arq/Celery)     → provider APIs (LiteLLM gateway outbound)
  sync-worker (hourly): pricing catalog + model registry pull

Production (month 2+): Kubernetes (or Fly.io), 3-region read replicas:
  ┌─────────────────────────────────────────────┐
  │   api (HPA, 3+ pods, stateless)             │
  │   redis (cache: curve snapshots, TTL)       │
  │   postgres (primary) + replicas (curves)    │
  │   eval-workers (autoscaled queue consumers) │
  │   object store (eval suites, artifacts)     │
  │   grafana + prometheus + otel tracing       │
  └─────────────────────────────────────────────┘
```

- API layer is stateless; all decision state lives in the DB so horizontal scaling is
  trivial and recommendations are auditable.
- Eval workers are the only component that talks to external model providers; they are
  rate-limited per provider and budget-capped per (task, run) — a runaway eval batch can
  spend money, so budgets are enforced in the DB before scheduling, not after.
- Env-based secrets; no provider keys in the repo. Tenant isolation is tenant-id scoped rows
  (v1): shared curve pool for public task types, private curves for enterprise tenants.

---

## 8. Integration Points

| System | Direction | Mechanism |
|---|---|---|
| Model pricing catalogs (Dell/LLMDeals, OpenRouter) | in | hourly `models_sync`; pricing snapshots |
| LiteLLM | out | recommendation → LiteLLM route config; hook captures outcomes → `/knee/feedback` |
| OpenRouter / other gateways | out | native API call execution by consumer; SDK telemetry |
| Evaluation providers (any chat API) | out | eval-worker probe execution |
| Sibling products (EndpointTruth, AgentSLA, StackGraph, FallbackGraph) | in/out | model health (EndpointTruth), per-task success baselines (AgentSLA), task graphs (StackGraph), failover policy (FallbackGraph) — all as data, not code |
| Data licensing consumers (router vendors, MISPs) | out | `GET /knee/{task_type}` snapshots + `/knee/history` exports; contractual schema |
| Webhooks | out | drift, price-change, model-deprecation events |

---

## 9. Technology Stack

| Layer | Technology | Why |
|---|---|---|
| API | FastAPI + uvicorn | Async, typed, OpenAPI docs out of the box |
| ORM/migrations | SQLAlchemy 2 + Alembic | Version-gated schema; audit-friendly |
| Database | PostgreSQL 15 | JSONB for protocol/provenance blobs, window functions for curve math, row-level tenant scoping |
| Cache | Redis 7 | Curve snapshots + rate limiting; invalidated on pricing sync/drift |
| Queue | arq (or Celery) | Eval + sync workers; budget-capped tasks |
| Metrics/observability | Prometheus + Grafana + OpenTelemetry | Cost accounting, estimate calibration, drift alerting |
| Model execution | LiteLLM SDK (or direct per-provider SDKs) | Single outbound gateway for eval workers |
| Embeddings | small open embedding model (e.g. sentence-transformers) | Task classification + transfer-prior similarity |
| Container | Docker + docker-compose → Helm/K8s | Standard path; cheap MVP, scalable prod |
| Secret management | env + cloud secret store | Keys never in repo |

---

## 10. Cost Estimates

MVP monthly infra (at 2026-08 pricing):

| Component | Monthly Cost | Notes |
|---|---|---|
| Compute (1 VM, 2 vCPU/4GB) | $20 | API + workers on one box |
| Database (managed Postgres) | $25 | Small, with backups; SQLite free in dev |
| Cache (managed Redis) | $15 | Curve snapshot TTL cache |
| Object storage | $5 | Eval suites + artifacts |
| Observability (hosted Grafana/Prom) | $10 | Free tier possible early |
| **Infra subtotal** | **$75** | |
| **Eval token spend (the real cost center)** | **$100–400** | 20 task types × ~10 models × 15 samples × avg $0.05/call ≈ $150/mo at 2026 blend; scales with tenure — must be capped by the budget controller |
| **Total first-month run rate** | **~$175–475** | vs report's $95 estimate, which omitted eval token spend — flagged, not fudged |

Revenue at 10k paid queries/day × $0.001 = $10/day ≈ $300/mo gross (billing tier must clear
the eval cost center before it is profitable; enterprise pricing at $99/mo/unlimited is the
actual margin engine).

---

## 11. Risk Analysis

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Sparse observations → wrong cliffs (cold start) | High | High | Bayesian priors, transfer across similar task types, cheapest-first sampling, `insufficient_data` abstention honestly surfaced |
| Noisy estimates from small n manufacture fake cliffs | Medium | High | Wilson CIs, δ_min separation gate, Kneedle on LB curve, `cliff_confidence` field |
| Model behavior drifts after deployment (estimates rot) | High | Medium | Freshness TTL, continuous re-eval, drift detection with webhooks, snapshot versioning |
| Provider pricing changes shift cliffs silently | High | Medium | Hourly pricing sync, read-time cost join, cache invalidation on any touched model |
| Eval budget overrun (measurement spends more than it earns) | High | Medium | DB-enforced budget caps per (task, batch), cheapest-first saturation, auto-pause when ROI test fails |
| Gaming: consumers report only failures (feedback bias) | Medium | High | Contractual telemetry schema, sampled independent verification, per-tenant dual reporting (eval vs feedback) reconciliation |
| Task taxonomy mismatch (user's mental categories ≠ our task types) | Medium | Medium | Alias learning, embedding classifier, custom tenant task types, 422-with-candidates instead of guessing |
| Protocol mixing contaminates curves | Medium | High | Protocol recorded per observation; comparisons only within protocol cohorts (2606.17930 discipline) |
| Big incumbent adds the feature (OpenRouter/AA) | Low-Medium | High | Speed + the feedback flywheel + honest abstention reputation; data licensing contracts lock in router vendors |
| Routing simply does not pay for certain task types (no cliff) | Certain (for some tasks) | Low | It is a designed outcome: `no_cliff` + cheapest recommendation is correct behavior, and it is marketed as such |

---

## 12. Success Metrics

| Metric | Target | How to Measure |
|---|---|---|
| API latency (p95) | < 100 ms (cached curve path) | Prometheus + traces |
| Recommendation hit rate | > 90% (observed success ≥ bar after rec executed) | via feedback ingest on opted-in traffic |
| Cost savings vs naive (always-frontier) | > 40% on routed traffic | customer-side A/B + KNEE-side projection from curve |
| Estimate calibration (ECE on success vs LB) | < 0.05 | quarterly audit over recommendations with outcomes |
| Abstention honesty | ≤ 20% of queries return insufficient_data at steady state; 100% of those are correct (never "ok" when data is thin) | audit sample |
| Curve freshness | median snapshot age < TTL/2 | drift/staleness events |
| Eval cost per task type | < 4× the revenue it generates in the first 3 months | cost accounting per task type |
| Data flywheel growth | monthly feedback observations > 3× eval observations by month 3 | DB counts |

---

## 13. Implementation Phases

### Phase 1 — MVP (Weeks 1-2)
- FastAPI skeleton with `/knee` (POST), `/knee/{task_type}` (GET), `/classify` (alias map +
  embedding), `/models` (manual seed registry).
- SQLite schema (models, task_types, observations, recommendations) → JSON observation
  ingest from a hand-run eval loop.
- Knee Engine v0: Wilson intervals + constrained argmin + Kneedle (S=1.0) + cliff metric +
  `insufficient_data` / `no_cliff` abstention. No feedback loop yet.
- 5 task types × 10 models seeded via 100-sample eval runs; manual pricing table.

### Phase 2 — Core (Weeks 3-4)
- PostgreSQL + Alembic; `/knee/batch`; `/knee/compare`; `/knee/history`.
- Evaluation Engine: worker pool, budget controller, protocol recording, cheapest-first
  sampling, uncertainty-directed next-sample selection.
- LiteLLM integration: outbound execution hook + `/knee/feedback` ingest; recommendation
  audit log complete.
- Model registry auto-sync (Dell/LLMDeals + OpenRouter); pricing snapshots + cache
  invalidation; Redis cache.

### Phase 3 — Public API (Month 2)
- Auth (API keys), rate limits, billing ($0.001/query), dashboard.
- Drift/staleness sweeper + webhooks; KPITU cross-check; `cliff_confidence` finalization.
- Drift alerting + Grafana dashboards; cost accounting per task type.

### Phase 4 — Data product & enterprise (Months 3-6)
- Enterprise tenants (private task types, custom eval suites, private curves).
- Anonymous aggregate curve exports + data licensing contracts with router vendors.
- SDKs (Python, TS), OpenRouter/LiteLLM one-click integration, partner onboarding.
- Regression probes: quarterly re-baseline of every task type against fresh gold to catch
  silent benchmark rot.

---

## 14. Research Appendix — verified references

Verified via arXiv API / Semantic Scholar on 2026-08-17. URLs are the abstract pages.

| ID | Paper | Relevance to KNEE |
|---|---|---|
| 2603.04445 | Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey | The report's headline survey; taxonomy of routing paradigms + "when/what/how" framework; validates the space |
| 2606.26836 | The Capability Frontier: Benchmarks Miss 82% of Model Performance | The product's mathematical ancestor: a Pareto frontier over models at each cost level; SOTA matched at 85% cost reduction |
| 2606.17930 | How Inference Compute Shapes Frontier LLM Evaluation | Evaluation is protocol-dependent — KNEE's per-observation protocol recording is mandatory, not optional |
| 2502.00409 | Doing More with Less: A Survey on Routing Strategies for Resource Optimisation in LLM-Based Systems | Formalizes routing as a performance-cost optimization problem; budget/global-optimization framing of /knee/batch |
| 2506.06579 | Towards Efficient Multi-LLM Inference: Routing and Hierarchical Techniques | Routing vs cascading comparison; supports both surface modes and argues for per-query difficulty signal |
| 2602.09902 | Routing, Cascades, and User Choice for LLMs | Game-theoretic: static routing often optimal; provider/user misalignment → KNEE must optimize for the *user's* bar, not provider margin |
| 2305.05176 | FrugalGPT: How to Use Large Language Models While Reducing Cost | Cascade learning; 98% cost reduction at matched performance — the economic ceiling of the category |
| 2406.18665 | RouteLLM: Learning to Route LLMs with Preference Data | Router that consumes cost-quality signal; >2x cost reduction — a downstream customer and a benchmark of the idea |
| 2404.14618 | Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing | Quality-bar-driven routing (40% fewer large calls); the "minimum_success" concept |
| 2502.17282 | Capability Instruction Tuning: A New Paradigm for Dynamic LLM Routing | Routing without per-query candidate inference; shows routing intelligence can be cheap — supports the margin model |
| 2604.07494 | Triage: Routing Software Engineering Tasks via Code Quality Signals | Falsifiable condition: cheaper-tier pass rate must exceed inter-tier cost ratio; KNEE's cliff actionability rules echo this |
| 2608.06607 | Pre-Inference Routing for Cost-Efficient Document Field Extraction | Routing pays only if cheaper model fails often enough AND failure predictable — the honest `no_cliff` design principle |
| 2602.06370 | Cost-Aware Model Selection for Text Classification | Pareto-frontier projections + utility functions; fine-tuned encoders 1-2 orders cheaper — evidence that flat (no-cliff) regions are common |
| 2606.02245 | When Knowledge Is Not Free: Cost-Aware Evidence Selection in RAG | Cost-tiered selection under budget; static selectors brittle → KNEE's active, compounding measurement philosophy |
| 2603.21389 | Task-Specific Efficiency Analysis: When Small LMs Outperform Large LMs | Performance-Efficiency Ratio; task-specific efficiency — empirical basis for per-task curves |
| 2409.15608 | Deep Learning Approach for Knee Point Detection on Noisy Data | Knee-point detection on noisy curves; motivates the CI-based (not point-based) knee logic |
| 2005.11600 | Knee Point Identification Based on Trade-Off Utility (KPITU) | Formal knee definition via trade-off utility; used as KNEE's cross-check detector |
| 2206.07682 | Emergent Abilities of Large Language Models (Wei et al.) | Counterpoint warning: capability cliffs are not always monotone or predictable — KNEE's estimates must carry uncertainty, and its abstention rule exists

Non-arXiv canonical reference (not located on arXiv; conference publication):

- Satopää, V.A., Albrecht, J., Irwin, D., Raghavan, B. — "Finding a 'Kneedle' in a Haystack:
  Detecting Knee Points in System Behavior", Proc. 20th Int'l Conf. on Computer Communications
  and Networks (ICCCN), 2011 — the standard curve-knee detection algorithm (normalized curve +
  maximum-distance-from-chord + sensitivity parameter S); basis of §4.2.

Unverified source-report citations (flagged, not repeated as fact):

- "Towards Cost-effective LLMs Routing with Batch Prompting" (SeqRoute) — **NOT VERIFIED** on
  arXiv or Semantic Scholar (2026-08-17). Budget-aware routing concept is covered instead by
  2502.00409 / 2305.05176.
- "The Capability Frontier: Benchmarks Miss 82% of Model" — **VERIFIED as 2606.26836** (title
  was truncated in the report; the 82% figure refers to error-rate reduction under oracle
  selection, not benchmark miss rate).

---

*Architecture spec generated by VentureLab · arXiv-verified 2026-08-17 · machine-proposed, not
human-adjudicated.*