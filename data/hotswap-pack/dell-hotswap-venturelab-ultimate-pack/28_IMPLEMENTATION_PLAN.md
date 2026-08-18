# Implementation Checkpoints

## CP-HS0 — Repair Dell release certificate
Fix all items in `01_DELL_FINAL_PEER_REVIEW.md`.
Re-run from clean checkout.

## CP-HS1 — TaskSpec
Add factory task taxonomy/schema/domain class.
Tag all existing LLM-consuming phases.

## CP-HS2 — LiteLLM gateway
Install/configure LiteLLM as centralized provider gateway.
Move/point configured provider keys through supported secret configuration.
Do not expose keys in repo.

## CP-HS3 — Dell candidate API
Expose clean candidate-route query with endpoint/evidence fields.
No final ranking required yet.

## CP-HS4 — HotSwap deterministic policy
Implement:
- hard gates
- exact task cost
- free-first
- Pareto prune
- static quality prior
- fallback plan

## CP-HS5 — Quota ledger
- published quota import
- reservations
- actual usage reconciliation
- reset/cooldown
- free scarcity

## CP-HS6 — Hermes runtime adapter
- per-task model override/profile
- generated fallbacks
- auxiliary task policies
- telemetry capture

## CP-HS7 — Failure classifier
- auth
- transient 429
- quota exhaustion
- server breaker
- context
- invalid response
- task failure

## CP-HS8 — Outcome learner
- task-cell posteriors
- evaluator integration
- cost-per-success reports

## CP-HS9 — Account opportunity queue
- Dell deal changes
- setup value/friction
- CLI/MCP
- activation verification

## CP-HS10 — Shadow benchmark
Compare against current fixed model on real factory traffic.

## CP-HS11 — Low-risk rollout
Market scouting/extraction/summarization/scaffolding.

## CP-HS12 — Coding rollout
Patch/build cells with deterministic tests.

## CP-HS13 — Bandit
Bounded Thompson exploration in routine cells.

## CP-HS14 — Verified cascade
Release/important tasks.

## CP-HS15 — Learned contextual router
Only if enough data and it beats deterministic policy.

## CP-HS16 — Dell feedback
Feed route measurements into Dell observation pipeline.

## CP-HS17 — Production certificate
HotSwap final external-agent/factory benchmark.
