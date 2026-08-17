# AGENTPACKS — Technical Architecture

*Generated: 2026-08-17T20:21Z · Machine-proposed spec from `reports/agentpacks/report.md` + verified arXiv research (see Annex A) · origin=machine · not yet human-reviewed*

*Supersedes the template stub previously committed at this path (2026-08-18T04:30Z).*

---

## 0. Product Definition (from the report + idea docs)

- **Thesis:** Cloneable agent architectures with measured cost/quality. *Docker Hub for agent systems.*
- **Key insight:** NOT another awesome-agent-frameworks list. Complete, benchmarked, cloneable architectures.
- **The unit is not a prompt — it is a reproducible agent system**: a directory with `manifest.yaml`, `AGENTS.md`, `agents/`, `skills/`, `mcps/`, `tools/`, `workflows/`, `evals/`, `env.example`, `docker-compose.yml`, `benchmarks.json`, `costs.json`, `README.agent.md`.
- **Position in the venture stack:** COMPOSE node of the progression `MEASURE → EndpointTruth, OPTIMIZE → Knee, SELECT → Toolloader, COMPOSE → Agentpacks`. Tier-S product #3 (final-shortlist.md).
- **Differentiator:** every published architecture carries a *continuously measured* cost/quality record, not stars.

---

## System Overview

```text
                          ┌──────────────────────────────────────────────┐
                          │               AGENTPACKS                      │
                          │                                              │
  PUBLISHERS ───────────► │  ┌──────────┐   ┌─────────────┐              │
  (humans, repos,         │  │ REGISTRY │   │ BENCHMARK   │  ┌────────┐  │
   paper-reported         │  │ service  │◄──┤ orchestrator│─►│ LEDGER │  │
   architectures)         │  └────┬─────┘   │ (ArchBench) │  └───┬────┘  │
                          │       │         └──────┬──────┘      │       │
  (content-addressed      │       │  version DAG   │ results     ▼       │
   pack blobs)            │       ▼                │         ┌─────────┐ │
  ┌──────────────┐        │  ┌─────────────┐       │         │ COST/   │ │
  │ OBJECT STORE │◄───────┤  │ EVOLUTION   │◄──────┘         │ QUALITY │ │
  │ S3/R2 (sha256)│       │  │ GRAPH svc   │              ┌──┤ RANKER  │ │
  └──────────────┘        │  └─────────────┘              │  └────┬────┘ │
                          │       ▲                       │       │      │
                          │       │ arXiv links,          │       ▼      │
                          │       │ changelogs, bench delta│  ┌────────┐ │
                          │       │                       │  │  MCP   │ │
  AGENTS ─────────────────┼───────┼───────────────────────┼─►│ /rec-  │ │
  (claude, codex, ...)    │  agentpack CLI ◄──────────────┘  │ ommend │ │
                          │  install compile bench          └────────┘ │
                          └──────────────────────────────────────────────┘
                                     │
               ┌─────────────────────┼──────────────────────┐
               ▼                     ▼                      ▼
       KNEE (model cliff)    TOOLLOADER (tool fit)   ENDPOINTTRUTH (live endpoint truth)
       AGENTSLA (cost/success) FALLBACKGRAPH (equiv)  STACKGRAPH (co-occurrence prior)
```

Data flow summary:
1. A publisher uploads a pack; the registry **content-addresses** it (immutable `sha256` blob + version DAG).
2. The benchmark orchestrator runs the pack against the fixed **task taxonomy** on ephemeral runners, following a fixed measurement protocol, and writes results to the ledger.
3. The cost/quality ranker consumes ledger rows + KNEE/ENDPOINTTRUTH signals and serves `MCP /recommend`.
4. A consumer's agent calls `/recommend` (or `agentpack install <pack>`), the compiler materializes a runnable scaffold, telemetry flows back from cloned runs.
5. Every measurement is timestamped, provenance-linked to the pack version + model config it was taken under (`measured_at`, `model_config`, `provider_snapshot`).

---

## Core Components

### 1. Registry Service
- **Purpose:** Store, version, and serve agentpack metadata + blobs; the catalog is the product surface.
- **Interface:**
  - `GET /architectures?task_type=&q=&limit=` — catalog browse/search
  - `POST /architectures` — publish a pack (multipart: tarball + manifest)
  - `GET /architectures/{slug}` — pack detail incl. current benchmark summary
  - `GET /architectures/{slug}/versions` — version list (semver pointers → immutable content ids)
