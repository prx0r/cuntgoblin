# Reuse Existing Infrastructure

## LiteLLM — use it as the gateway

Do not rebuild:
- 100+ provider adapters
- OpenAI-compatible normalization
- virtual keys
- spend tracking
- team/project budgets
- rate limits
- load balancing
- gateway admin UI
- generic observability
- transport retries

HotSwap should identify requests with metadata/tags so LiteLLM accounting can attribute:

```text
factory
product
task_kind
criticality
run_id
route_plan_id
```

## Hermes — use it as the agent runtime

Hermes already provides:
- per-invocation `--model`
- `--provider`
- custom OpenAI-compatible endpoints
- credential pools
- fallback providers
- retry-before-fallback behavior
- separate auxiliary model slots
- per-auxiliary fallback chains
- session continuity

HotSwap therefore creates a Hermes execution profile rather than forking the agent loop.

## Dell — use it as economic truth

HotSwap should never scrape provider prices itself when Dell has a canonical fact.

HotSwap may maintain:
- transient live request outcomes;
- local quota reservations;
- local bandit state.

Those are runtime state, not replacements for Dell.

## LiteLLM UI vs new dashboard

Do NOT build a dashboard initially.

Use LiteLLM UI for:
- configured keys
- spend
- teams
- model deployments

HotSwap only needs:
- CLI/MCP for account opportunities;
- route decisions;
- quota status;
- factory savings.

Build a dedicated UI only after workflows prove it is necessary.
