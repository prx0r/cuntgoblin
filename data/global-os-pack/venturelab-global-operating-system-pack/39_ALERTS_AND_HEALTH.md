# Alerts / Health

Alert only on actionable events.

Critical:
- Merkle/integrity mismatch
- wrong release SHA
- budget overspend
- schema corruption
- secret leak
- persistent manager lease failure

High:
- no usable LLM route
- Dell stale beyond policy
- dead-letter spike
- production product unhealthy

Normal:
- valuable account/deal setup opportunity
- factory spawn candidate
- major opportunity
- benchmark winner

Do not notify on every failed source poll.

System health endpoint should expose:
manager, DB, artifact store, Dell, HotSwap, LiteLLM, Hermes, queue, budget, checkpoint.
