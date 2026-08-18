# Agent Factory Decision Logic

## Step 1 — resolve existing

Compute ArchitectureFit.

```text
>= .78 REUSE
.62-.78 FORK_OR_COMPOSE
< .62 SYNTHESIZE_EXPERIMENTAL_BUILD
```

## Step 2 — synthesize

Use:
- baseline templates
- Pattern Registry
- semantic mutations
- ArchitectureNeed

Generate small candidate batch.

## Step 3 — cheap screen

- graph validity
- permissions
- deterministic orchestration simulation
- resource estimate
- HotSwap model-slot satisfiability

## Step 4 — real benchmark

Run promising candidates on target tasks.

## Step 5 — select

Pareto archive, not just max score.

## Step 6 — deploy solution

The winning build can solve the original solution even if it never becomes a named
reusable AgentSystem.

## Step 7 — promotion check

Only promote after repeated cross-task evidence.

This closes the loop from opportunity → autonomous architecture → product/result.
