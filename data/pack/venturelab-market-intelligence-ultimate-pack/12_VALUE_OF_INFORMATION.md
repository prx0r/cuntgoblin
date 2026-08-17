# Value of Information — Choosing What to Research Next

The factory should not research every uncertainty equally.

## Goal

Select the next research action that is most likely to improve the downstream decision.

## Approximate EVSI

For research action A:

```text
EVSI(A) =
P(decision changes after A)
× expected value gap between current best and alternative
× confidence impact
- expected research cost
```

Since exact Bayesian models are expensive, start with a deterministic approximation.

## Simple approximation v1

For uncertain dimension d:

```text
decision_sensitivity =
abs(score_if_low(d) - score_if_high(d))

uncertainty =
1 - confidence(d)

researchability =
expected probability the action obtains useful evidence

importance =
dimension weight

gross_information_value =
decision_sensitivity × uncertainty × researchability × importance

VOI =
gross_information_value - normalized_research_cost
```

Select highest positive VOI.

## Examples

If technical feasibility is already .95 with strong evidence but competition gap
is UNKNOWN, research competitors.

If demand is strong but willingness-to-pay is UNKNOWN, do not read five more papers.
Run a buyer/usage experiment.

If a cross-oracle correlation is strong but geographic mapping is uncertain,
verify mappings before generating products.

## Research actions can be different types

- API/source query
- repository review
- paper reproduction
- customer interview
- landing-page/fake-door experiment
- technical spike
- manual concierge test
- competitor pricing check

The market intelligence system should return the NEXT ACTION, not only a score.
