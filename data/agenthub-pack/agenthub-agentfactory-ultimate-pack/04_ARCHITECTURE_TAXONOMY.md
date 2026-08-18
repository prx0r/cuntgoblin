# Architecture Taxonomy

## Runtime / orchestrator

- Hermes
- LangGraph
- Letta
- Microsoft Agent Framework
- Google ADK
- AutoGen
- CrewAI
- custom
- A2A-composed

Runtime is not architecture family.

## Architecture families

- single-agent
- planner-worker
- supervisor-specialists
- worker-verifier
- hierarchical
- DAG
- sequential pipeline
- fan-out/fan-in
- debate/ensemble
- swarm
- persistent-factory
- dynamic-runtime-graph
- evolutionary
- market/auction allocation

## Structural patterns

- decomposition
- delegated planning
- independent review
- majority/ensemble
- reflection
- retry-repair
- fault isolation
- persistent task graph
- memory retrieval
- memory summarization
- context compaction
- tool specialization
- role specialization
- difficulty routing
- model-slot routing
- trusted checkpoint
- artifact certification

## System types

- coding
- research
- browser
- data
- security
- product-factory
- market-intelligence
- scientific
- general-autonomous
- workflow-automation

## Maturity is per-feature

Example:

```yaml
maturity:
  overall: experimental
  features:
    orchestration: working
    resume: working
    verifier: working
    evolution: conceptual
    external_benchmark: absent
```

Never infer "production" because a repo has many files.
