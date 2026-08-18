# Acceptance Criteria

## AH-1 Registry
PASS:
- manifest schema works
- `cuntgoblin` ingested at pinned SHA
- build identity reproducible

## AH-2 Hermes runtime
PASS:
- manifest compiles to real Hermes plan
- HotSwap resolves model slots
- run artifacts collected

## AH-3 Controlled benchmark
PASS:
- >=2 architecture variants
- identical controlled model policy
- >=3 repeated tasks/trials
- cost/time/success logged

## AH-4 Recovery
PASS:
- >=3 fault modes
- detection/recovery/cascade metrics

## AH-5 Lineage
PASS:
- fork produces semantic mutations
- parent/child benchmark comparison

## AH-6 Resolver
PASS:
- real ArchitectureNeed routed
- system can REUSE
- system can FORK_OR_COMPOSE
- system can SYNTHESIZE on a deliberately unsupported need

## AH-7 Agent Factory
PASS:
- synthesize >=3 candidate architectures
- cheap simulation screens them
- real benchmark evaluates survivors
- Pareto archive retained

## AH-8 Promotion
PASS:
- single successful candidate is correctly NOT promoted
- promotion only occurs when strict evidence fixture/live evidence satisfies gates

## AH-9 External benchmark
PASS:
- at least one A2A/AgentBeats-compatible subject adapter smoke test

## AH-10 End-to-end
Opportunity → SolutionHypothesis(agentic) → ArchitectureNeed → Resolver →
ArchitectureBuild → HotSwap → Hermes → Benchmark → Registry/Outcome.
