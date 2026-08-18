# Reproducibility Contract

Each assessment stores:

- architecture build ID
- source SHA
- manifest hash
- runtime adapter/version
- dependency lock hash
- container digest if used
- benchmark suite/task version
- evaluator version
- model-policy mode
- actual model/route IDs
- tool versions
- random seeds
- environment hash
- artifacts
- stdout/stderr
- costs
- timestamps

Fresh state per assessment.

This matches AgentBeats's core principle that each assessment should run from a clean,
independent state.

## Repetition

Stochastic agent results require repeated trials.

Never publish one lucky run as architecture quality.
