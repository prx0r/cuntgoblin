# Router Benchmark

Compare:

A. fixed current Hermes model
B. cheapest Dell-qualified
C. free-first deterministic
D. HotSwap ECPS
E. HotSwap ECPS + bandit
F. HotSwap + verified cascade

## Evaluate by task cell

Metrics:

```text
success_rate
certification_rate
mean_task_cost
median_task_cost
cost_per_success
free_completion_rate
escalation_rate
mean_wall_time
p95_wall_time
quota_exhaustion_events
rework_count
```

## Required win condition

Do not promote a more complex router merely because spend falls.

For its target cells it must:
- satisfy quality floor;
- not increase release defects;
- reduce cost per success or materially improve success/SLO.

## Held-out split

Split chronologically where possible:
- train
- shadow validation
- held-out live period

Avoid training and declaring success on the same factory runs.
