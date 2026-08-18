# Verified Primary Source Notes — 2026-08-18

## LLMRouterBench
https://aclanthology.org/2026.findings-acl.1881/
https://github.com/ynulihao/LLMRouterBench

400K+ instances, 21 datasets, 33 models, 10 representative routers.
Findings include model complementarity, diminishing returns from larger model pools and
a persistent Oracle gap from model-recall failures.

## Conformal LLM Routing
https://aclanthology.org/2026.acl-srw.70/

Calibrates a cheap-model safety gate with distribution-free violation guarantees under
the paper's assumptions.

## Adaptive Routing Under Budget Constraints
https://aclanthology.org/2025.findings-emnlp.1301/

Frames LLM routing as contextual bandit learning rather than full-information supervision.

## Bandit Feedback Routing
https://arxiv.org/abs/2510.07429

Contextual-bandit routing under chosen-model-only feedback with cost/performance preferences.

## T2MO
https://arxiv.org/abs/2608.08528

Production coding methodology centered on cost per completed task, including escalation.

## RouteLLM
https://arxiv.org/abs/2406.18665
https://github.com/lm-sys/RouteLLM

Strong/weak preference-data routing framework and OpenAI-compatible server.

## RouteBalance
https://arxiv.org/abs/2606.17949

Joint quality/cost/live-load routing research for heterogeneous serving.

## LiteLLM
https://docs.litellm.ai/
https://github.com/BerriAI/litellm

Unified OpenAI-format gateway for 100+ providers, with router/fallback, spend/budget,
virtual-key and load-balancing infrastructure.

## OpenRouter provider routing
https://openrouter.ai/docs/guides/routing/provider-selection
https://openrouter.ai/docs/guides/routing/model-fallbacks

Provider price/throughput/latency preferences, health-aware routing, hard max price,
fallbacks and parameter/provider constraints.

## Hermes Agent
https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/configuration.md
https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/fallback-providers.md
https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/provider-routing.md

Supports per-invocation model/provider selection, fallback provider chains,
credential pools, configurable retry count, auxiliary-model fallback chains and
provider-routing preferences.
