# Final Stack Architecture

```text
                      VENTURELAB
                    task + evaluator
                          │
                          ▼
                      HOTSWAP
       task semantics / policy / learning / quota
          │                 │                 │
          ▼                 ▼                 ▼
        DELL          OUTCOME STORE      QUOTA LEDGER
 market truth         local success      reservations
 capabilities         per task cell      resets
 economics
          │
          └────────────┬─────────────────────┘
                       ▼
                 EXECUTION PLAN
        primary + fallbacks + constraints
                       │
                       ▼
                   LITELLM
      credentials / unified API / budgets /
      same-model deployment load balancing
                       │
                       ▼
        provider/OpenRouter routing if used
                       │
                       ▼
                     HERMES
                 full agent session
                       │
                       ▼
               objective evaluation
                       │
                       └──────────→ feedback
```

## Routing hierarchy

### HotSwap selects
- model family/model
- allowed economic tier
- exact model-route candidates
- fallback model order
- free quota allocation
- exploration vs exploitation

### LiteLLM selects
Within an allowed stable model group:
- API credential / deployment
- region replica
- provider transport adapter
- same-model healthy deployment

### OpenRouter may select
Underlying provider endpoint only when HotSwap deliberately delegates endpoint choice.

If Dell selected a specific OpenRouter provider route for measurement/reproducibility,
pass provider constraints to keep that choice stable.

### Hermes selects
Nothing economic by default.

Hermes receives an execution profile from HotSwap.
Its fallback chain is generated from HotSwap's plan rather than being an unrelated
static chain.

## Avoid double fallbacks

Bad:

```text
HotSwap fallback
× LiteLLM arbitrary model fallback
× OpenRouter model fallback
× Hermes unrelated fallback
```

Good:

```text
HotSwap = cross-model fallback policy
LiteLLM = same-model deployment failover
OpenRouter = provider endpoint failover where explicitly delegated
Hermes = mechanism that applies HotSwap fallback chain while preserving session
```
