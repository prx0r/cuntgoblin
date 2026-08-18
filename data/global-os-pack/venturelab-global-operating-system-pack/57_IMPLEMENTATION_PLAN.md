# Implementation Plan

## CP-G0 — Dell self-description
Regenerate MANIFEST at current HEAD and add CI freshness gate.

## CP-G1 — global contracts
IDs, schemas, WorkflowSpec, Job/Event/Artifact state machines.

## CP-G2 — Postgres ledger/queue
Migrations, idempotency, SKIP LOCKED leases.

## CP-G3 — Manager daemon
Scheduler, priority, budgets, lease recovery, singleton leader.

## CP-G4 — artifact/Merkle
Content-addressed store, proper RFC8785 canonicalizer, checkpoint/proof integration.

## CP-G5 — Hermes projection
Global Job <-> per-run Kanban board + reconciliation.

## CP-G6 — HotSwap routing authority
Remove competing hard-coded model/fallback policy and propagate retry/budget ownership.

## CP-G7 — dry-run + chaos subset
No autonomous publishing yet.

### After CP-G7
Read-only/experimental `venturelab go` may run.

## CP-G8 — market schedules
Oracle -> signals -> topics -> opportunities.

## CP-G9 — product build workflow
Completion Contract end-to-end.

## CP-G10 — GitHub/deploy release saga
Live verification.

## CP-G11 — AgentHub operations
Benchmark queue, lineage, promotion.

## CP-G12 — Paper Intake Factory
Paper2Agent/Paper2Code adapters.

## CP-G13 — Router Research Lab
LLMRouterBench adapter, optional upstream algorithm reproductions.

## CP-G14 — Dell GTM
Public API/MCP/site/trust pages/SDK integrations.

## CP-G15 — VisionTruth prototype
VLM modality schema + benchmark adapter.

## CP-G16 — VideoTruth research prototype
Understanding/generation cost-unit schemas.

## CP-G17 — historical replay
Schedules, market thresholds and router algorithms.

## CP-G18 — optional Temporal adapter
Only when operational triggers justify it.

## CP-G19 — bounded evolution
Only after stable outcome history.
