# Conformal / Verified Cascades

For tasks with an objective verifier, VentureLab can often do something stronger than
generic LLM confidence.

## Deterministic verification cascade

Example coding:

```text
cheap/free coder
    ↓
apply patch
    ↓
tests
 ┌──┴──┐
PASS  FAIL
 │      │
accept  escalate
```

This is better than asking the model whether it feels confident.

## Semantic tasks

Where deterministic verification is unavailable:
- use calibrated judge/evaluator;
- collect empirical calibration set;
- optionally implement conformal routing.

## Conformal concept

Choose a cheap route only when calibrated evidence keeps cheap-route failure among
accepted tasks below configured tolerance.

For `release_gate`, configure much tighter tolerance than `routine`.

## Two distinct gates

1. **router gate** — should cheap route be tried?
2. **output gate** — is this output accepted?

Both must be logged.

## Model-family independence

For high-stakes certification/review, prefer a verifier from a different model family
when cost permits.

This reduces correlated builder/verifier mistakes, though it is not a formal guarantee.