- **Input/Output JSON (manifest normalization):**
  ```json
  {
    "slug": "deep-research-v3",
    "task": "deep_research",
    "architecture": "planner -> parallel researchers -> synthesizer -> verifier",
    "models": ["replaceable"],
    "required_mcps": ["browser", "github"],
    "min_context": 64000,
    "license": "MIT",
    "estimated_cost": 0.42,
    "median_runtime": 310,
    "benchmark_score": 0.87,
    "clone": "git+https://git.agentpacks.dev/packs/deep-research-v3",
    "agent_install": "agentpack install deep-research-v3"
  }
  ```
- **Implementation details:**
  - Pack tarball → `sha256` → immutable object in blob store; `pack_versions.sha256` is the content address (Pāṭala-style provenance: every measurement references the exact bytes it was taken against).
  - Manifest is parsed strictly (JSON Schema v1); unknown fields fail publish, not warn.
  - Publishing requires: valid manifest, `benchmarks.json` present, license file, `env.example` (no secrets — secret attrs are rejected by schema).
  - Signed uploads (Sigstore cosign) for verified-publisher tier; community tier unsigned but gated by benchmark pass.

### 2. Benchmark Orchestrator (ArchBench engine)
- **Purpose:** Produce the *measured* cost/quality record that differentiates the product. One architecture → one bench result per (task_type, suite, model_config).
- **Interface:**
  - `POST /benchmarks` `{"pack_version_id": "...", "suite": "standard", "model_config": "knee-default"}`
  - `GET /benchmarks/{id}` — status/progress/results
  - `GET /benchmarks?pack={slug}` — historical bench rows
- **Input/Output JSON (result row):**
  ```json
  {
    "bench_id": "b_9f2c",
    "pack_version_id": "pv_…sha256…",
    "task_type": "deep_research",
    "suite": "standard-v1",
    "trials": 40,
    "success_rate": 0.92,
    "cost_usd_mean": 0.38,
    "median_runtime_s": 305,
    "tokens_in_mean": 81200,
    "tokens_out_mean": 9400,
    "model_config": {"provider": "openrouter", "model": "replaceable-default"},
    "provider_snapshot": {"endpointtruth_rev": "et_2026-08-17T20:00Z"},
    "measured_at": "2026-08-17T20:21Z",
    "benchmark_protocol_rev": "bp-1.0"
  }
  ```
- **Implementation details:**
  - Fixed measurement protocol (`benchmark_protocol_rev`): N trials, fixed temperature, fixed harness version, no interactive human correction, per-task type instance set from the shared task taxonomy (same instances the sibling Knee product uses — one corpus, many products).
  - Runners are ephemeral Docker/K8s Jobs with per-run cost cap (LLM tokens are metered through the LiteLLM gateway so cost is *billed cost*, not estimated).
  - Hidden/reserved eval instances (30% of suite) not shipped in the pack's own `evals/` to reduce benchmark gaming; disclosed in the protocol.
  - Results are append-only; a re-bench supersedes, never mutates, the previous row.

### 3. Cost/Quality Ledger + Ranker
- **Purpose:** Turn bench rows + clone telemetry into the recommendation surface.
- **Interface (internal, consumed by 5 and by sibling products):**
  - `POST /runs` — clones report telemetry: `{pack_version_id, task_type, success, cost_usd, runtime_s, model, provider}`
  - `GET /ledger/{slug}/summary` — aggregate cost/quality summary
- **Implementation details:**
  - Ledger merges two sources: (a) controlled bench rows (high trust), (b) community clone telemetry (lower trust, weighted, only used when agreeing with bench within tolerance).
  - The ranker marginalizes over model_config: for recommendation, models are treated as *replaceable slots* — cost/quality surface is computed for the default config and, when KNEE data is available, re-projected onto the requested budget.
  - **Abstention policy:** if fewer than `MIN_RUNS` (default 25) successful bench trials or telemetry is stale (`> 30 days` with no model-config match), the ranker returns `NO_RECOMMENDATION` with the nearest evidence distance instead of a forced pick — an honest "insufficient data" is a valid answer (mirrors the lab doctrine: abstain rather than invent).

