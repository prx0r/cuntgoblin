# Router Research Lab

## LLMRouterBench

Clone/pin as a LAB benchmark/reference, not production core.

Use it for:
- standardized datasets/model outcomes;
- external routing algorithm comparison;
- cost/performance tradeoffs;
- adapter validation.

Store under a pinned third-party lab path.

## Avengers / AvengersPro

Do not clone separately by default because LLMRouterBench already provides their
routing baselines/adapters.

Clone upstream only for:
- exact algorithm reproduction;
- newer changes not represented in LLMRouterBench;
- implementation-specific ablations.

## Other router labs

Candidates:
- RouteLLM
- MTRouter for multi-turn/history-conditioned routing
- VL-RouterBench for VLM routing
- future execution-aware agent routers
- NVIDIA LLM/VLM routing reference implementations

## Promotion path

```text
external reproduction
-> canonical RouterAlgorithm adapter
-> historical factory replay
-> shadow routing
-> held-out live experiment
-> beats simpler baseline at fixed quality
-> production promotion
```

If it cannot beat deterministic HotSwap ECPS, do not ship it.
