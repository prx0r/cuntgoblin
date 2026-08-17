# VentureLab Standard

*Standardized schemas, hermes features, clean autonomous pipeline*

---

## 1. Schemas (JSON)

### Idea Schema
```json
{
  "idea_id": "string",
  "idea": "string",
  "thesis": "string",
  "category": "string",
  "status": "seeded|researched|spec'd|building|done",
  "scores": {
    "novelty": "0-10",
    "research": "0-10",
    "feasibility": "0-10",
    "market_timing": "0-10",
    "overall": "0-10"
  },
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### Report Schema
```json
{
  "product": "string",
  "thesis": "string",
  "competitors": [{"name": "string", "does": "string", "gap": "string"}],
  "arxiv": [{"title": "string", "year": "int", "finding": "string"}],
  "github": [{"repo": "string", "stars": "int", "does": "string"}],
  "monetization": ["string"],
  "path_to_market": ["string"],
  "rating": "0-10",
  "rating_why": "string"
}
```

### Architecture Spec Schema
```json
{
  "product": "string",
  "system_overview": "string (ASCII diagram)",
  "components": [{"name": "string", "purpose": "string", "interface": "string"}],
  "data_model": "string (SQL/JSON)",
  "api_endpoints": [{"path": "string", "method": "string", "purpose": "string"}],
  "tech_stack": [{"layer": "string", "tech": "string", "why": "string"}],
  "costs": [{"component": "string", "monthly": "number"}],
  "risks": [{"risk": "string", "prob": "string", "impact": "string", "mitigation": "string"}],
  "phases": [{"name": "string", "duration": "string", "deliverables": ["string"]}]
}
```

---

## 2. Hermes Features to Use

### AGENTS.md
Project instructions loaded at startup. Defines:
- THE ONE RULE
- Anti-mess standard
- Workflow

### Skills
On-demand knowledge documents. Load when needed.
- factory-build
- factory-verify
- factory-spec
- venture-report
- arch-spec

### Kanban
Task management with:
- create: Create tasks
- specify: Flesh out details
- decompose: Break into subtasks
- dispatch: Spawn workers
- claim: Workers claim tasks
- complete: Mark done
- review: Request verification

### Checkpoints
Automatic snapshots before file changes. Rollback with /rollback.

### Memory
Persistent memory across sessions. Store:
- Ideas and scores
- Research findings
- Architecture decisions

### Cron
Schedule tasks to run automatically.

---

## 3. Pipeline

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
VERIFY (tests + review)
    ↓
DONE (MVP ready)
```

---

## 4. File Structure

```
venturelab/
├── AGENTS.md              # Project rules
├── FACTORY.md             # Factory line docs
├── STANDARD.md            # This file
├── data/
│   └── venturelab.db      # SQLite database
├── reports/
│   └── {product}/
│       └── report.md      # Venture report
├── specs/
│   └── {product}/
│       └── architecture.md # Technical spec
├── builds/
│   └── {product}/         # Built MVPs
├── skills/
│   ├── factory-build/     # Build skill
│   ├── factory-verify/    # Verify skill
│   ├── factory-spec/      # Spec skill
│   ├── venture-report/    # Report skill
│   └── arch-spec/         # Architecture spec skill
└── ideas/
    └── *.md               # Research documents
```

---

## 5. Quality Gates

Every build must pass:

1. **Code compiles** — no syntax errors
2. **Tests pass** — pytest returns 0
3. **Documentation exists** — README.md present
4. **Evidence logged** — data/runs/ has entries
5. **Content-addressed** — sha256 hashes computed
6. **Timestamped** — all files have dates

---

## 6. Anti-Cheat

> "Nothing written in markdown counts as evidence."

Evidence must be:
- Machine-produced from code
- Logged to data/runs/
- Content-addressed
- Reproducible

---

*Standard version 1.0*
