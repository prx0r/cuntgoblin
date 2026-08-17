# VentureLab Reference Guide

*The complete system reference*

---

## System Overview

VentureLab is an autonomous venture research and MVP building system driven by hermes kanban.

```text
┌─────────────────────────────────────────────────────────┐
│                  VENTURELAB SYSTEM                       │
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   IDEAS     │    │  RESEARCH   │    │   REPORTS   │ │
│  │  (SQLite)   │───▶│  (browser)  │───▶│  (markdown) │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   SPECS     │    │  KANBAN     │    │   BUILDS    │ │
│  │ (markdown)  │───▶│  (hermes)   │───▶│   (code)    │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ CERTIFICATE │    │   EVIDENCE  │    │   DEPLOY    │ │
│  │   (JSON)    │◀───│  (hashes)   │◀───│  (docker)   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
IDEA (SQLite)
    ↓
RESEARCH (browser: arxiv/github/web)
    ↓
REPORT (reports/{product}/report.md)
    ↓
SPEC (specs/{product}/architecture.md)
    ↓
KANBAN (create → specify → decompose)
    ↓
DISPATCH (spawn workers)
    ↓
BUILD (workers write code)
    ↓
TEST (pytest)
    ↓
VERIFY (content hashes, provenance)
    ↓
CERTIFY (12-check certification)
    ↓
DEPLOY (docker, API live)
```

---

## Components

### 1. Ideas Database (SQLite)

Location: `data/venturelab.db`

Tables:
- ideas (153 ideas)
- research (193 research records)
- evaluations (scores)
- competitors (27 competitors)
- evidence (16 evidence points)

### 2. Reports

Location: `reports/{product}/report.md`

Structure:
- Thesis
- Product Spec
- Competitors
- arXiv Research
- GitHub Projects
- Why It's Cool
- Monetization
- Path to Market
- Rating

### 3. Architecture Specs

Location: `specs/{product}/architecture.md`

Structure:
- System Overview (ASCII diagram)
- Core Components
- Data Model
- API Endpoints
- Deployment Architecture
- Technology Stack
- Cost Estimates
- Risk Analysis
- Implementation Phases

### 4. Builds

Location: `builds/{product}/`

Structure:
```
builds/{product}/
├── app/
│   ├── api.py
│   ├── db.py
│   ├── models.py
│   └── mcp.py
├── tests/
├── data/
├── docs/
├── CERTIFICATE.json
├── MANIFEST.json
├── README.md
└── requirements.txt
```

### 5. Certificates

Location: `builds/{product}/CERTIFICATE.json`

Checks:
1. clean_install
2. schema_valid
3. unit_tests
4. api_contract
5. mcp_contract
6. content_hashes
7. provenance
8. observations_logged
9. documentation
10. deterministic_fixtures
11. integration_tests
12. adversarial_tests

---

## Hermes Integration

### Kanban Commands

```bash
# Create task
hermes kanban create "Build Product" --body "..." --assignee patala

# Specify task (hermes fleshes out)
hermes kanban specify <task_id>

# Decompose (hermes breaks into subtasks)
hermes kanban decompose <task_id>

# Dispatch workers
hermes kanban dispatch --max 5

# Worker claims task
hermes kanban claim <task_id>

# Complete task
hermes kanban complete <task_id> --result "..."

# Request review
hermes kanban request-review <task_id>
```

### Skills

- `factory-build` — Build MVPs from specs
- `factory-verify` — Verify builds pass tests
- `factory-spec` — Generate architecture specs
- `venture-report` — Generate venture reports
- `certify` — Certify MVPs pass production checks

---

## Content Addressing

Every artifact gets a SHA-256 hash:

```python
import hashlib
import json

def compute_hash(data):
    canonical = json.dumps(data, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()
```

Run records:
```json
{
  "run_id": "...",
  "gold_hash": "...",
  "code_hash": "...",
  "config_hash": "...",
  "out_hash": "..."
}
```

---

## Certification

Every MVP must pass 12 checks:

1. Clean install works
2. Schema valid
3. Unit tests pass
4. API contract valid
5. MCP contract valid
6. Content hashes computed
7. Provenance tracked
8. Observations logged
9. Documentation exists
10. Deterministic fixtures
11. Integration tests pass
12. Adversarial tests pass

Certificate format:
```json
{
  "product": "knee",
  "certificate": "PASS",
  "checks": {...}
}
```

---

## Anti-Cheat Rules

1. **No synthetic data** — Must use real measurements
2. **No mock certificates** — Must pass actual tests
3. **Content hashes required** — Every artifact must be hashed
4. **Provenance required** — Every observation must link to evidence
5. **"Nothing in markdown counts as evidence"**

---

*Reference guide v1.0*
