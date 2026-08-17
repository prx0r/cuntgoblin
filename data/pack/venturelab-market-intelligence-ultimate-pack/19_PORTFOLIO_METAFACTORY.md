# Portfolio MetaFactory

## Resource allocation

Factories compete for bounded:
- research calls
- build agent calls
- compute
- deployment slots
- maintenance budget

Do not allocate from "interestingness".

Use expected marginal portfolio value:

```text
EMPV =
OpportunityScore
× EvidenceConfidence
× FactoryExecutionProbability
× PortfolioSynergy
/
ExpectedTotalCost
```

## Diversification

Avoid all factories chasing the same correlated market.

Track:
- market topic overlap
- source overlap
- buyer overlap
- technical dependency overlap

Set a diversification penalty when portfolio concentration becomes extreme.

## Reallocation

Weekly/epoch review:

- new market evidence
- new opportunity mass
- factory completion rate
- actual product outcomes
- maintenance burden
- opportunity cost

Actions:
- INCREASE
- HOLD
- REDUCE
- PAUSE
- RETIRE

## Factory death

A factory should be retired when:
- opportunity cluster dissipates;
- no successful products after enough certified attempts;
- maintenance cost dominates;
- another factory subsumes it;
- market becomes structurally commoditized.

Keep lineage/history. Do not delete.
