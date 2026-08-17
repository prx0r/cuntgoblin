# Cross-Oracle Join Lab

This is one of the strongest potential moats.

Goal:

> Discover economically meaningful combinations of signals that normally live
> in different institutional/data silos.

## Oracle Registry requirements

Every oracle advertises:

```yaml
domains: [...]
entities: [...]
metrics: [...]
dimensions:
  - geography_iso3
  - geography_subnational
  - sector_isic
  - occupation_isco
  - product_hs
  - technology_topic
temporal_granularity: monthly
source_families: [...]
```

## Canonical bridge dimensions

Start with:

- geography: ISO2/ISO3 + subnational mappings
- industry: ISIC/NACE/SIC
- occupation: ISCO/SOC
- product: HS codes
- organization IDs
- technology/topic IDs
- dates/windows

A join is legal only if:
- keys are explicitly compatible; OR
- a versioned bridge table exists.

## Rule templates

### SHORTAGE + SUPPORT

```text
labor_supply_contraction
AND demand_or_wage_pressure
AND training/subsidy/policy_support
```

Hypothesis:
new products reducing training/discovery/matching friction may be timely.

### IMPORT_DEPENDENCY + DOMESTIC_SUPPORT

```text
import_dependency ↑
AND supply disruption risk ↑
AND domestic industrial subsidy/support ↑
```

Possible solutions:
- supplier intelligence
- procurement search
- compliance/eligibility API
- sourcing tooling

### DEMAND + LOW DIGITAL SUPPLY

```text
demand signal ↑
AND small provider fragmentation ↑
AND low software penetration
```

Possible solutions:
- vertical SaaS
- lead routing
- marketplace infrastructure
- data/enrichment API

### RESEARCH + IMPLEMENTATION LAG

```text
research velocity ↑
AND package/repo adoption low
AND reproducible mechanism exists
```

Possible solutions:
- reference implementation
- API/MCP
- benchmark
- developer library

### REGULATION + TOOL GAP

```text
official deadline/event
AND large exposed population
AND low current tooling coverage
```

Possible solutions:
- compliance data/API
- workflow automation
- monitoring

### AGING SUPPLY + TRAINING DECLINE

```text
older workforce share ↑
AND new entrants/training ↓
AND wages/vacancies ↑
```

Possible solutions:
- recruitment/training discovery
- apprenticeship/subsidy tools
- workflow productivity tools

## Anti-spurious-correlation gates

Cross-data joins are dangerous if treated as causal.

Every JoinHypothesis must pass:

1. semantic path declared before scoring;
2. time windows overlap or have an explicitly allowed lag;
3. geography/sector/entity mappings are valid;
4. at least 2 independent source families support the pattern;
5. relation persists in >=2 windows, unless a primary-source event shock;
6. leave-one-source-out sensitivity does not collapse the whole signal;
7. plausible confounders listed;
8. output language says "association/opportunity hypothesis", never causality;
9. a targeted research action is generated to falsify the hypothesis;
10. historical replay/backtest is preferred before live promotion.

## Join novelty

Interesting joins are not random joins.

Score novelty from:
- source-domain distance;
- rarity of the combination in existing Opportunity Graph;
- absence of strong incumbent solution coverage.

Do NOT reward bizarre unrelated joins.

## Join score

```text
JoinScore =
semantic_plausibility^.25
× signal_strength^.20
× source_independence^.15
× temporal_alignment^.10
× persistence^.10
× solution_gap^.15
× novelty^.05
```

Hard minimum:
`semantic_plausibility >= .70`

This ensures novelty cannot compensate for nonsense.
