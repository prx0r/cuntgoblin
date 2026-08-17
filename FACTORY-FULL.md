# VentureLab Factory — Full Build System

*Hermes kanban + agentic-infra patterns*

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              VENTURELAB FACTORY                      │
│                                                      │
│  ┌─────────────┐                                    │
│  │   IDEAS     │ ← 153 ideas in SQLite              │
│  │   (153)     │                                    │
│  └──────┬──────┘                                    │
│         │                                            │
│         ▼                                            │
│  ┌─────────────┐                                    │
│  │  SPECIFY    │ ← hermes fleshes out details       │
│  │  (hermes)   │   creates architecture spec        │
│  └──────┬──────┘                                    │
│         │                                            │
│         ▼                                            │
│  ┌─────────────┐                                    │
│  │  DECOMPOSE  │ ← hermes breaks into               │
│  │  (hermes)   │   parallel subtasks                │
│  └──────┬──────┘                                    │
│         │                                            │
│         ▼                                            │
│  ┌─────────────┐                                    │
│  │  DISPATCH   │ ← hermes spawns workers            │
│  │  (kanban)   │                                    │
│  └──────┬──────┘                                    │
│         │                                            │
│         ▼                                            │
│  ┌─────────────┐                                    │
│  │   BUILD     │ ← workers write code               │
│  │  (workers)  │   following agentic-infra          │
│  └──────┬──────┘                                    │
│         │                                            │
│         ▼                                            │
│  ┌─────────────┐                                    │
│  │  VERIFY     │ ← hermes reviews                   │
│  │  (hermes)   │   runs tests                       │
│  └──────┬──────┘                                    │
│         │                                            │
│         ▼                                            │
│  ┌─────────────┐                                    │
│  │   DONE      │ ← MVP ready                        │
│  └─────────────┘                                    │
└─────────────────────────────────────────────────────┘
```

---

## Agentic-Infra Patterns to Adopt

From `/root/agentic-infra/`:

### 1. AGENTS.md
- THE ONE RULE: nothing is real without logged evidence
- DETERMINISTIC ANTI-MESS STANDARD
- Timestamped build notes
- Content-addressed records

### 2. agent/run.py
- Orchestrator for lab steps
- Logs to data/runs/agent-steps.jsonl
- Content-addressed run records

### 3. agent/trace.py
- Centralized run/experiment trace
- Query with: `python3 agent/trace.py --recent`

### 4. agent/audit.py
- Golden-file audit
- Recomputes on fixed gold
- Fails on mismatch

### 5. pipeline/run_recorder.py
- Content-addressed runs
- Nanopublication: {assertion, evidence, provenance}

### 6. pipeline/objective.py
- Weighted multi-axis scoring
- Pick next checkpoint by value/cost

### 7. pipeline/checkpoint.py
- Vision → checkpoint DAG
- Deterministic gates

---

## Factory Commands

### Create Board
```bash
hermes kanban boards create venturelab
hermes kanban boards switch venturelab
```

### Create Task
```bash
hermes kanban create "Build Knee MVP" \
  --body "Build cost-quality cliff API" \
  --assignee patala
```

### Specify Task (hermes fleshes out)
```bash
hermes kanban specify <task_id>
```

### Decompose (hermes breaks into subtasks)
```bash
hermes kanban decompose <task_id>
```

### Dispatch Workers
```bash
hermes kanban dispatch --max 5
```

### Workers Claim and Build
Workers automatically:
1. Claim ready tasks
2. Read specs from specs/{product}/
3. Write code following agentic-infra patterns
4. Log to data/runs/
5. Mark complete

### Verify
```bash
hermes kanban request-review <task_id>
```

---

## What Workers Build

For each product:

```
product/
├── AGENTS.md          # Rules for this product
├── app/
│   ├── __init__.py
│   ├── api.py         # FastAPI endpoints
│   ├── models.py      # Data models
│   ├── schemas.py     # Pydantic schemas
│   └── db.py          # Database operations
├── tests/
│   └── test_api.py    # Tests
├── data/
│   └── runs/          # Experiment logs
├── docs/
│   └── README.md      # Documentation
├── requirements.txt
└── Dockerfile
```

---

## Evidence Standard

From agentic-infra:

> "Nothing is real because a file exists. It is real only when an independently defined task,
> human-grounded gold, and a reproducible, LOGGED gate show it does what it claims."

Every build must:
- Log to data/runs/agent-steps.jsonl
- Content-address runs with sha256
- Pass deterministic gates
- Register in MANIFEST.json

---

## Current Status

```
Ideas: 153
Reports: 15
Architecture Specs: 4
Kanban Tasks: 15
Workers Running: 3
```

---

## Next Steps

1. Wait for architecture specs to complete
2. Specify MVP tasks
3. Decompose into subtasks
4. Dispatch workers
5. Build MVPs
6. Verify with tests
7. Ship

---

*Factory line driven by hermes kanban + agentic-infra*
