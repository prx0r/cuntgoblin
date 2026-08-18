# Migration from current repo

This is not a rewrite.

## Preserve heavily

### `factory/hotswap/`
Keep routing math, quality floors, quotas, bandits, free-policy and fallback logic.
Extend route identity from model/provider to:
`executor + worker profile + model + provider + capability set`.

### `factory/market/market_algorithms.py`
Keep robust normalization, mandatory-unknown handling, source independence, opportunity score,
factory fit, genesis decision and approximate VOI.

### `factory/agenthub/`
Keep architecture-fit/reuse logic. Make AgentHub a factory plugin.

### Existing certification/tests
Migrate into the unified gate/certificate pipeline.

## Replace/retire

- `agent/run.py`: compatibility wrapper after OS is live.
- `factory/global_os/go.py`: replace broken runtime with `factory/os/`.
- handwritten MCP shim: replace after core state is stable.
- generic builder: call it TemplateInstantiator until it actually builds/tests/verifies.

## Rewrite doctrine

Current `AGENTS.md` hard-codes Hermes and one model. Replace with:
- Factory OS owns state/policy.
- Hermes is default reasoning executor.
- HotSwap chooses approved routes.
- deterministic code preferred when sufficient.
- workers cannot self-certify.
- source failure is not zero results.
- publish/deploy side effects require release gates.

Keep the current anti-cheat/content-addressing doctrine.
