# Test Matrix

## Identity
ID-01 source SHA changes build ID
ID-02 manifest changes build ID
ID-03 model-policy digest changes controlled build identity
ID-04 repo name alone never identifies benchmark build

## Resolver
RES-01 unknown hard capability excluded
RES-02 >=.78 reuse
RES-03 .62-.78 fork/compose
RES-04 <.62 synthesize experimental
RES-05 popularity never affects fit
RES-06 benchmark evidence outranks README claim

## Benchmark
BEN-01 same model policy in controlled comparison
BEN-02 actual model routes logged
BEN-03 fresh state each trial
BEN-04 repeated stochastic trials
BEN-05 cost includes all model attempts
BEN-06 evaluator isolated
BEN-07 no benchmark-gold access
BEN-08 simulation clearly separated from real result

## Failure
FAIL-01 injected failure location logged
FAIL-02 autonomous vs trusted-state detection distinguished
FAIL-03 recovery rate
FAIL-04 cascade radius
FAIL-05 blind retry cost visible

## Lineage
LIN-01 semantic mutations recorded
LIN-02 parent build immutable
LIN-03 child gets new build ID
LIN-04 Git diff alone insufficient

## Agent Factory
AF-01 one-off build does not auto-promote
AF-02 simple baseline included
AF-03 candidate graph validated
AF-04 immutable evaluation contracts
AF-05 Pareto archive retains tradeoffs
AF-06 promotion requires ablation
AF-07 promotion requires repeated tasks/runs

## HotSwap
HS-01 model slots resolved per role
HS-02 benchmark freeze mode disables dynamic model changes
HS-03 production mode logs HotSwap policy version
HS-04 verifier independence policy respected

## Runtime
RT-01 doctor
RT-02 clean install
RT-03 start/status/stop
RT-04 resume where declared
RT-05 A2A adapter fresh context
