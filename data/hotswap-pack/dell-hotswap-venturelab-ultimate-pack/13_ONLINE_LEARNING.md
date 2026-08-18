# Online Learning

## Task cell

Start with categorical cells:

```text
task_kind
× difficulty
× criticality_class
× tools_required
× context_bin
× artifact_type
```

Do not over-split before enough samples exist.

## Prior

Use Dell task-domain quality evidence to initialize a weak Beta prior.

Example:

```text
prior_strength = 2 + 8 * evidence_confidence
alpha = 1 + prior_strength * p_prior
beta  = 1 + prior_strength * (1 - p_prior)
```

Weak enough for real factory outcomes to dominate.

## Posterior

Each objectively evaluated task:

```text
success:
  alpha += weight

failure:
  beta += weight
```

Use partial weight for noisy judge-based outcomes.

## Conservative routing

Important/release tasks use posterior lower confidence bound, not posterior mean.

Routine tasks may use posterior mean.

## Thompson exploration

For eligible low-critical tasks:

```text
sample p_i ~ Beta(alpha_i, beta_i)
```

then evaluate expected cost with sampled p.

Restrict exploration to a near-Pareto candidate set.

## Contextual upgrade

After enough history, train a contextual router from:
- task metadata
- prompt embeddings
- repository/build context
- route/model features

But it must beat:
- deterministic task-cell baseline
- cheapest-sufficient baseline
on held-out runs.

## Partial feedback

Only the chosen model outcome is normally observed.
This is exactly why online bandit methods are attractive.

Do not pay to label every request with every model.
