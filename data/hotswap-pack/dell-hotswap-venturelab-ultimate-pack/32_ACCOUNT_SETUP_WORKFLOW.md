# Practical Provider Setup Workflow

## Discovery

Dell detects:
- new provider/deal
- free allowance/promo
- qualifying models
- activation requirements

## Value

HotSwap forecasts:
- which factory cells can use it
- expected calls until expiry/reset
- ECPS displacement
- setup friction

## Present to operator

Example:

```text
Provider X
Potential monthly saving: high
Eligible workload: source_extract, research_synthesis, coding_scaffold
Setup friction: 1/4
Action: add API key
Promo expiry: 21 days
Confidence: .88
```

## Configure

Use provider-supported setup path:
- LiteLLM deployment/key configuration
- Hermes model wizard only where Hermes needs direct auth

## Verify

Before ACTIVE:
- model list works
- one inference succeeds
- Dell model identity matches
- usage/spend telemetry captured
- quota behavior recorded where possible

## Retirement

Deal expiry:
- Dell emits change
- HotSwap stops new allocation
- remaining tasks re-resolve
- account may remain configured but deal-specific route loses priority
