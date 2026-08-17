# Opportunity Miners

An Opportunity is a market condition, not a product idea.

Each miner has:
- trigger
- required evidence
- output features
- disqualifiers
- possible solution families

## O1 — Pain × Growth × Undersupply

Trigger:

```text
pain >= .65
growth >= .55
solution_coverage <= .45
```

Evidence needs:
- problem signal
- market/adoption signal
- competitor/solution census

Possible solutions:
- API/data oracle
- automation
- workflow tool
- SaaS
- service
- marketplace

## O2 — Supply / Demand Gap

Examples:
- qualified workers falling while vacancies/wages rise
- API demand rising while reliable supply low
- compute demand rising while free/cheap routes fragmented

Features:

```text
demand_pressure
supply_contraction
price_or_wage_pressure
persistence
geographic_concentration
```

Trigger v1:

```text
demand_pressure >= .65
AND supply_response <= .40
AND persistence >= .50
```

## O3 — Policy Shock / Subsidy Unlock

Examples:
- new apprenticeship funding
- tax credit
- grant program
- procurement program
- regulatory deadline

Hard rule:
policy existence must be supported by a primary/official source.

Opportunity score should then combine:
- affected market size
- friction to access benefit
- existing tool coverage
- time window
- buyer clarity

Possible solutions:
- eligibility calculator
- discovery API
- compliance tooling
- marketplace
- lead-generation/data product
- workflow automation

## O4 — Research → Implementation Gap

Trigger:

```text
research_velocity >= .70
implementation_adoption <= .35
technical_readiness >= .60
```

This is useful for frontier ML/agent infrastructure.

Possible solutions:
- reference implementation
- API wrapper around legitimate mechanism
- benchmark
- agent system
- developer tool

## O5 — Price / Quality Arbitrage

Trigger when:
- incumbent cost or friction is high;
- a new technique/provider materially lowers cost;
- minimum quality/capability remains sufficient.

Do not score "cheap" alone.
Require:
`quality_sufficiency`.

Possible solutions:
- router
- broker
- optimizer
- migration tool
- reseller/data layer

## O6 — Fragmentation → Standardization

Trigger:

```text
fragmentation >= .65
pain >= .55
interoperability_need >= .60
dominant_standard_or_registry <= .55
```

Possible solutions:
- registry
- compatibility layer
- schema
- resolver
- benchmark
- adapter factory

## O7 — Geographic Divergence / Transfer

Look for:
- a proven product/behavior in geography A;
- similar structural problem in geography B;
- low local solution coverage.

Require comparability metadata.
Do not assume cultural or regulatory transferability.

## O8 — Portfolio Composition

Search existing products/patterns:

```text
product A's data
+
product B's capability
+
market opportunity C
```

Example:
Dell + AgentSLA → cost-per-success product.

## O9 — Cross-Oracle Join

Uses semantically meaningful rule templates over different oracle domains.

This is the high-upside discovery engine and is specified separately.

## O10 — Decline / Displacement

Falling incumbent usage + rising substitute adoption can create:
- migration tooling
- compatibility adapters
- archive/import/export
- training/content
- replacement infrastructure

Do not automatically build around a declining ecosystem; require residual buyer mass.
