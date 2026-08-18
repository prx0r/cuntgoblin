# Router Training Dataset

One row per attempted route within a task:

```json
{
  "task_id": "...",
  "cell_id": "...",
  "task_features": {...},
  "route_features_at_decision": {...},
  "propensity": 0.0,
  "selected": true,
  "attempt_index": 0,
  "usage": {...},
  "runtime": {...},
  "evaluation": {
    "success": true,
    "score": 1.0,
    "evaluator": "pytest",
    "deterministic": true
  },
  "economics": {
    "request_cost": 0.0,
    "total_task_cost": 0.01
  }
}
```

## Propensity

When exploration/randomization is used, log selection probability where practical.

This is required for serious off-policy evaluation later.

## Prompt privacy

For learned router training, prefer:
- task metadata
- locally-computed embeddings
- hashes/references

Avoid unnecessary retention of secrets/source code in centralized analytics.
