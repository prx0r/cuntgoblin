# Hermes Runtime Compiler

Hermes is the first runtime adapter.

## Compile

Input:
AgentSystem Manifest + ArchitectureBuild + resolved model slots.

Output:
- Hermes task graph/kanban configuration
- role instructions
- task decomposition policy
- worker limits
- per-task HotSwap profiles
- verifier/certifier role
- filesystem/artifact contract
- fallback behavior

## Current doctrine patch

Replace:

`Always use mimo v2.5`

with:

```text
All model-consuming tasks MUST carry a TaskSpec/model slot.
Runtime model selection MUST use HotSwap unless benchmark mode explicitly freezes models.
```

## Dynamic workers

Cardinality:

```yaml
cardinality:
  min: 1
  max: 8
  policy: difficulty_and_parallelism
```

Compiler can ask orchestration policy how many workers to activate.

## Artifact handoffs

Prefer artifact IDs + hashes over copying entire transcript between workers.

This improves reproducibility and context control.

## Verifier independence

Compiler should isolate verifier context from builder chain where architecture requires
independent verification.
