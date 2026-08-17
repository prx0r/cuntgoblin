# AGENTS.md — VentureLab Factory

*The rules for agents working on this project*
*Model: mimo v2.5*

---

## THE ONE RULE

> **Nothing is "real" because a file exists. It is real only when an independently defined task,
> human-grounded gold, and a reproducible, LOGGED gate show it does what it claims.**

---

## MODEL

**Always use mimo v2.5 for all hermes calls.**

---

## HOW AN AGENT CONTROLS THIS SYSTEM

### 1. Read Context First

```bash
cat AGENTS.md          # Rules
cat REFERENCE.md       # System reference
cat ENFORCEMENT.md     # Quality gates
cat STANDARD.md        # Schemas
cat SCORING-RUBRIC.md  # Scoring rules
```

### 2. Check Kanban Status

```bash
hermes kanban list     # See all tasks
hermes kanban stats    # See summary
```

### 3. Create Tasks

```bash
hermes kanban create "Build Product X" \
  --body "Build from specs/product-x/architecture.md" \
  --assignee patala
```

### 4. Specify Tasks (hermes fleshes out)

```bash
hermes kanban specify <task_id>
```

### 5. Decompose (hermes breaks into subtasks)

```bash
hermes kanban decompose <task_id>
```

### 6. Dispatch Workers

```bash
hermes kanban dispatch --max 5
```

### 7. Workers Build

Workers:
1. Claim task
2. Read spec
3. Write code
4. Run tests
5. Log evidence
6. Mark complete

### 8. Verify

```bash
hermes kanban request-review <task_id>
```

### 9. Certify

```bash
cd builds/{product}
.venv/bin/python -m factory.certification.certifier
```

---

## WORKER WORKFLOW

When you claim a task:

1. **Read the spec** from `specs/{product}/architecture.md`
2. **Read the report** from `reports/{product}/report.md`
3. **Build the code** following the spec
4. **Write tests** that verify the spec
5. **Log evidence** to `data/runs/`
6. **Compute content hashes** for all artifacts
7. **Run certification** to verify everything works
8. **Mark task complete** with results

---

## QUALITY GATES

Every task must pass:

### Gate 1: Specification
- [ ] Task has clear requirements
- [ ] Tests are defined
- [ ] Evidence is defined

### Gate 2: Build
- [ ] Code follows patterns
- [ ] Code has docstrings
- [ ] Code handles errors

### Gate 3: Test
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Edge cases handled

### Gate 4: Verify
- [ ] Evidence logged
- [ ] Content hashes computed
- [ ] Provenance tracked

### Gate 5: Certify
- [ ] All 12 checks pass
- [ ] Certificate generated

---

## EVIDENCE STANDARD

**"Nothing written in markdown counts as evidence."**

Evidence must be:
- Machine-produced from code
- Logged to `data/runs/`
- Content-addressed (SHA-256)
- Timestamped
- Reproducible

---

## SCORING STANDARD

**Every score MUST have evidence attached.**

```json
{
  "factor": "novelty",
  "score": 8,
  "evidence": "GitHub search found 0 similar repos",
  "checked_at": "2026-08-18T09:00:00Z",
  "method": "github_search"
}
```

If you can't find evidence, the score is 0.

---

## FILE STRUCTURE

```
venturelab/
├── AGENTS.md              # This file
├── REFERENCE.md           # System reference
├── ENFORCEMENT.md         # Quality gates
├── STANDARD.md            # Schemas
├── SCORING-RUBRIC.md      # Scoring rules
├── RECIPES.md             # Step-by-step guides
├── SCHEMAS.md             # Data structures
├── DOCS-INDEX.md          # Documentation index
├── factory/               # Factory implementation
│   ├── domain/            # Domain models
│   ├── scoring/           # Scoring engine
│   ├── intake/            # Idea ingestion
│   ├── research/          # Research generation
│   ├── builders/          # MVP building
│   └── certification/     # Certification
├── templates/             # Product templates
├── schemas/               # JSON schemas
├── builds/                # Built MVPs
├── reports/               # Venture reports
├── specs/                 # Architecture specs
├── reviews/               # Review logs
├── ideas/                 # Research documents
└── skills/                # Hermes skills
```

---

## ANTI-CHEAT RULES

1. **No synthetic data** — Must use real measurements
2. **No mock certificates** — Must pass actual tests
3. **Content hashes required** — Every artifact must be hashed
4. **Provenance required** — Every observation must link to evidence
5. **"Nothing in markdown counts as evidence"**
6. **Always use mimo v2.5**
7. **Every score MUST have evidence**

---

*Version 1.0*
