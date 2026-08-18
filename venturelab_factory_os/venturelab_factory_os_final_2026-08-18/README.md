# VentureLab Factory OS — Final Integration Pack
**Date:** 2026-08-18
**Target:** `prx0r/cuntgoblin`
**Reviewed head:** `a56716251f4c60a2593e71efc6c88c5c61beb5bf`

This pack extends the existing system rather than replacing HotSwap, market scoring,
AgentHub, Hermes, or working verification code.

## Thesis

VentureLab is an economic control plane for autonomous factories.

It must decide:
1. what changed;
2. what opportunities exist;
3. which opportunity deserves compute;
4. which factory should handle it;
5. which ready work node should execute;
6. which worker/model/provider HotSwap should route it to;
7. whether the result passed independent verification;
8. what it cost;
9. what happened after release;
10. what the system should learn.

## Read first

1. `docs/00_FINAL_ARCHITECTURE.md`
2. `docs/01_MIGRATION_FROM_CURRENT_REPO.md`
3. `agent/MASTER_IMPLEMENTATION_PROMPT.md`
4. `tasks/IMPLEMENTATION_TASKS.json`
5. `checklists/PHASE_ACCEPTANCE.md`
6. `reference/venturelab_os/`
7. `schemas/`, `factory_manifests/`, `team_manifests/`

The reference package is runnable outside the repo. The implementation agent should transplant
it under `factory/os/` and adapt imports instead of bulk-overwriting the repository.
