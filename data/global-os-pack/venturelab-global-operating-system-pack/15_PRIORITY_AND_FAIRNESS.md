# Intelligent Priority Scheduler

Base:

```text
value =
  strategic_value
  × evidence_confidence
  × probability_of_success
  × urgency

cost =
  expected_llm_cost
  + worker_time_cost
  + scarce_quota_shadow_cost

priority = value / max(cost, epsilon)
```

Then apply:
- blocker multiplier
- dependency-unlock multiplier
- staleness multiplier
- near-release completion multiplier

Suggested initial queue-share floors:
- 50% highest-value/release work
- 25% maintenance/verification
- 15% exploration
- 10% starvation prevention

These are policy priors, not hard science. Version and calibrate them.

Queue classes:
CRITICAL, RELEASE, NORMAL, EXPLORATION, MAINTENANCE, BULK.

Bulk market research may never starve verification/recovery.
