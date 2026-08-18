# Exact VentureLab Patch Plan

## 1. `AGENTS.md`

Delete/replace:
`Always use mimo v2.5`

New rule:

> All model-consuming factory tasks MUST declare a TaskSpec/model slot.
> HotSwap resolves model routes from Dell. Fixed model names are permitted only for
> explicit benchmark-control runs.

## 2. `factory/domain/`

Add:
- architecture.py
- architecture_need.py
- benchmark.py

## 3. `factory/ideas/solution_lab.py`

When solution type == `agentic_system`:
produce ArchitectureNeed and route into AgentHub Resolver.

## 4. `factory/builders/`

MVPBuilder remains for normal product archetypes.

Add:
`AgentSystemBuilder`

It builds ArchitectureBuild candidates from manifests/templates/patterns.

## 5. `factory/certification/`

Add architecture certifier:
- manifest
- doctor
- clean-run
- benchmark
- lineage
- model-policy control

## 6. `factory/runtime/` or `factory/runtimes/`

Hermes compiler uses HotSwap slot resolutions.

## 7. `factory/market/`

No direct change required.
Market Intelligence supplies Opportunities upstream.

## 8. Outcome Oracle

Add architecture/build outcomes so MetaFactory can learn:
which architecture families work for which solution classes.
