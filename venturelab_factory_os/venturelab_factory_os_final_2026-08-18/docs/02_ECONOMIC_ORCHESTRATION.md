# Economic orchestration

HotSwap asks: given a task, which execution route is cheapest while satisfying quality?

Factory OS adds:
- should the task run at all?
- which factory gets scarce compute first?
- when should work stop?

## Opportunity decision

Estimate:
- demonstrated need
- recurrence
- actionability
- verifiability
- distribution
- timing
- competition
- evidence confidence
- build cost
- maintenance
- policy friction
- data moat
- factory reuse

## Factory-run value

```text
expected_run_value =
  P(certified_output) * expected_output_value
  - expected_run_cost
  - expected_followup_cost
  - opportunity_cost_of_compute
```

## Node value

```text
marginal_utility =
  expected_decision_gain
  + expected_artifact_gain
  + expected_risk_reduction
  - expected_execution_cost
  - latency_penalty
  - redundancy_penalty
```

## Opportunity cost

Compare the chosen node to the best other eligible ready node. Store:
- candidate-set hash
- policy version
- estimate timestamp
- uncertainty
- underlying evidence refs

## Stop is a real action

Stop when:
- expected marginal value <= 0
- budget exhausted
- evidence unavailable
- quality ceiling reached
- repeated failure class
- opportunity expired
- policy blocked
- another factory strictly dominates expected return
