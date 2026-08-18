# Hermes / Nous Research Orchestration

Current Hermes already provides useful primitives:
- durable SQLite-backed Kanban,
- dispatcher workers,
- idempotency keys,
- max runtime/retries,
- scratch/worktree workspaces,
- skills,
- cron,
- subagents,
- programmatic HTTP/JSON-RPC/ACP surfaces,
- model/provider switching.

## Split of authority

### VentureLab owns
- opportunity/product/evidence IDs,
- research/build DAG,
- budgets,
- artifact hashes,
- certification,
- publication state,
- outcome telemetry,
- HotSwap learning,
- factory selection.

### Hermes Kanban owns
- worker dispatch,
- workspace lifecycle,
- heartbeats,
- per-worker runtime,
- operator visibility.

Kanban is an execution adapter, not the venture database.

## Job mapping

| VentureLab | Hermes |
|---|---|
| job id | stored with Hermes task ID |
| dependency | readiness / parents |
| skills | `--skill` |
| timeout | `--max-runtime` |
| retries | `--max-retries` |
| isolation | `--workspace` |
| dedupe | `--idempotency-key` |
| role | `--assignee` |

## Initial profiles

```text
venture-researcher
venture-builder
venture-verifier
venture-publisher
```

Give each a narrow skill and tool policy.

## Integration path

1. Persist local job.
2. Create Hermes Kanban task using board-scoped CLI + `--json`.
3. Persist returned Hermes task ID.
4. Dispatcher runs worker in isolated workspace.
5. Worker emits artifact and machine summary.
6. VentureLab ingests it.
7. Independent verifier accepts/retries/fails.
8. Commit application state/outcome.

## Richer programmatic runtime

For P0, a checked subprocess is acceptable.

Later use:
- Hermes HTTP API for language-independent async runs,
- TUI JSON-RPC for fine-grained lifecycle/approvals/cancel,
- `AIAgent` in-process only if tight coupling is desired.

## Cron

Use cron for recurring scouts/freshness checks, not as the primary durable build queue.

## Skills

Store skill hash/version, provenance, allowed tools, eval result and promotion state. Auto-modified skills must pass frozen evals before promotion.
