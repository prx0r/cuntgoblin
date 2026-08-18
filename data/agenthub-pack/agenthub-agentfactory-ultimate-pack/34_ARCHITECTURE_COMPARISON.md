# Architecture Comparison

## No universal score

Store metric vectors.

## Pareto dominance

A build A dominates B only when A is no worse on all selected objectives and strictly
better on at least one.

Common objective set:
- maximize task success lower bound
- minimize cost per success
- minimize wall time
- maximize recovery
- minimize architecture complexity

## Pairwise architecture effect

For controlled experiments:

```text
delta_success
delta_cost
delta_wall
delta_recovery
```

with paired tasks and confidence intervals.

## Promotion criterion

A structurally more complex candidate should not be promoted merely for a tiny noisy
improvement.

Require configured minimum practical effect or Pareto benefit.
