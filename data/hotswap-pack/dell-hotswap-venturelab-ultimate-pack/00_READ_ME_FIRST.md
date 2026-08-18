# Dell × HotSwap × VentureLab — Ultimate Runtime Pack

Target systems:
- `prx0r/dell`
- `prx0r/cuntgoblin`
- Hermes Agent
- LiteLLM
- optional OpenRouter / Nous provider routing beneath LiteLLM

Reviewed Dell head:
`ce10713f3a25999bea6120c5a7fa27754710713c`

Reviewed VentureLab state:
current factory modules include builders, certification, domain, ideas, intake,
market, research, scoring and vision.

## Mission

Build the missing runtime control layer:

```text
Factory Task
   ↓
TaskSpec / ModelPolicy
   ↓
HotSwap
   ↓
Dell truth + local outcome history + quota ledger
   ↓
economic route plan
   ↓
LiteLLM execution gateway
   ↓
Hermes worker
   ↓
objective task outcome
   ↓
HotSwap learner
   ↓
Dell observations / local policy state
```

The objective is NOT "always cheapest tokens".

The objective is:

> Minimize expected cost per successfully completed factory task subject to
> capability, quality, latency, safety, quota and evidence constraints.

Free routes are preferred when they are genuinely sufficient and capacity remains.

## Stack responsibilities

### Dell
Truth / economics / capabilities / freshness / offer activation / route evidence.

### HotSwap
Task-aware decision policy, free-capacity allocation, fallback plan, online learning.

### LiteLLM
Gateway, credentials, normalized provider I/O, per-key/team spend and budgets,
same-model deployment load balancing, transport retries, observability.

### Hermes
Agent loop, tools, session state, checkpoints, auxiliary tasks and native provider fallback.

### VentureLab
Produces typed tasks and objective completion/evaluation signals.

## Critical architectural rule

Do not make all four layers independently "smart route."

Exactly one layer owns each decision:

```text
MODEL / TASK selection      → HotSwap
economic/capability facts   → Dell
API transport / credentials → LiteLLM
same-model endpoint balance → LiteLLM / provider router
agent-loop continuity       → Hermes
task success label          → VentureLab evaluator
```

This avoids routing feedback loops and unreproducible failover.

## Pack contents

- final Dell peer review and required fixes
- task taxonomy and factory task annotations
- HotSwap route algorithm
- expected cost-per-success objective
- free-quota allocator
- quota reservation/reconciliation ledger
- contextual bandit learning
- conformal/verified cascade design
- failure classifier and circuit breakers
- LiteLLM integration
- Hermes integration
- OpenRouter/provider-routing integration
- account/setup opportunity queue
- outcome telemetry
- shadow evaluation and router training
- API/MCP specs
- SQL schema
- reference Python implementation
- deterministic tests
- implementation checkpoints
- final agent prompt

Reference implementation tests are included and executed when this pack was built.