### 4. Recommendation Service (MCP surface)
- **Purpose:** The agent-facing entry point: "what complete architecture should I clone for X?"
- **Interface (MCP-idiomatic + REST):**
  - `POST /recommend` (REST) / `mcp.recommend` (MCP tool):
    ```json
    {
      "task": "analyze customer feedback",
      "data_note": "10k reviews",
      "budget_usd": 5.00,
      "quality_min": 0.85,
      "model_slots": ["replaceable"],
      "required_mcps": ["browser"]
    }
    ```
    ```json
    {
      "recommended": {"slug": "sentiment-analyzer-v3", "version": "v3.1.0",
                      "estimated_cost": 2.14, "success_rate": 0.92,
                      "clone": "agentpack install sentiment-analyzer-v3",
                      "reason": "best measured cost/quality for customer_feedback; 847 runs on record"},
      "alternatives": [{"slug": "...", "score": 0.91, "cost_usd": 3.1}],
      "evidence": {"bench_rows": 847, "stale": false, "abstained": false}
    }
    ```
- **Implementation details:**
  - Candidate filter: task_type similarity (embedding over task taxonomy via pgvector) ∩ required_mcps ∩ min_context ≤ available.
  - Ranking: Pareto front over (cost_usd, success_rate); Knee integration picks the elbow model-cliff-constrained variant when the caller gives a budget; otherwise default config ranking.
  - Output carries an evidence block so callers can judge trust (no bare "trust us").
  - Rate limits + request logging: every recommendation is an audit row (request hash → chosen → used-or-not telemetry).

### 5. Compiler / Installer (`agentpack` CLI + server-side scaffold service)
- **Purpose:** True "clone" — one command from registry to runnable system.
- **Interface:**
  - `agentpack install <slug>[@version]` — client-side: fetches immutable blob, materializes tree, renders `env.example` → `.env` (interactive secret prompt, never stored server-side), validates Docker compose, prints "ready" + first-run smoke test.
  - `POST /install` — server-side bundle: `tar.gz` of the compiled tree (for CI/CD pipelines / non-interactive consumers).
  - `agentpack bench <slug>` — local clone re-runs the pack's own `evals/` against the fixed protocol and uploads a telemetry row.
- **Implementation details:**
  - Compile = template render only; the served artifact is the content-addressed tree + env scaffold. No server-side codegen that could diverge from the blob.
  - Dependency resolution: `required_mcps` / `required_tools` checked against the Toolloader catalog; missing dependencies fail install with the compatible alternative list (FallbackGraph-sourced).
  - Installation is immutable: the CLI records the installed `sha256` locally so `agentpack update` is a diff, not a reinstall.

### 6. Evolution Graph Service
- **Purpose:** The graph-based evolution research layer: which patterns changed, why, with what measured delta, linked to arXiv evidence.
- **Interface:**
  - `GET /architectures/{slug}/graph` — version DAG
  - `POST /architectures/{slug}/versions/{version}/note` — publisher changelog (requires pack publisher key)
- **Implementation details:**
  - Edges carry `reason` (e.g. "added verification pass"), optional `arxiv_ids` (verified format `arXiv:2407.01489`), and `bench_delta` (success_rate Δ, cost Δ vs parent, computed from ledger at publish time).
  - Immutable: a version once published cannot be edited; corrections are new versions (or deprecations). This keeps the delta math honest.

---

## Data Model

