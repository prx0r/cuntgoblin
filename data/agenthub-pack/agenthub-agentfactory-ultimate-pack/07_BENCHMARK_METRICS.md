# Benchmark Metrics

## Task performance
- completion rate
- deterministic pass rate
- partial score
- quality score
- quality lower confidence bound

## Economics
- input tokens
- output tokens
- tool calls
- model calls
- first-attempt cost
- total task cost
- cost per success

## Time
- wall-clock time
- critical-path time
- idle time
- coordination overhead

## Architecture behavior
- decomposition quality
- coordination success
- delegation correctness
- information retention
- duplicate work
- parallel efficiency
- verifier precision/recall when measurable

## Reliability
- run variance
- crash recovery
- resume success
- fault recovery rate
- cascade radius
- retries
- unrecovered latent failure count

## Reproducibility
- clean-start success
- deterministic environment hash
- artifact hash
- build identity
- run replay completeness

## Complexity
- role count
- graph nodes/edges
- active parallel agents
- prompt/config complexity
- dependency count

## Architecture efficiency

Examples:

```text
cost_per_success = total_cost / successful_tasks

parallel_efficiency =
serial_estimated_makespan / (workers * actual_makespan)
```

Do not claim a metric is meaningful unless its assumptions are documented.
