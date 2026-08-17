# Factory Genesis — Explicit Tipping Point

A factory should exist only when a repeated economic/search/build pattern justifies
its own reusable machinery.

## Hard gates

All required unless explicitly marked exceptional:

### G1 — Opportunity cluster
At least 3 distinct evidence-backed Opportunities sharing a coherent market thesis.

A single exceptional product is a project, not a factory.

### G2 — Existing factory misfit
Best existing `FactoryFit < .60`.

If `.60–.75`, extend/fork existing factory first.

### G3 — Repeatability
`repeatability >= .65`

Meaning the opportunities share enough of:
- customer/problem class
- source/data needs
- solution mechanism
- build/test pipeline
- distribution

### G4 — Shared infrastructure reuse
`shared_infra_reuse >= .60`

### G5 — Evidence
- cluster evidence confidence >= .70
- >= 3 independent source families
- no single source family provides >60% of critical evidence

### G6 — Opportunity mass
`opportunity_mass >= .65`

Suggested calculation:

```text
opportunity_mass =
weighted mean(top 3 opportunity scores)
× persistence
```

### G7 — Genesis economics
Expected engineering saved over first 3 products should exceed Factory Genesis cost.

```text
reuse_roi =
(cost_without_factory - cost_with_factory - genesis_cost)
/
max(genesis_cost, epsilon)
```

Require `reuse_roi >= .50` as starting prior.

## Genesis Score v1

After hard gates:

```text
FGS =
.25 opportunity_mass
+ .20 repeatability
+ .15 evidence_confidence
+ .15 strategic_coherence
+ .15 shared_infra_savings
+ .10 persistence
```

Decision:

```text
FGS >= .72 → SPAWN_CANDIDATE
.58 <= FGS < .72 → FACTORY_EXPERIMENT
FGS < .58 → NO_FACTORY
```

Again: initial priors. Backtest and version.

## FACTORY_EXPERIMENT

Before activating a borderline factory:

1. build one reference product;
2. extract shared template/patterns;
3. use template on a second product;
4. measure engineering reuse;
5. only promote if reuse and product quality improve.

## Factory Proposal output

```yaml
proposal_id: factory-proposal-...
opportunity_ids: [...]
vision: "..."
market_scope: [...]
allowed_product_archetypes: [...]
reference_product: ...
shared_patterns: [...]
source_oracles: [...]
genesis_score: .76
evidence: [...]
decision: SPAWN_CANDIDATE
```

## Factory activation certificate

Factory is ACTIVE only after:
- versioned vision exists
- opportunity cluster remains valid
- at least one certified reference product
- product completion contract exists
- score/evidence methods registered
- factory can say NO to an out-of-scope opportunity