```sql
-- Registry
CREATE TABLE agentpacks (
  id            BIGSERIAL PRIMARY KEY,
  slug          TEXT UNIQUE NOT NULL,          -- deep-research-v3
  name          TEXT NOT NULL,
  description   TEXT,
  task_type     TEXT NOT NULL REFERENCES task_taxonomy(code),
  architecture_pattern TEXT NOT NULL,          -- planner_executor | reflexion | tos_scout ...
  min_context   INT,
  license       TEXT,
  publisher_id  BIGINT REFERENCES publishers(id),
  tier          TEXT NOT NULL DEFAULT 'community',   -- verified | community | deprecated
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE pack_versions (
  id              BIGSERIAL PRIMARY KEY,
  pack_id         BIGINT NOT NULL REFERENCES agentpacks(id),
  version         TEXT NOT NULL,               -- semver pointer
  sha256          TEXT NOT NULL UNIQUE,        -- content address of blob
  manifest_json   JSONB NOT NULL,              -- normalized manifest (costs/benchmark booleans)
  parent_version_id BIGINT REFERENCES pack_versions(id),  -- evolution DAG
  status          TEXT NOT NULL DEFAULT 'active', -- active | deprecated | withdrawn
  published_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON pack_versions (pack_id, version);
CREATE INDEX ON pack_versions (sha256);

CREATE TABLE pack_files (
  id            BIGSERIAL PRIMARY KEY,
  version_id    BIGINT NOT NULL REFERENCES pack_versions(id),
  path          TEXT NOT NULL,
  content_hash  TEXT NOT NULL,
  size_bytes    BIGINT NOT NULL,
  UNIQUE (version_id, path)
);

-- Benchmark ledger (append-only)
CREATE TABLE benchmarks (
  id          BIGSERIAL PRIMARY KEY,
  pack_version_id BIGINT NOT NULL REFERENCES pack_versions(id),
  task_type   TEXT NOT NULL,
  suite       TEXT NOT NULL,                   -- standard-v1 | hidden-v1
  protocol_rev TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'queued',  -- queued | running | done | failed
  queued_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  started_at  TIMESTAMPTZ,
  finished_at TIMESTAMPTZ
);

CREATE TABLE benchmark_results (
  id              BIGSERIAL PRIMARY KEY,
  benchmark_id    BIGINT NOT NULL REFERENCES benchmarks(id),
  trials          INT NOT NULL,
  success_rate    NUMERIC(6,4) NOT NULL,
  cost_usd_mean   NUMERIC(10,4) NOT NULL,
  median_runtime_s NUMERIC(10,1),
  tokens_in_mean  BIGINT,
  tokens_out_mean BIGINT,
  model_config    JSONB NOT NULL,              -- {provider, model, params}
  provider_snapshot TEXT,                      -- endpointtruth revision id
  measured_at     TIMESTAMPTZ NOT NULL
);

-- Telemetry from clones (lower trust)
CREATE TABLE runs_telemetry (
  id            BIGSERIAL PRIMARY KEY,
  pack_version_id BIGINT NOT NULL REFERENCES pack_versions(id),
  clone_id      TEXT,                          -- anonymous install id
  task_type     TEXT NOT NULL,
  success       BOOLEAN NOT NULL,
  cost_usd      NUMERIC(10,4),
  runtime_s     NUMERIC(10,1),
  model         TEXT,
  provider      TEXT,
  recorded_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Recommendations (audit trail)
CREATE TABLE recommendations (
  id            BIGSERIAL PRIMARY KEY,
  request_hash  TEXT NOT NULL,                 -- sha256(task, budget, quality_min, mcps, ctx)
  tasked        TEXT NOT NULL,
  budget_usd    NUMERIC(10,4),
  quality_min   NUMERIC(6,4),
  chosen_pack_version_id BIGINT REFERENCES pack_versions(id),
  alternatives  JSONB,                         -- top-K with scores
  evidenced     JSONB,                         -- bench_rows, stale, abstained
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON recommendations (request_hash, created_at);

-- Shared taxonomy (sibling products use the same codes)
CREATE TABLE task_taxonomy (
  code        TEXT PRIMARY KEY,                -- deep_research | repo_bugfix | ...
  description TEXT,
  embedding   VECTOR(768),                     -- pgvector, for fuzzy task match
  parent_code TEXT REFERENCES task_taxonomy(code)
);
```

