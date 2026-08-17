# Opportunity Scoring

## Do not reduce everything to one LLM number

Every opportunity carries a vector.

### Need
- pain severity
- frequency
- growth/urgency

### Gap
- current solution coverage
- incumbent strength
- fragmentation

### Feasibility
- technical readiness
- data availability
- buildability
- legal/operational feasibility

### Economics
- buyer clarity
- willingness-to-pay evidence
- marginal cost
- distribution access

### Moat
- compounding proprietary observation history
- learning effects
- workflow integration
- network effects where real

### Portfolio
- reusable components
- distribution reuse
- shared data
- strategic fit

### Risk
- market fragility
- regulation
- high capital requirements
- dependence on unstable upstreams

### Evidence
- coverage
- source independence
- recency
- confidence

## Core score v1

Use weighted geometric mean for positive dimensions so a catastrophic weakness matters.

```text
positive =
Need^.22
× Gap^.18
× Feasibility^.18
× Economics^.18
× Moat^.10
× Portfolio^.14

risk_factor = 1 - 0.55 * Risk

evidence_factor = 0.55 + 0.45 * EvidenceConfidence

OpportunityScore =
positive × risk_factor × evidence_factor
```

All inputs normalized to [0,1].

Do NOT set missing dimensions to 0.5.

If mandatory dimensions are UNKNOWN:
decision should generally be `RESEARCH`.

## Coverage

```text
coverage =
weighted known evidence mass / total required evidence mass
```

## Decision policy v1

```text
score >= .72
confidence >= .72
coverage >= .70
→ BUILD

score >= .62
and (confidence < .72 or coverage < .70)
→ RESEARCH

score .48-.72 with positive velocity/persistence
→ WATCH

score < .48 and confidence >= .70
→ REJECT

low score + low confidence
→ LOW_PRIORITY / RESEARCH only if VOI high
```

## Why BUILD is not an irreversible decision

BUILD means:
`run cheapest archetype-appropriate falsification experiment`.

It does not mean:
`create polished SaaS immediately`.
