# Factory Resolver

## Question

Given an Opportunity + SolutionHypothesis:

> Should an existing factory build this, should an existing factory be extended,
> or is a genuinely new factory justified?

## Existing-factory fit

For every active factory compute:

```text
FactoryFit =
.30 vision_fit
+ .20 market_scope_fit
+ .20 product_archetype_support
+ .15 component_reuse
+ .15 completion_contract_compatibility
```

Initial policy:

```text
max_fit >= .75 → USE_EXISTING
.60 <= max_fit < .75 → EXTEND_OR_FORK_EXISTING
max_fit < .60 → evaluate Factory Genesis
```

No new factory is considered while a suitable existing factory scores >= .75.

## Why

Factories have operational cost:
- templates
- tests
- docs
- maintainers
- source adapters
- evaluation
- deployment paths

Spawning one for every idea recreates monorepo chaos at a higher layer.
