# LiteLLM Integration

## Recommended deployment

Run LiteLLM Proxy as the credential/accounting gateway.

HotSwap stores NO raw API keys.

HotSwap references:
`litellm_deployment_id` / `credential_ref`.

## Stable model groups

Each configured economic route should map to a stable LiteLLM model/deployment group.

Example conceptual names:

```text
route/qwen-flash/openrouter
route/qwen-flash/direct
route/deepseek/direct
```

Do not place secrets in generated source-controlled config.

Use environment/secret references.

## Responsibilities

LiteLLM:
- provider adapters
- actual request usage
- cost accounting
- same-model replicas/keys
- request budgets/rate limits
- health-aware deployment choice
- admin UI

HotSwap:
- which model group should serve this task
- cross-model fallback order
- quota scarcity
- quality prediction

## Metadata on every request

Attach tags:
- `factory:<id>`
- `product:<id>`
- `task_kind:<kind>`
- `criticality:<level>`
- `run:<id>`
- `plan:<id>`

Use these for spend and success analysis.

## Retries

Avoid long retry churn.

HotSwap error policy should inform LiteLLM/Hermes retry count.

For a clearly exhausted quota:
zero same-deployment retries.

For short network/server transient:
small bounded retries may be appropriate.

## Dynamic routing

Do not rebuild LiteLLM's load balancer.

HotSwap outputs a model-group/fallback plan; LiteLLM executes the chosen group.

Cross-model model-group fallbacks should not be independently configured in LiteLLM
unless they are generated from the same HotSwap plan.
