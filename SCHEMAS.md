# Data Schemas

*All data structures used in VentureLab*

---

## 1. Idea Schema

```json
{
  "idea_id": "string (unique)",
  "idea": "string (description)",
  "thesis": "string (why it matters)",
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

---

## 2. Report Schema

```json
{
  "product": "string",
  "thesis": "string",
  "competitors": [
    {
      "name": "string",
      "does": "string",
      "gap": "string"
    }
  ],
  "arxiv": [
    {
      "title": "string",
      "year": "int",
      "finding": "string"
    }
  ],
  "github": [
    {
      "repo": "string",
      "stars": "int",
      "does": "string"
    }
  ],
  "monetization": ["string"],
  "path_to_market": ["string"],
  "rating": "0-10",
  "rating_why": "string"
}
```

---

## 3. Architecture Spec Schema

```json
{
  "product": "string",
  "system_overview": "string (ASCII diagram)",
  "components": [
    {
      "name": "string",
      "purpose": "string",
      "interface": "string"
    }
  ],
  "data_model": "string (SQL/JSON)",
  "api_endpoints": [
    {
      "path": "string",
      "method": "string",
      "purpose": "string"
    }
  ],
  "tech_stack": [
    {
      "layer": "string",
      "tech": "string",
      "why": "string"
    }
  ],
  "costs": [
    {
      "component": "string",
      "monthly": "number"
    }
  ],
  "risks": [
    {
      "risk": "string",
      "prob": "string",
      "impact": "string",
      "mitigation": "string"
    }
  ],
  "phases": [
    {
      "name": "string",
      "duration": "string",
      "deliverables": ["string"]
    }
  ]
}
```

---

## 4. Certificate Schema

```json
{
  "schema": "venturelab/certificate/1",
  "product": "string",
  "certified_at": "ISO8601",
  "results": [
    {
      "test": "string",
      "status": "PASS|FAIL",
      "detail": "string"
    }
  ],
  "summary": {
    "passed": "int",
    "failed": "int"
  },
  "certificate": "PASS|CONDITIONAL PASS|FAIL"
}
```

---

## 5. Run Record Schema

```json
{
  "run_id": "string (unique)",
  "step": "string",
  "gold_hash": "string (SHA-256)",
  "code_hash": "string (SHA-256)",
  "config_hash": "string (SHA-256)",
  "out_hash": "string (SHA-256)",
  "metrics": {},
  "created_at": "ISO8601"
}
```

---

## 6. Task Schema (Kanban)

```json
{
  "task_id": "string (unique)",
  "title": "string",
  "body": "string",
  "status": "ready|running|review|done",
  "assignee": "string",
  "created_at": "ISO8601",
  "completed_at": "ISO8601"
}
```

---

## 7. Score Record Schema

```json
{
  "idea_id": "string",
  "factor": "string",
  "score": "0-10",
  "evidence": "string",
  "checked_at": "ISO8601"
}
```

---

*Schemas v1.0*
