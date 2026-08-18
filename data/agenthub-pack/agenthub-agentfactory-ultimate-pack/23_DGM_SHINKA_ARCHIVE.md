# Open-Ended Architecture Archive

DGM demonstrates the value of an archive/tree rather than replacing the current best.

ShinkaEvolve provides practical population/island/evaluation machinery.

## AgentHub archive

Each child stores:
- parent build(s)
- semantic mutations
- proposal agent/model
- benchmark evidence
- cost
- novelty
- retained/rejected status

## Why archive

A candidate that is worse today may contain:
- better recovery
- better memory
- lower cost
- a reusable pattern

and become a stepping stone later.

## Island idea

Maintain distinct niches:
- cheapest
- most reliable
- fastest
- recovery-strong
- coding-specialized
- research-specialized
- low-context

Cross-island recombination only after semantic compatibility checks.

## Shinka integration

Use ShinkaEvolve only for bounded modules where:
- candidate representation is executable;
- evaluator is automated;
- immutable regions are marked.

AgentHub's own archive remains canonical.
