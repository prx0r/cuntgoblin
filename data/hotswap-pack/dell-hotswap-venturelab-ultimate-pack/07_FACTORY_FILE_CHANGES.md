# Exact VentureLab File Changes

Current factory does not yet have a task/model-policy domain object.

Add:

```text
factory/domain/task.py
factory/runtime/
  __init__.py
  hotswap.py
  hermes_runner.py
  evaluation.py
factory/policies/
  model_policies.yaml
schemas/task-spec.schema.json
```

## `factory/domain/task.py`

Add:
- TaskSpec
- TaskKind
- Difficulty
- Criticality
- CapabilityRequirements
- QualityContract
- EconomicPolicy
- LearningPolicy

## Kanban/task decomposition integration

When coordinator/specification creates a task, it must attach:

```json
{
  "model_policy": {
    "task_kind": "coding_patch",
    "difficulty": "medium",
    "criticality": "important",
    "quality_floor": 0.76,
    "free_policy": "prefer"
  }
}
```

If missing, the runtime derives conservative defaults from lane/phase and logs:

`TASK_POLICY_INFERRED`

but the long-term goal is explicit metadata.

## Builder integration

Before launching a Hermes task:

```python
plan = hotswap.resolve(task_spec)
result = hermes_runner.run(task, plan)
evaluation = evaluator.grade(task, result)
hotswap.record_outcome(plan, evaluation)
```

## Certification integration

Certifier tasks must:
- set `criticality=release_gate`
- disable exploration
- prefer model-family diversity from the builder where possible
- record outcome separately from builder success

## Market Intelligence integration

Scout/extraction calls:
- free-first
- high volume
- cheap cells

Market adjudication:
- stronger cells

This is exactly where task-aware routing saves money.
