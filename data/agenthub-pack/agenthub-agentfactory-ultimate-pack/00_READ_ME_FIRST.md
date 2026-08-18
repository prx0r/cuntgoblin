# AgentHub + Agent Factory + Architecture Benchmark Lab — Ultimate Build Pack

Target:
- `prx0r/cuntgoblin`
- downstream integration with Dell + HotSwap
- Hermes-first runtime, runtime-adapter architecture

Reviewed VentureLab head:
`22094efe30dc1a38d8e66ab545f543dd6deb3d93`

## Endgame

Market Intelligence finds evidence-backed Opportunities.
Solution Lab proposes possible Solutions.

When a solution is inherently agentic:

```text
Opportunity
  ↓
SolutionHypothesis
  ↓
AgentArchitectureResolver
  ↓
┌───────────────────────┬────────────────────────┬─────────────────────────┐
│ reuse existing system │ fork/compose existing  │ synthesize architecture │
└───────────────────────┴────────────────────────┴─────────────────────────┘
  ↓
ArchitectureBuild
  ↓
HotSwap assigns models to role/task slots
  ↓
Hermes/runtime adapter compiles + runs it
  ↓
AgentHub Benchmark Lab
  ↓
certified outcomes
  ↓
AgentHub Registry + lineage
  ↓
Architecture Factory learns/evolves
```

## The crucial distinction

`ArchitectureBuild` can be generated for ONE problem.

A new reusable named `AgentSystem` should be promoted only after evidence shows the
architecture is useful beyond one lucky task.

This prevents architecture spam.

## AgentHub is not another "agent registry"

It specializes in:
- complete agent systems
- topology / roles / state / tools / verification
- pinned reproducible builds
- installation and operation
- benchmark evidence
- architecture lineage/forks
- architecture resolution
- architecture search/evolution

## Core objects

1. AgentSystem
2. ArchitectureBuild
3. Installation
4. Run
5. BenchmarkSuite
6. BenchmarkTask
7. Assessment
8. ArchitecturePattern
9. ArchitectureLineage
10. ArchitectureNeed
11. AgentFactoryProposal

## Benchmark philosophy

Never compare vague "agents".

Compare a pinned:

```text
architecture
× runtime version
× model-slot policy
× tool set
× environment
× benchmark version
```

and report confidence intervals, cost, failure/recovery behavior and artifacts.

## Current repo correction

The current `AGENTS.md` says "Always use mimo v2.5".

That MUST be replaced by the HotSwap contract:

> Every model-consuming role/task emits a TaskSpec. HotSwap + Dell selects the
> current economic model-route. Architecture manifests specify requirements, not
> permanently hard-coded provider/model names.

Fixed model names are allowed only for benchmark-control experiments.

## First proof

Do NOT claim AgentHub complete because a registry page exists.

PASS requires:

1. ingest/describe one real architecture (`cuntgoblin` itself);
2. compile it through Hermes adapter;
3. benchmark at least two architecture variants under the same model policy;
4. demonstrate a structural result not reducible to model choice;
5. fork one architecture with a semantic architecture diff;
6. resolve one SolutionHypothesis to reuse/fork/synthesize;
7. synthesize one experimental architecture when reuse does not fit;
8. benchmark/certify it;
9. refuse to promote it to reusable AgentSystem unless promotion gates pass.
