# Integration With Current VentureLab

Current VentureLab already has:
- market/
- ideas/
- vision/
- scoring/
- builders/
- certification/
- Hermes discipline
- HotSwap pack integration

Add:

```text
factory/
├── agenthub/
│   ├── registry.py
│   ├── resolver.py
│   ├── lineage.py
│   ├── patterns.py
│   ├── evidence.py
│   └── api.py
│
├── agentfactory/
│   ├── need.py
│   ├── synthesize.py
│   ├── compose.py
│   ├── mutate.py
│   ├── search.py
│   ├── promote.py
│   └── archive.py
│
├── benchmark/
│   ├── runner.py
│   ├── suites.py
│   ├── metrics.py
│   ├── simulator.py
│   ├── failures.py
│   ├── compare.py
│   └── certify.py
│
├── runtimes/
│   ├── base.py
│   ├── hermes.py
│   ├── a2a.py
│   └── docker.py
│
└── domain/
    ├── architecture.py
    ├── benchmark.py
    └── architecture_need.py

schemas/agenthub/
config/agenthub/
skills/agenthub-*
data/agenthub/
```

## Solution Lab integration

Add a solution mechanism:

`agentic_system`

If selected:
- derive ArchitectureNeed
- call AgentHub Resolver
- do not send directly to ordinary MVPBuilder.

## Factory Resolver integration

Factory Resolver answers:
"What product/factory should own the opportunity?"

AgentHub Resolver answers:
"What autonomous architecture should execute this agentic solution?"

These are distinct decisions.

## Outcome integration

Benchmark outcomes feed:
- AgentHub
- Architecture Factory
- HotSwap task-cell outcomes
- VentureLab Outcome Oracle

One run can therefore improve both model routing and architecture routing.
