# Frontier Routing Research → Design Decisions

## LLMRouterBench (ACL 2026)

Key implications:
- model complementarity is real;
- many sophisticated routers look similar under unified evaluation;
- several routers fail to beat a simple baseline;
- model recall remains a major gap;
- careful model-pool curation matters;
- larger ensembles have diminishing returns.

Design consequence:

**Start simple and measurable.**

HotSwap v1 should not begin with a giant neural router.

Use:
1. hard constraints;
2. curated Dell candidate pool;
3. local per-task success statistics;
4. expected cost per completion;
5. Pareto filtering.

Only add learned routing after the factory generates enough real outcomes.

Primary:
https://aclanthology.org/2026.findings-acl.1881/
Repo:
https://github.com/ynulihao/LLMRouterBench

## T2MO (2026)

Production coding routing should optimize **cost per completed task**, pricing failures,
retries and escalations explicitly.

Design consequence:

```text
not: cheapest $/token
but: expected total dollars to get task over its gate
```

Use task-category × difficulty cells and traffic-weighted savings.

Primary:
https://arxiv.org/abs/2608.08528

## Contextual-bandit routing

Adaptive routing under budget constraints and later bandit-feedback work model routing
under partial feedback—the production reality that only the selected route's outcome
is normally observed.

Design consequence:
- Beta/Thompson or contextual bandit after enough data;
- low-risk exploration;
- no expensive all-model labeling on every request.

Primary:
https://aclanthology.org/2025.findings-emnlp.1301/
https://arxiv.org/abs/2510.07429

## Conformal routing

Conformal routing adds a calibrated violation tolerance rather than relying on an
uncalibrated router confidence.

Design consequence:
release-critical tasks may use:
- cheap first attempt;
- accept only if a calibrated verifier/gate passes;
- otherwise escalate.

Primary:
https://aclanthology.org/2026.acl-srw.70/

## RouteLLM

Preference-trained strong-vs-weak routing is useful as an optional learned-router
baseline.

Do not make it the architectural core because VentureLab needs >2 models, quotas,
multiple providers and rapidly changing economics.

Repo:
https://github.com/lm-sys/RouteLLM

## RouteBalance / serving-aware routing

Research increasingly shows model choice and live serving conditions should not be
completely isolated.

HotSwap therefore combines:
- Dell quality/economic route facts;
- live breaker/latency state;
- LiteLLM deployment availability.

But keep the optimization decomposed operationally for reliability.

Primary:
https://arxiv.org/abs/2606.17949

## Practical synthesis

HotSwap should progress:

```text
Stage 0  deterministic curated policy
Stage 1  per-task-cell Bayesian outcomes
Stage 2  shadow learned classifier
Stage 3  contextual bandit
Stage 4  conformal/verified cascades
Stage 5  bounded policy evolution
```

Each stage must beat the simpler previous stage on held-out factory tasks.
