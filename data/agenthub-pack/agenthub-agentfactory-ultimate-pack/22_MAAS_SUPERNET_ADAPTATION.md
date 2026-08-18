# MaAS-style Supernet Adaptation

MaAS's strongest transferable idea is NOT a specific MetaGPT implementation.

It is:

> There may be no single best multi-agent architecture. Sample a task-dependent
> architecture from a learned distribution.

## AgentHub supernet

Operators:
- plan
- research
- execute
- critique
- verify
- aggregate
- memory
- retry

Edges have activation probabilities conditioned on ArchitectureNeed/task features.

Example:

```text
easy extraction
→ worker only

medium code patch
→ planner → worker → tests

hard feature
→ planner → parallel workers → aggregator → verifier
```

## Economics

Every sampled graph records:
- model calls
- tokens
- wall time
- success

HotSwap resolves model slots after topology selection.

## Training

Use VentureLab outcomes to update operator/path preference.

Initially:
simple contextual frequency/bandit.

Later:
learned controller.

## Constraint

Supernet output must compile into a valid AgentSystem topology and pass graph validation.
