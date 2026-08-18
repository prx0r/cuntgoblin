# Frontier Research Worth Implementing

## WISERouter — arXiv:2607.23765

Constrained contextual bandit routing under a workload budget.

**Direct mapping:** HotSwap already has task budget/quota pressure. Add total workflow budget and context/outcome logging.

## BaRP — arXiv:2510.07429

Learns routing from bandit feedback—the deployed setting where only the selected route is observed—and supports a tunable cost/performance preference.

**Direct mapping:** persist selected route + context + verifier reward.

## Verified Multi-Agent Orchestration — arXiv:2603.11445

Plan → execute DAG in parallel → verify → replan with stop conditions.

**Direct mapping:** research and build DAGs. This is more useful than an unstructured “swarm.”

Implement:
- plan schema,
- dependencies,
- verifier gap list,
- bounded replan,
- budget/max-round stop.

## Procedural-memory / skill research

Useful because Hermes already has a skill system.

Implement:
- skill version,
- task/skill outcomes,
- frozen eval,
- promotion gate.

## Not P0

- RL agent training,
- neural routers,
- evolutionary agent populations,
- blockchain orchestration,
- general agent marketplace.

First accumulate reliable outcomes.
