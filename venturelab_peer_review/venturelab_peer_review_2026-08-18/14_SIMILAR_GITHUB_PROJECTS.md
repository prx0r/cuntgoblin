# Similar GitHub Projects — What to Borrow

## NousResearch/hermes-agent

Use its:
- durable Kanban,
- worker profiles,
- skills,
- cron,
- isolated workspaces,
- provider/model switching,
- programmatic execution surfaces.

Do not duplicate them in VentureLab.

## langchain-ai/langgraph

Borrow:
- checkpointed state,
- durable resume,
- deterministic/idempotent side effects,
- explicit graph transitions,
- human interrupts.

Adopt the framework only if the small kernel becomes hard to maintain.

## OpenHands/OpenHands

Borrow:
- isolated software-agent execution,
- clean runtime/SDK boundary,
- environment reproducibility,
- eval-centric coding-agent design.

## BerriAI/litellm

Use/borrow:
- provider normalization,
- retries/fallback plumbing,
- cost accounting,
- gateway behavior.

HotSwap should decide; a provider layer should execute.

## modelcontextprotocol/python-sdk

Use directly. Do not maintain a fake MCP protocol implementation.

## microsoft/agent-lightning

Later. Its separation between execution trajectories and optimization becomes useful after reliable rewards exist.

## Dependency gate

Adopt a dependency only if it removes a difficult, non-differentiating problem.
