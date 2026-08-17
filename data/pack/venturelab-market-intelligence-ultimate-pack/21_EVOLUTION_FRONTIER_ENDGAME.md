# Endgame — Evolving Agent/Factory Frameworks

Do NOT start here. Evolution is valuable only after immutable evidence and outcome
contracts exist.

## Representation: Agentic Computation Graph

Represent every factory run with three layers:

### TemplateGraph
Reusable architecture:
- roles
- tools
- edges
- prompts
- model policies
- verification topology

### RealizedGraph
The concrete graph selected/generated for one task.

### Trace
What actually happened:
- calls
- artifacts
- retries
- costs
- decisions
- failures

This separation is essential for meaningful architecture optimization.

## Mutable surfaces

Safe early mutation surfaces:
- research query mix
- source allocation
- topic thresholds
- opportunity rule weights
- task decomposition
- model assignment
- worker count
- verifier count
- retry policy
- tool selection
- prompt templates
- product compiler patterns

## Immutable/fixed surfaces

Do NOT let evolution rewrite:
- artifact identity
- provenance requirements
- immutable observations
- permission boundaries
- zero-tolerance safety/truth invariants
- historical outcome records

## Evolution engines

### ShinkaEvolve-style bounded evolution
Good for modules with explicit evaluator:
- scoring algorithm
- query planner
- deduper
- ranker
- build optimizer

Candidate → evaluator → archive → mutation.

### Darwin Gödel Machine-style archive/tree
Maintain diverse descendants instead of one "latest best".

Use for:
- agent architectures
- factory strategies
- workflow graphs

### AlphaEvolve principle
Use multiple proposal models plus automated evaluators and a candidate database.

### Red Queen principle
Static evaluators eventually become targets.

Allow evaluator/utility evolution only at controlled epoch boundaries.

Keep immutable floor gates:
- provenance
- hard constraint correctness
- release correctness
- safety/permission invariants

## Multi-objective fitness

Never optimize factory evolution on one score.

Track Pareto objectives:

```text
opportunity quality
certified product success
real adoption
cost
time
maintenance burden
evidence coverage
novelty/diversity
```

## Shadow-first deployment

Evolution sequence:

1. historical replay
2. offline benchmark
3. shadow variant
4. bounded live A/B
5. archive
6. promote only with statistical/operational evidence

No uncontrolled self-modification of production.
