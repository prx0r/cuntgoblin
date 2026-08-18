# Outcome Telemetry

Every LLM task produces a RouterOutcome.

## Request/runtime

- plan_id
- task_id
- route_id
- actual provider/deployment
- fallback index
- input tokens
- output tokens
- estimated cost
- actual cost
- latency
- TTFT/TPS if observed
- error class
- retry count

## Task evaluation

- evaluator id/version
- PASS/FAIL/UNKNOWN
- score
- deterministic?
- evidence artifact
- repair/escalation needed
- final route that completed task

## Economic result

- first-attempt cost
- total task cost
- free quota used
- paid cost
- wall time
- number of model attempts

## Derived

```text
cost_per_success
success_rate
escalation_rate
wasted_failure_cost
free_completion_rate
quota_efficiency
```

## Important

The unit of optimization is the entire factory task, not individual completion requests.
