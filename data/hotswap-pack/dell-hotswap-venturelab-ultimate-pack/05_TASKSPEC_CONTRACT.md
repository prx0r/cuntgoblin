# TaskSpec — Contract Between Factory and HotSwap

Every LLM-consuming factory action MUST emit a TaskSpec.

```yaml
task_id: t_...
factory: agent-infrastructure
product: mcptruth
phase: build

task_kind: coding_patch
difficulty: medium
criticality: important

input:
  estimated_tokens: 18000
  expected_output_tokens: 5000
  context_tokens_min: 64000

capabilities:
  tools: required
  json_schema: preferred
  vision: forbidden

quality:
  floor: .76
  target: .84
  evaluator: pytest
  deterministic_gate: "python -m pytest"

economics:
  free_policy: prefer
  paid_allowed: true
  task_budget_usd: .20

latency:
  max_wall_seconds: 600
  throughput_preference: medium

learning:
  exploration_allowed: true
  route_diversity_required: false
```

## Criticality

- `disposable`
- `routine`
- `important`
- `release_gate`
- `production`

Criticality changes:
- success floor;
- exploration;
- paid escalation;
- verifier requirements;
- route diversity.

## Factory tasks MUST declare the evaluator

If no evaluator exists:
- success feedback is UNKNOWN;
- do not train the router as though the task succeeded merely because Hermes exited 0.
