# Canonical AgentSystem Manifest

Example:

```yaml
apiVersion: agenthub.ai/v1
kind: AgentSystem

metadata:
  id: venturelab-hermes-factory
  name: VentureLab Hermes Factory
  version: 0.3.0
  source:
    repo: prx0r/cuntgoblin
    sha: <PINNED>

classification:
  runtime: hermes
  families:
    - hierarchical
    - planner-worker
    - persistent-factory
  system_types:
    - product-factory
    - research

topology:
  nodes:
    - id: coordinator
      role: planner
      model_slot: architecture_planner

    - id: worker_pool
      role: worker
      cardinality:
        min: 1
        max: 8
      model_slot: worker

    - id: certifier
      role: verifier
      independence_group: verification
      model_slot: verifier

  edges:
    - from: coordinator
      to: worker_pool
      kind: task_delegation
    - from: worker_pool
      to: certifier
      kind: artifact_review

model_slots:
  - id: worker
    task_kind: coding_patch
    quality_floor: .76
    free_policy: prefer

  - id: verifier
    task_kind: certification
    quality_floor: .88
    free_policy: neutral
    independent_family_preferred: true

state:
  task_graph: hermes_kanban
  artifacts: filesystem
  run_log: data/runs

operations:
  doctor: ...
  install: ...
  start: ...
  resume: ...
  status: ...
  stop: ...
  benchmark: ...

verification:
  tests: true
  independent_certifier: true
  content_hashing: true

maturity:
  overall: experimental
```

## Model-slot rule

Manifest specifies model REQUIREMENTS.

It does not generally pin actual models.

HotSwap resolves slots at run time.

Benchmark-control mode may freeze model assignments to isolate architectural effects.