Migration policy: additive migrations only in MVP; the ledger tables are append-only by contract (no UPDATE/DELETE grants to app role except status transitions).

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/architectures` | GET | Browse/search catalog (`task_type`, `q`, `limit`, `sort=cost\|quality\|recent`) |
| `/architectures` | POST | Publish pack (multipart tarball + manifest) |
| `/architectures/{slug}` | GET | Pack detail + current bench summary |
| `/architectures/{slug}/versions` | GET | Version list (semver → sha256) |
| `/architectures/{slug}/graph` | GET | Evolution DAG with bench deltas + arXiv links |
| `/architectures/{slug}/versions/{v}` | GET | Version detail + benchmark rows |
| `/architectures/{slug}/versions/{v}/note` | POST | Publisher changelog/deprecation (keyed) |
| `/recommend` | POST | Architecture recommendation (REST) |
| `/mcp/recommend` | POST | MCP tool surface (`tools/recommend`) |
| `/mcp/install` | POST | MCP tool surface (`tools/install` → returns `agentpack install …`) |
| `/benchmarks` | POST | Queue a bench run |
| `/benchmarks/{id}` | GET | Bench status/results |
| `/benchmarks?pack={slug}` | GET | Bench history |
| `/runs` | POST | Clone telemetry ingest |
| `/ledger/{slug}/summary` | GET | Aggregate cost/quality summary |
| `/install` | POST | Server-side compiled bundle (tar.gz) |
| `/health` | GET | Liveness + ledger freshness |

Authn/policy: publish + bench + note = publisher key scoped to pack slug; recommend/runs = rate-limited API key; health = open. Signing: verified-tier publishes require cosign signature over the blob sha256.

---

## Deployment

```text
                    ┌──────────────── Edge / customers ─────────────────┐
                    │  agents (claude/codex/…)  ⇄  MCP gateway        │
                    │  developers  ⇄  agentpack CLI / web UI          │
                    └───────────────────────┬──────────────────────────┘
                                            │ HTTPS
                    ┌───────────────────────▼──────────────────────────┐
                    │        Kubernetes cluster (k3s MVP → EKS/GKE)    │
                    │  ┌────────────┐ ┌────────────┐ ┌──────────────┐  │
                    │  │ registry-api│ │ recommend- │ │ evolution-   │  │
                    │  │  (FastAPI)  │ │  api       │ │  api         │  │
                    │  └─────┬──────┘ └─────┬──────┘ └──────┬───────┘  │
                    │        │  ┌──────────▼───────┐         │         │
                    │        ├─►│ bench workers    │         │         │
                    │        │  │ (K8s Jobs,       │         │         │
                    │        │  │ Docker-in-Docker)│         │         │
                    │        │  └──────────┬───────┘         │         │
                    │        │             ▼                 ▼         │
                    │  ┌─────▼─────┐ ┌──────────┐ ┌────────────────┐  │
                    │  │ PostgreSQL│ │  Redis   │ │ Object storage │  │
                    │  │ +pgvector │ │ queues/  │ │ S3/R2, sha256  │  │
                    │  └───────────┘ │ cache    │ │ content-addr.  │  │
                    │                └──────────┘ └────────────────┘  │
                    └──────────────────────────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │ Model gateway (LiteLLM)      │──► OpenRouter / providers
                    │ metering = billed cost       │──► ENDPOINTTRUTH snapshots
                    └──────────────────────────────┘
