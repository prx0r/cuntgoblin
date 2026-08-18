# COPY INTO THE CUNTGOBLIN / VENTURELAB AGENT

You are converting VentureLab into a durable autonomous operating system.

Reviewed baseline:
`2fcc6abcce78d4fac8c516e62069827d0e8cf931`

Read this entire pack first.

## Do not press autonomous GO until CP-G0..CP-G7 PASS.

### Global truth
Postgres owns schedules/runs/jobs/events/artifact metadata/budgets/releases/checkpoints.

Hermes Kanban is a per-run collaboration projection.
Hermes Cron may trigger a manager workflow but is not canonical scheduling truth.

### Dell
Functional hardening landed, but regenerate the current MANIFEST and prove it matches HEAD.

### Routing
HotSwap is the only cross-model selector.
Do not leave static `always use mimo` or unrelated cross-model fallbacks active.
Propagate one retry budget through Hermes/LiteLLM/provider layers.

### Integrity
Use proper RFC8785 JCS implementation in production.
Hash all durable artifacts.
Add Merkle checkpoints over ordered event sequence.

### External repos
Keep router/paper projects pinned behind lab adapters.
Do not merge experimental code into production core without benchmark promotion.

### Paper workflow
paper -> reproduce/reconstruct -> MCP/agent -> benchmark -> AgentHub -> market-transfer.

### Product stack
Use the default stack unless a benchmark/reason justifies deviation.

### Required final proof
1. `venturelab doctor`
2. `venturelab go --dry-run`
3. start tiny-budget manager
4. one schedule creates exactly one Run
5. multiple workers cannot duplicate a Job
6. Hermes task projects/reconciles
7. a free-first HotSwap route fails or rate-limits and safely fails over
8. evaluator determines task success
9. event/artifact chain is complete
10. Merkle checkpoint verifies
11. manager restart does not duplicate effects
12. a build reaches certification
13. release saga accurately handles full or partial external success

Create `GLOBAL-OS-FINAL.md` with exact SHAs, commands, tests, queue/budget stats,
checkpoint root, Dell manifest status, HotSwap behavior, AgentHub status, paper/router
lab status, limitations, and GO/NO-GO.
