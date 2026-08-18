# Search Algorithms

## Stage 0 — Handful of strong baselines

Always compare:
- single agent
- planner-worker
- worker-verifier
- planner-worker-verifier
- parallel workers + aggregator

If a complex search cannot beat these, stop.

## Stage 1 — Beam / local search

Cheap and interpretable.

Generate semantic mutations, benchmark, retain Pareto candidates.

## Stage 2 — AFlow-style workflow search

Search compositions of reusable operators using tree/search methods.

Useful once operator library is stable.

## Stage 3 — MaAS-style agentic supernet

Represent architecture as a distribution over:
- operators
- edges
- roles
- execution paths

Sample query-specific subarchitectures.

This aligns strongly with AgentHub's eventual task-conditioned resolver.

## Stage 4 — archive/open-ended evolution

DGM/Shinka-inspired:
- archive diverse high-quality builds;
- sample parents;
- mutate;
- benchmark;
- retain useful stepping stones.

## Stage 5 — co-evolve meta-search

Only after governance and benchmark integrity are strong.

Hyperagent/DGM-like meta-components may improve how architectures are generated.

Do not permit evaluation/safety contracts to self-modify inside the same epoch.
