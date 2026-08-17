---
name: factory-build
description: "Build MVPs from architecture specs. Write code, tests, docs following agentic-infra patterns."
version: 1.0.0
date: 2026-08-18
author: venturelab
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Build, MVP, Code]
    related_skills: [arch-spec, venture-report]
---

# Factory Build Skill

You build MVPs from architecture specs. Write code following agentic-infra patterns.

## When to use

When a kanban task says "Build [product] MVP" and points to specs/{product}/architecture.md

## What to build

For each product, create:

```
builds/{product}/
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

## Code patterns (from agentic-infra)

1. **Log everything**
```python
import json
from datetime import datetime, timezone

def log_run(step, result):
    record = {
        "step": step,
        "result": result,
        "ts": datetime.now(timezone.utc).isoformat()
    }
    with open("data/runs/agent-steps.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
```

2. **Content-address runs**
```python
import hashlib
def content_address(data):
    return hashlib.sha256(json.dumps(data).encode()).hexdigest()
```

3. **Deterministic gates**
```python
def gate_pass():
    # Run tests
    # Check outputs
    # Return True/False
    pass
```

## After building

1. Run tests
2. Log results to data/runs/
3. Mark kanban task complete
4. Request review if needed
