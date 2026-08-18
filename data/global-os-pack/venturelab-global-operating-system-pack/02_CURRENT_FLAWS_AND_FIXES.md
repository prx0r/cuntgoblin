# Current Flaws and Fixes

## F1 — Multiple durable truths
Potential truth currently exists in files, Hermes Kanban, Cron state, AgentHub state,
and future runtime databases.

Fix: Postgres owns global workflow/product state. Everything else is a projection.

## F2 — No globally idempotent GO
Restarting managers can recreate work.

Fix: unique trigger IDs + logical job dedupe keys + Job != Attempt.

## F3 — No portfolio-wide budget
HotSwap can optimize a task without knowing the day's total allocation.

Fix: global budget accounts and reservations.

## F4 — Schedule ownership ambiguous
Fix: one Postgres schedule registry. Hermes Cron may only invoke/notify.

## F5 — Nested routing
HotSwap + Hermes + LiteLLM + provider fallback can multiply attempts.

Fix: HotSwap owns cross-model fallback. Lower layers only operate inside an explicitly
allowed equivalence/deployment group.

## F6 — External research repo drift
Fix: third_party lockfile, pinned SHA, license metadata and adapters.

## F7 — Stale authority at commit time
A long-running task may finish after evidence/budget/target state changed.

Fix: commit-time validation + commit intents.

## F8 — Individual hashes without global checkpoint
Fix: append-only event sequence + periodic Merkle roots.

## F9 — Product output divergence
Fix: global Product Completion Contract and repo conventions.

## F10 — Partial external release
GitHub push can succeed while deployment fails.

Fix: explicit release saga; `RELEASED` only after live smoke verification.
