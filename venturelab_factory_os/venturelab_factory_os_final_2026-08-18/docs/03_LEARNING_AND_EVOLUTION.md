# Learning and evolution

Replace fixed '+10 revenue / -5 abandonment' score deltas with outcome lineage.

```text
Observation
 -> Opportunity(version + frozen feature hash)
 -> Decision
 -> FactoryDefinition(version)
 -> FactoryRun
 -> WorkNodeRun*
 -> Artifact*
 -> Certificate
 -> Release
 -> OutcomeWindow*
```

Learn at four levels:

1. **Execution route** — which worker/model/provider succeeds for a task class?
2. **Team/formula** — which red-team/research/publish formula improves outcomes relative to cost?
3. **Factory** — which factory definitions produce useful certified outputs efficiently?
4. **Opportunity policy** — which decision-time features predict later value?

Start with running statistics, Beta success posteriors, cost quantiles, failure classes,
UCB exploration and historical replay. Train predictive models only after enough independent
outcomes exist.

Never mutate old decision features with future information.

Factory metrics stay separate:
- certification rate
- median/p90 total cost
- time to certified output
- release rate
- outcome success
- contribution margin
- active usage
- retention
- reliability
- maintenance cost
- data gain
- strategic utility
- confidence/sample count

Factory evolution is versioned clone/mutate/compare/promote/rollback/retire, never silent self-editing.
