# Expected Cost Per Successful Task

Token price is only one component.

## Two-route cascade

Cheap route A:
- cost C_A
- success probability P_A

Escalation B:
- expected completion cost E_B

Then:

```text
E_A = C_A + (1 - P_A) * E_B
```

If failed attempts create extra repair/retry cost R:

```text
E_A = C_A + (1-P_A)*(R + E_B)
```

## Compare against strong route

Use cheap-first iff:

```text
C_A + (1-P_A)*(R + E_B) < E_B
```

Rearrange to derive the minimum cheap-model success rate needed to justify it.

This is much more useful than:
`input_per_m is cheaper`.

## Time cost

For automated factories time may still matter:
- worker occupancy
- deadline/SLO
- queue blocking

Optional:

```text
latency_penalty = lambda_time * expected_wall_seconds
```

Do not invent a dollar value unless configured.

## Criticality risk

For release gates add:

```text
risk_penalty =
failure_probability
× downstream_failure_cost
```

If downstream failure cost is UNKNOWN, use policy rules rather than fabricated dollars.

## Output metrics

Every plan exposes:

```text
estimated_first_attempt_cost
estimated_completion_cost
predicted_success
success_lower_bound
free_quota_cost
fallback_expected_cost
```
