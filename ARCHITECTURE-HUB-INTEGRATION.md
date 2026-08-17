# Architecture Hub Integration

*How cuntgoblin fits into the agent architecture registry*

---

## Classification

```yaml
apiVersion: agentarchitectures.ai/v1
kind: AgentSystem

metadata:
  name: venturelab-factory
  slug: cuntgoblin
  version: 0.3.0

classification:
  runtime:
    - hermes

  family:
    - hierarchical-orchestrator
    - autonomous-factory

  patterns:
    - planner-worker
    - task-decomposition
    - parallel-workers
    - reviewer-gate
    - persistent-kanban
    - evidence-logging
    - certification

  domains:
    - software-development
    - product-generation
    - research
    - autonomous-operations
```

---

## What It Does

Turns researched product ideas into decomposed Hermes tasks, dispatches parallel coding workers, verifies outputs and certifies generated MVPs.

---

## Best For

```text
✓ long-running product development
✓ autonomous MVP generation
✓ research → architecture → code
✓ parallel build pipelines
✓ multi-project experimentation
```

## Avoid For

```text
✗ tiny coding tasks
✗ interactive low-latency work
✗ projects without objective acceptance tests
```

---

## Architecture

```text
IDEA POOL
    ↓
SCORING (deterministic, with evidence)
    ↓
SELECT (BUILD/WATCH/REJECT)
    ↓
HERMES SPECIFY
    ↓
HERMES DECOMPOSE
    ↓
KANBAN DAG
    ↓
┌──────────┼───────────┐
▼          ▼           ▼
worker    worker    worker
│          │           │
└──────────┼───────────┘
           ↓
         BUILD
           ↓
        REVIEW
           ↓
     CERTIFICATION
           ↓
    BUILT PRODUCT
```

---

## Maturity

```text
Hermes orchestration        WORKING
MVP builder                 WORKING
Certification               WORKING
Idea scoring                EXPERIMENTAL
Evolution                   CONCEPTUAL
Reinforcement               CONCEPTUAL
Cross-pollination           CONCEPTAL
```

---

## Current Evidence

```text
AgentSLA:
58/58 tests
12/12 certification
25 benchmark runs
```

---

## Known Weaknesses

```text
Idea scoring appears degraded
Evolution mechanics conceptual
Manifest stale
Docs fragmented
```

---

## Requirements

```text
Git
Python
Hermes
Filesystem access
Shell access
```

---

## Operations

```text
Install
Fork
Run
Resume
Inspect Tasks
Scale Workers
Benchmark
```

---

## Lineage

```text
Original
   │
   ├─ Cheap Factory
   ├─ Research Factory
   └─ Strict Verified Factory
```

---

*Architecture hub integration v1.0*
