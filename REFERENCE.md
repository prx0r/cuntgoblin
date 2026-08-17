# VentureLab Reference Guide

*The complete system reference*

---

## System Overview

VentureLab is an autonomous venture factory that converts raw ideas into researched, tested, versioned, deployed products.

```text
┌─────────────────────────────────────────────────────────┐
│                  VENTURELAB FACTORY                      │
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   IDEAS     │    │  RESEARCH   │    │   SCORING   │ │
│  │  (ingest)   │───▶│  (packets)  │───▶│ (evidence)  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │  BUILDERS   │    │ CERTIFICATION│    │  GITHUB     │ │
│  │  (MVP gen)  │───▶│  (12 checks)│───▶│ (publish)   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   DEPLOY    │    │  TELEMETRY  │    │ PORTFOLIO   │ │
│  │  (cloud)    │◀───│  (metrics)  │◀───│  (manage)   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
IDEA (text/JSON)
    ↓
INGEST (normalize, deduplicate)
    ↓
RESEARCH (GitHub, arxiv, market)
    ↓
SCORE (deterministic, with evidence)
    ↓
DECIDE (BUILD, WATCH, REJECT)
    ↓
BUILD (from template)
    ↓
TEST (unit, integration)
    ↓
CERTIFY (12-check suite)
    ↓
PUBLISH (GitHub)
    ↓
DEPLOY (cloud)
    ↓
MEASURE (metrics)
    ↓
ITERATE / KILL / SCALE
```

---

## Components

### 1. Domain Models

Location: `factory/domain/`

- `idea.py` — Idea with scores and evidence
- `product.py` — Product with metrics
- `research.py` — Research packet
- `score.py` — Scorecard with dimensions

### 2. Scoring Engine

Location: `factory/scoring/`

- `engine.py` — Deterministic scoring with evidence

Dimensions:
- novelty (0.15)
- research (0.10)
- feasibility (0.10)
- market_timing (0.10)
- pain_severity (0.15)
- willingness_to_pay (0.13)
- competition_gap (0.10)
- data_moat (0.10)
- strategic_fit (0.07)

### 3. Intake

Location: `factory/intake/`

- `ingester.py` — Idea ingestion from text/JSON

### 4. Research

Location: `factory/research/`

- `packet.py` — Research packet generation

### 5. Builders

Location: `factory/builders/`

- `builder.py` — MVP generation from templates

### 6. Certification

Location: `factory/certification/`

- `certifier.py` — 12-check certification suite

---

## Templates

Location: `templates/`

- `data-oracle/` — For Dell, MCPTruth, EndpointTruth
- `agent-tool/` — For Toolloader, Knee
- `benchmark/` — For AgentSLA
- `registry/` — For ArchOracle, Agentpacks
- `saas/` — For dashboards
- `library/` — For packages

---

## Schemas

Location: `schemas/`

- `idea.schema.json` — Idea structure
- `product.schema.json` — Product structure
- `certificate.schema.json` — Certificate structure

---

## Certification

Every MVP must pass 12 checks:

1. clean_bootstrap
2. schema_valid
3. unit_tests
4. integration_tests
5. api_contract
6. mcp_contract
7. security
8. adversarial
9. documentation
10. deterministic_fixtures
11. content_hashes
12. provenance

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

---

## Anti-Cheat Rules

1. **No synthetic data** — Must use real measurements
2. **No mock certificates** — Must pass actual tests
3. **Content hashes required** — Every artifact must be hashed
4. **Provenance required** — Every observation must link to evidence
5. **"Nothing in markdown counts as evidence"**
6. **Every score MUST have evidence**

---

*Reference guide v1.0*
