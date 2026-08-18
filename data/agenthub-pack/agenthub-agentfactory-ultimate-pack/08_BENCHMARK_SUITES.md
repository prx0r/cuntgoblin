# Initial AgentHub Benchmark Suites

Build a small, high-signal suite before importing dozens of benchmarks.

## AH-CODE

Tasks:
- repository patch
- bug diagnosis
- multi-file feature
- refactor
- test repair
- release hardening

Evaluation:
- patch apply
- tests
- hidden tests where available
- repo-state invariants

Measures:
- success
- cost
- rework
- coordination
- verifier impact

## AH-RESEARCH

Tasks:
- source discovery
- evidence extraction
- conflicting-source reconciliation
- report generation
- falsification task

Evaluation:
- human-grounded gold where available
- source/evidence correctness
- unsupported-claim count
- retrieval coverage

## AH-FACTORY

Tasks derived from VentureLab:
- opportunity → spec
- spec → build
- build → certificate

This is the native proving ground for persistent factories.

## AH-ORCHESTRATION-SIM

Deterministic DAG simulation inspired by OrchBench:
- graph size
- parallelism
- context budgets
- information transfer
- worker budget

Measures:
- makespan
- retained critical information
- coordination cost

Use it for cheap pre-screening, not as a replacement for real execution.

## AH-RECOVERY

Controlled failure injection inspired by current orchestration benchmark research:
- tool failure
- worker crash
- ambiguous delegation
- stale intermediate artifact
- corrupted output
- latent semantic error

Measures:
- detection
- containment
- recovery
- cascade radius
- time to detection

## External adapters

Later support:
- AgentBeats green-agent suites via A2A
- GAIA-like tool-use
- CORE-Bench-like research reproduction
- framework-level suites such as MAFBench where licensing/integration permit