```

- Bench workers run on spot/cheap instances; the queue is Redis-backed with per-run cost caps and global daily bench budget (cost runaway is the #1 infra risk — see Risks).
- Blob store: S3-compatible (R2) with versioning; blobs immutable so CDN caching is safe.
- Multi-region: read replicas of Postgres for catalog reads; ledger writes single-region (consistency > latency).
- Observability: OpenTelemetry traces on every recommend + bench; ledger freshness heartbeat.

---

## Integration Points

| System | How |
|--------|-----|
| **Knee** | Recommendation ranker calls Knee at request time to re-project the pack cost/quality surface onto the caller's budget; Knee's model-cliff data picks the cheapest config that still clears `quality_min`. (Knee = OPTIMIZE, Agentpacks = COMPOSE; the request-time call, not batch, keeps both fresh.) |
| **Toolloader** | Pack `required_mcps`/`required_tools` checked against Toolloader's catalog during install; recommended tool set per task_type becomes a pack attribute (`tools/` dir). |
| **EndpointTruth** | Every bench row pins a `provider_snapshot` (endpointtruth revision) so cost/latency measurements are interpretable when endpoints drift; stale-vs-snapshot flagged in ledger summaries. |
| **FallbackGraph** | Install-time dependency resolution surfaces equivalent MCP/model/provider alternatives when a required resource is unavailable. |
| **AgentSLA** | Clone telemetry (`/runs`) feeds the cost-per-success profiler; AgentSLA's per-task cost-per-success numbers validate/override pack `estimated_cost` in the ledger summary. |
| **StackGraph** | Co-occurrence data (which frameworks/models/tools ship together) supplies the Bayesian prior for ranking packs with thin bench data; trending combos get a discovery boost on the catalog home. |
| **ArchBench** | This spec's Benchmark Orchestrator IS the ArchBench substrate; ArchBench productizes the bench result surface (frontier curves) over the same ledger. |
| **MCP registry pulse** | Crawler watches MCP servers referenced by packs for health/compat flags; broken required-MCP packs get deprioritized in recommend. |
| **Marketplace billing** | Stripe for pro/enterprise; revenue share on paid packs is a ledger line item, not a separate system (pack `price` field in manifest; share computed on usage-attributed installs). |

---

## Tech Stack

| Layer | Tech | Why |
|-------|------|-----|
| API | FastAPI (Python 3.12) | Async, typed, FastAPI is the project's existing convention; Pydantic models double as manifest schema |
| Catalog DB | PostgreSQL 16 + pgvector | Relational ledger integrity + task-embedding similarity in one engine |
| Queue/cache | Redis 7 | Bench job queue, rate limits, recommendation cache (5 min TTL) |
| Blob store | S3-compatible (R2) | Content-addressed immutable pack blobs; cheap egress |
| Bench runner | K8s Jobs + Docker-in-Docker | Isolated, reproducible, capped execution per bench |
| Model gateway | LiteLLM | Uniform provider access + billing metering (actual cost, not estimate) |
| CLI | Go (single binary) `agentpack` | Fast install, zero-runtime-deps distribution, easy `brew`/`npm` shims |
| Signing | Sigstore cosign | Verified-publisher attestation over blob sha256 |
| Search | pgvector + Postgres FTS | Task-type fuzzy match + tag browse; no separate search cluster in MVP |
| Observability | OpenTelemetry + Prometheus/Grafana | Trace every recommend; alert on ledger freshness |

---

## Costs

| Component | Monthly (MVP→Core) | Notes |
|-----------|-------------------|-------|
| Compute (EKS/GKE spot workers) | $150–$400 | Bench runners dominate; capped by daily bench budget |
| Inference (LLM metering via LiteLLM) | $400–$1,500 | Proportional to bench volume + telemetry trials; per-bench cost caps |
| PostgreSQL (managed, 2×4GB) | $120–$250 | Read replica in second region |
| Redis (managed) | $30–$60 | |
| Object storage (R2) | $10–$50 | Blobs are small; egress grows with installs |
| Observability + logging | $50–$150 | |
| Domains/CDN/basic | $20–$50 | |
| **Total** | **~$800 – $2,500** | Optimistic floor: MVP on a single k3s box + SQLite = well under $300 |

Monetization offsets (targets, not commitments): free tier (browse/install, attribution), Pro $19/mo (bench API + MCP + private packs), Enterprise $500–2k/mo (private registry, SSO, signed packs), marketplace revenue share (bench-gated paid packs).

---

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|-----------|
| Benchmark gaming (packs overfit to public suite) | Med | High | 30% hidden/reserved instances; protocol revisioning; ad-hoc task sampling for verified tier |
| Endpoint/model drift invalidates measurements | High | Med | Every row pinned to provider_snapshot; staleness flags; re-bench triggers on drift detected via EndpointTruth |
| Cost runaway on bench workers | Med | High | Per-run cost cap, daily bench budget, spot-only workers, queue rate limiting |
| Community pack quality variance | High | Med | Benchmark-gated publishing (must pass suite to be listed), verified-publisher tier, deprecation flow |
| Low clone telemetry (privacy concerns) | Med | Med | Opt-in telemetry, anonymous clone_id, aggregate-only ledger, bench data carries the product by itself |
| MCP/tool ecosystem churn breaks installs | High | Med | Install-time dependency check via Toolloader + FallbackGraph alternatives; broken-pack auto-deprecation |
| "Another framework directory" drift (losing the benchmark differentiator) | Med | High | Ledger data is the product; catalog UI defaults to quality/measured sorting, never stars |
| Marketplace abuse (paid packs mislabeled) | Low | Med | Signed publishes, benchmark gate before `paid` status, human review of paid listings |

---

## Metrics

| Metric | Target | Measure |
|--------|--------|---------|
| Catalog size (active packs) | 50 by end of Phase 3 | `COUNT(*) FROM agentpacks WHERE tier <> 'deprecated'` |
| Bench coverage | ≥ 80% of active packs have ≤ 30-day-old bench row | Ledger freshness query |
| Category coverage | ≥ 40 task types covered | taxonomy coverage |
| Recommend hit-rate (accepted→installed) | ≥ 25% | recommendations → install events (request_hash join) |
| Install success (first-run smoke pass) | ≥ 90% | CLI-uploaded smoke result |
| Measured-vs-estimated cost | |Δ| ≤ 20% across catalog | ledger summary vs manifest |
| MCP adoption | ≥ 1k /recommend calls/mo by end of Phase 3 | recommendations table |
| Bench turnaround | p95 ≤ 24 h from publish to first bench row | benchmarks timestamps |
| Abstention honesty | abstain rate 5–20% (not 0, not 50) | recommendations where abstained=true |
| Ledger freshness heartbeat | 100% of days green | OTel heartbeat |

---

## Implementation Phases

### Phase 1: MVP (Week 1–2)
- Pack format v1 + strict manifest schema; `POST /architectures` publish; content-addressed blob store (R2); SQLite-first registry.
- `agentpack install` CLI (Go): fetch blob → materialize tree → env scaffold → docker compose validate → smoke test.
- 10 seed packs (deep-research-v3, coding-factory, github-maintainer, customer-support, paper-reviewer, dataset-curator, security-auditor, translation-factory, browser-research-swarm, cheap-coding-agent) manually benchmarked on **3** task types with the fixed protocol v1.
- Rule-based `/recommend` (hard filters + static rank by measured score).
- Deliverable: `agentpack install deep-research-v3` works end-to-end; catalog lists 10 packs with honest measured rows.

### Phase 2: Core (Week 3–4)
- Postgres + pgvector; task taxonomy table shared with Knee/Toolloader.
- Benchmark orchestrator: Redis queue, K8s Job workers, per-run cost caps, hidden instances, append-only ledger.
- Cost/quality ranker with abstention policy; Knee + EndpointTruth integration at request time.
- Evolution graph v1: version DAG, changelog notes, arXiv-link fields, bench delta on publish.
- MCP surface (`mcp.recommend`, `mcp.install`); audit row per recommendation.
- `agentpack bench <slug>` telemetry upload; AgentSLA feed.
- Deliverable: automatic re-bench on publish; MCP-driven recommendation with evidence block.

### Phase 3: Production (Month 2)
- Marketplace: paid packs, revenue share, Stripe; verified-publisher tier with Sigstore signing.
- Enterprise: private registries, SSO, signed internal packs, on-prem compiler.
- Scale: multi-region read replicas, CDN-backed blob delivery, bench worker autoscaling with daily budget governor.
- StackGraph prior + MCP registry pulse crawl in ranking.
- Publish ArchBench (the frontier-curve product) over the same ledger.
- Deliverable: public API, catalog of 50+ packs, ≥ 1k MCP recommends/mo, measured ledger at p95 bench turnaround ≤ 24h.

---

## Annex A — Verified arXiv Research (retrieved 2026-08-17 via arXiv + Semantic Scholar APIs)

Pattern families that inform `architecture_pattern` taxonomy, the benchmark protocol, and the evolution-graph arXiv links. Each ID was fetched and matched against live API metadata; no citation here is recalled from memory.

### A.1 Reasoning–acting loops (single-agent control flow)
| Pattern | Paper | What it supports in this design |
|---|---|---|
| ReAct (interleaved reasoning + acting) | Yao et al., arXiv:2210.03629 | Canonical baseline pattern; most seed packs are ReAct-derived; benchmark suite includes a ReAct control |
| Tree of Thoughts (explicit search over thoughts) | Yao et al., arXiv:2305.10601 | `tree_search` architecture_pattern family; used for high-branching tasks like planning |
| Language Agent Tree Search (unified reasoning/acting/planning with search) | Zhou et al., arXiv:2310.04406 | Generalize ToT+ReAct into one control loop; candidate pattern for planner-heavy packs |
| Reflexion (verbal self-feedback + memory) | Shinn et al., arXiv:2303.11366 | `reflexion` family with retry-from-feedback; benchmark protocol must count retry attempts in cost |

### A.2 Multi-agent orchestration
| Pattern | Paper | What it supports in this design |
|---|---|---|
| AutoGen (multi-agent conversation framework) | Wu et al., arXiv:2308.08155 | Reference implementation for `planner→workers→conversation` packs; compatibility notes in pack metadata |
| MetaGPT (role-based SOP multi-agent coding) | Hong et al., arXiv:2308.00352 | `role_sop` pattern family; coding-factory seed pack is MetaGPT-derived |
| AgentVerse (collaboration/competition environments) | Chen et al., arXiv:2308.10848 | Collaborative worker topologies for research/synthesis packs |
| LLM-Agent survey | Wang et al., arXiv:2308.11432 | Taxonomy source for `architecture_pattern` enum (planning, memory, tool use, reflection) |
| Rise and Potential of LLM-based Agents survey | Xi et al., arXiv:2309.07864 | Market/pattern landscape evidence for the catalog's pattern descriptions |
| Multi-agent systems challenges | Han et al., arXiv:2402.03578 | Documents open problems (task allocation, communication cost) — informs risk table + bench design for multi-agent packs |
| Agentic design patterns | arXiv:2601.03624 | Pattern catalog for composing agentic systems — cross-check for our pattern enum as it matures |

### A.3 Evaluation & benchmarking (protocol evidence)
| Paper | What it supports in this design |
|---|---|
| AgentBench — Liu et al., arXiv:2308.03688 | Multi-environment agent evaluation framing; our task taxonomy takes the "environment×task" matrix idea |
| GAIA — Mialon et al., arXiv:2311.12983 | Real-world assistant tasks with strict, verifiable answers; used as one hidden-instance source |
| SWE-bench — Jimenez et al., arXiv:2310.06770 | Repo-level task instances for `repo_bugfix`; the coding-factory pack's eval corpus |
| τ-bench — Yao et al., arXiv:2406.12045 | Tool-agent-user interaction benchmark; models the tool-call fidelity dimension of our bench protocol |
| TheAgentCompany — Xu et al., arXiv:2412.14161 | Consequential long-horizon real-world tasks; informs the long-horizon subset of benchmark suites |
| Agentless — Xia et al., arXiv:2407.01489 | Agentless vs agentic comparison shows measured deltas matter — supports publishing *measurements*, not architectures, as the commodity |

### A.4 Cost/quality measurement (the differentiator's evidence base)
| Paper | What it supports in this design |
|---|---|
| FrugalGPT — Chen et al., arXiv:2305.05176 | LLM cascades: cost reduction with quality preservation — the conceptual proof that cost/quality surfaces are real and exploitable |
| RouteLLM — Ong et al., arXiv:2406.18665 | Learned routing with preference data — validates the model-replaceable-slot assumption in pack metadata |
| Hybrid LLM (cost-efficient quality-aware query routing) — arXiv:2404.14618 | Quality-aware routing datasets/methods; supports the ranker's cost/quality projection |

### A.5 Reference architecture
| Paper | What it supports in this design |
|---|---|
| Cognitive Architectures for Language Agents (CoALA) — Sumers et al., arXiv:2309.02427 | Memory/action/decision taxonomy — the schema for pack `memory/` + `context` sections in manifest v1 |

---

## Provenance & Doctrine Notes

- **HOW-known:** This spec is `MACHINE-PROPOSED` (origin=machine). Its inputs are `EXTRACTED` from real sources: `reports/agentpacks/report.md`, `ideas/agent-framework-site.md`, `ideas/agent_infra_registry.md`, `ideas/final-shortlist.md`, sibling product reports (knee, agentsla, archbench). arXiv citations were verified against live arXiv/Semantic Scholar APIs on 2026-08-17 (22 records, see Annex A); none were recalled from memory, and no numeric performance claims beyond the fetched abstracts are asserted.
- **Not yet:** `HUMAN_REVIEWED` / `ADJUDICATED`. Bench numbers in examples (e.g. success_rate 0.92) are illustrative schema shapes, not measured results of any real pack.
- **Banned-language:** no claim of provability, correctness, or "best" is made; the recommendation surface is designed to abstain (`NO_RECOMMENDATION`) rather than fabricate.

---

*Agentpacks architecture spec v1 · VentureLab · generated 2026-08-17T20:21Z*