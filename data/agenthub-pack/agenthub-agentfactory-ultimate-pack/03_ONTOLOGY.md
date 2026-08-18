# AgentHub Ontology

## AgentSystem

Stable conceptual architecture identity.

Example:
`venturelab-hermes-factory`

It is NOT one Git commit or one deployed instance.

## ArchitectureBuild

Immutable executable realization of an AgentSystem.

Identity includes:
- source SHA
- manifest hash
- runtime adapter/version
- dependency lock hash
- model policy
- tool policy
- container/image digest if used

Benchmark THIS object.

## Installation

A build installed on a specific host/environment.

## Run

One execution of an Installation/Build on one Task.

## ArchitecturePattern

Reusable structural primitive:
- planner-worker
- worker-verifier
- fan-out/fan-in
- persistent kanban
- independent certifier
- contextual memory
- retry-repair
- supervisor
- dynamic routing

## ArchitectureNeed

Requirements derived from a SolutionHypothesis.

## BenchmarkSuite

Versioned set of BenchmarkTasks + environment/evaluator policy.

## Assessment

One build evaluated against one suite/task configuration.

## Lineage

Parent build/system and semantic architecture mutation.

## ArchitectureCandidate

A proposed build not yet promoted.

## AgentFactoryProposal

The result of architecture synthesis/search.

## ArchitecturePromotion

Evidence-backed transition:

```text
EXPERIMENTAL_BUILD
→ VALIDATED_BUILD
→ REUSABLE_SYSTEM_CANDIDATE
→ VERIFIED_AGENT_SYSTEM
```
