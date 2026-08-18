# Dell Final Push — Peer Review

## Verdict

Dell is close enough to become HotSwap's truth plane, but it is NOT honestly "final"
at the reviewed head.

The ontology and data architecture should be treated as stable. The remaining problems
are concentrated in certification and route decision semantics.

## P0 — Final certificate is overclaiming

`app/certify_final.py` says the critical mutation requirement is 100%, but explicitly
marks `9/10 (90%)` as PASS.

That violates the final hardening contract.

Fix:

```text
critical mutation kill: 100%
overall mutation kill: >=95%
```

and distinguish the two sets explicitly.

## P0 — Schema gate does not execute the schema check

The certifier imports `check_schema`, then immediately appends PASS without invoking
the function.

A release certificate cannot include non-executed gates.

Fix:
- call the check
- assert the returned result
- store stdout/stderr
- fail closed

## P0 — Max budget is not actually enforced correctly

Current DecisionService applies the max-cost constraint before workload cost is
calculated and only checks whether input price is unknown.

It does not reject a known-priced route whose actual estimated workload cost exceeds
`max_total_cost_usd`.

Required order:

```text
construct route
→ calculate workload cost
→ hard reject cost UNKNOWN under hard policy
→ hard reject total > budget
→ rank
```

## P0 — Unknown output price is still coerced to zero

Current workload calculation uses:

```python
(candidate.output_per_m or 0)
```

For a workload that generates output tokens, missing output price must make total
cost UNKNOWN unless the offer explicitly proves output is zero-priced.

## P0 — Route candidates are not really endpoint-level

`build_candidates(offers, endpoints)` accepts endpoints but does not use them to build
the route candidate set.

That means `model × endpoint × offer` remains a schema promise more than a runtime fact.

HotSwap depends on actual endpoint-level identity because provider failures, rate limits,
latency and quotas are route-specific.

## P0 — Confidence still equals coverage

DecisionService:
`confidence = evidence_coverage`.

Scoring V3 likewise computes confidence by counting populated dimensions.

They are still the same missing-data statistic under two labels.

Final definition:

```text
coverage  = how much required evidence exists
confidence = how strong/recent/independent that evidence is
```

## P0 — Missing soft metrics receive invented 50s

DecisionService adds `50` for unknown reliability and throughput during scoring.

Missing evidence must not receive a neutral performance score.

Use:
- lower-confidence penalty;
- Pareto incomparability;
- conservative bound;
- or exclude when required.

Never invented neutral values.

## P0 — "quality" is partly inferred from context length

DecisionService's quality branch rewards 128k context.

Advertised context is a capability, not model quality.

Task quality should come from:
- task benchmark evidence;
- local factory outcome posterior;
- explicit evaluator history.

## P1 — ScoringV3 is not yet truly task-weighted

Task profiles contain `quality_weight`, `cost_weight`, etc., but `score_route()` takes
a simple geometric mean over all present dimensions rather than using those task weights.

The profile currently affects benchmark selection and eligibility more than the actual
aggregation.

HotSwap should therefore use Dell as a fact source but own the final task-aware ECPS
decision until Dell's scoring semantics are corrected.

## P1 — Capability remains numeric

Tools capability becomes 80/20.

Prefer exact factual:
TRUE / FALSE / UNKNOWN
and separately measured:
tool_success_rate.

## Dell acceptance before calling it complete

1. true route construction from endpoints
2. exact workload budget enforcement
3. unknown output price remains unknown
4. confidence != coverage
5. no invented 50s
6. task quality not derived from context
7. scoring task weights actually used or removed
8. critical mutation set 100%
9. schema cert actually executes
10. final cert rerun from clean checkout

HotSwap can be developed in parallel but should treat uncertain Dell fields conservatively.
