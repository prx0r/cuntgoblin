# Architecture Search Space

## Nodes / roles

- planner
- coordinator
- worker
- specialist
- researcher
- critic
- verifier
- certifier
- memory manager
- router
- aggregator

## Edges

- sequential
- parallel
- delegation
- conditional
- review
- retry
- escalation
- consensus
- memory read/write

## State

- stateless
- scratchpad
- append-only artifacts
- persistent task graph
- episodic memory
- semantic memory
- shared blackboard

## Context policies

- full shared
- role-scoped
- summary handoff
- artifact-only
- selective critical-context retention

## Verification

- none
- self-check
- independent reviewer
- deterministic test
- multi-review
- formal/schema gate

## Model slots

Each role has a HotSwap TaskSpec.

Do not search model identity and architecture topology as one uncontrolled space at first.

Recommended:
1. freeze model policy while searching topology;
2. optimize model slots after structural candidate exists;
3. jointly optimize only later.
