# Final Shortlist — What to Actually Build

*2026-08-18T03:30:00Z · Based on GitHub, arXiv, and competitive analysis*

---

## Core Insight

Don't build one giant Oracle repo.

Build a collection of small, independently useful products that each emit Oracle-compatible observations.

---

## Tier S — Build These

| # | Product | Question | Gap |
|---|---------|----------|-----|
| 1 | **Knee** | What is the cheapest model that still passes task X? | Huge |
| 2 | **Toolloader** | Which 3-5 tools should this agent load right now? | Huge |
| 3 | **Agentpacks** | What complete agent architecture should I clone for X? | Huge |
| 4 | **EndpointTruth** | Is provider/model endpoint X actually good right now? | Large |
| 5 | **FallbackGraph** | What can transparently replace resource X? | Huge |
| 6 | **FreeCompute** | What usable free inference/compute capacity exists? | Medium-large |
| 7 | **AgentSLA** | What does one successful task actually cost? | Large |
| 8 | **StackGraph** | What agent components are actually used together? | Huge |

---

## Tier A — Build Next

| # | Product |
|---|---------|
| 9 | MCP Truth / Health API |
| 10 | Agentability API |
| 11 | Architecture Bench |
| 12 | API↔MCP↔CLI Equivalence Graph |
| 13 | Video Architecture Registry |
| 14 | Video Cost/Quality Oracle |
| 15 | Agent Adoption Census |

---

## The Progression

```text
MEASURE → EndpointTruth
OPTIMIZE → Knee
SELECT → Toolloader
COMPOSE → Agentpacks
```

---

## Key Partnerships

- **LiteLLM**: Use as gateway, not compete
- **OpenRouter**: Integrate, not replace
- **MCP**: Feed intelligence to gateways

---

## The 8 Repos to Build

1. `knee` — Cost/quality cliff API
2. `toolloader` — Dynamic MCP/API tool loader
3. `agentpacks` — Cloneable agent architectures
4. `endpointtruth` — Provider/model endpoint measurements
5. `fallbackgraph` — API/MCP/model equivalence + fallbacks
6. `freecompute` — Live free/cheap machine-capacity API
7. `agentsla` — Cost-per-success profiler
8. `stackgraph` — Agent ecosystem adoption/co-occurrence graph

---

## The Flywheel

```text
recommend → execute → observe → learn
```

Oracle recommends, LiteLLM executes, telemetry feeds back.

---

*Final shortlist based on competitive analysis.*
