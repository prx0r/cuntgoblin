# Model Pool Curation

LLMRouterBench indicates larger ensembles have diminishing returns and model recall
is a major routing problem.

Do not give HotSwap 300 models for every task.

## Curated pool per task cell

Keep 3–8 candidates:
- 1–3 free/near-free workhorses
- 1 cheap reliable paid route
- 1 strong escalation route
- optionally 1 exploratory candidate

## Diversity

Candidate pool should ideally vary:
- model family
- provider route
- cost tier
- capability profile

## Prune

Remove models that are:
- dominated on local outcomes + economics
- chronically unavailable
- stale
- no longer deal-competitive
- unsupported for required tools/context

## Re-entry

Dell change events can re-open a candidate when:
- price drops
- new free promo appears
- quota improves
- model version changes
- provider performance changes
