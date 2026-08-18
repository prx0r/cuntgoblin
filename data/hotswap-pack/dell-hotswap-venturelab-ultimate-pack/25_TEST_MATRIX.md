# HotSwap Test Matrix

## Dell boundary
D-01 output price unknown remains UNKNOWN
D-02 total budget actually enforced
D-03 route includes endpoint
D-04 confidence != coverage
D-05 no neutral-50 missing metrics
D-06 task quality independent of context length

## Task policy
T-01 every factory LLM task has TaskSpec
T-02 release gate disables exploration
T-03 evaluator missing => learning result UNKNOWN
T-04 hard capability UNKNOWN excluded

## Free routing
F-01 free sufficient route preferred
F-02 free insufficient route does not block paid success
F-03 exhausted free quota excluded
F-04 quota reservation concurrency safe
F-05 quota windows remain separate
F-06 unknown quota not promised
F-07 scarce free route gains shadow cost

## ECPS
E-01 failure escalation included
E-02 retry repair cost included when configured
E-03 paid route can beat failing free route
E-04 output price included
E-05 wall-time penalty optional/configured only

## Failure
R-01 auth no retry
R-02 transient 429 honors retry-after
R-03 quota exhaustion cooldown until reset
R-04 5xx opens exact route breaker
R-05 context triggers re-resolution
R-06 task evaluator failure updates bandit
R-07 safety refusal not bypassed by automatic fallback

## Learning
L-01 priors weakly derived from Dell
L-02 local outcomes dominate with samples
L-03 Thompson only low criticality
L-04 held-out routing beats simple baseline before promotion
L-05 propensity/exploration logged for online evaluation

## LiteLLM/Hermes
I-01 HotSwap never stores raw keys
I-02 LiteLLM receives plan tags
I-03 Hermes primary matches plan
I-04 Hermes fallback order matches plan
I-05 actual deployment reconciled
I-06 no unrelated static cross-model fallback

## Account opportunities
A-01 unconfigured attractive deal surfaces
A-02 expired deal suppressed
A-03 setup friction included
A-04 activation requires verification
