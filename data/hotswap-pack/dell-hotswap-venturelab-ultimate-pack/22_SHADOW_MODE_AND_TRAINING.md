# Shadow Mode / Training Ground

VentureLab is the training harness.

## Phase A — observe only

Run existing model policy.
HotSwap computes what it WOULD have chosen.

Record:
- chosen old route
- shadow route
- predicted ECPS

No execution change.

## Phase B — low-risk cells

Enable HotSwap on:
- extraction
- summarization
- scouting
- scaffolding

## Phase C — coding cells

Use deterministic tests as outcome labels.

## Phase D — important reasoning

Use independent evaluator and limited exploration.

## Phase E — release gates

No exploration.
Only enable after held-out evidence.

## Counterfactual evaluation

Do not claim shadow plan would have succeeded merely because its predicted score was high.

Counterfactual labels require:
- sampled paired runs;
- historical benchmark data;
- or statistical off-policy method with appropriate propensity logging.

## Router benchmark

Track:
- task completion
- total spend
- free completion %
- rework
- wall time
- escalation
- savings vs baseline
- quality regression

Primary KPI:
`cost per certified/successful task`.
