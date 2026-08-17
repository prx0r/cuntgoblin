# Documentation Index

*All documentation organized for agent consumption*

---

## Core Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| `AGENTS.md` | Rules for agents | First |
| `REFERENCE.md` | System reference | Before building |
| `STANDARD.md` | Schemas and standards | Before building |
| `ENFORCEMENT.md` | Quality gates | Before verifying |
| `SCORING-RUBRIC.md` | Anti-hallucination scoring | When scoring |
| `FACTORY.md` | Factory line overview | To understand flow |
| `FACTORY-FULL.md` | Full factory with agentic-infra | To build MVPs |

---

## Research Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| `ideas/*.md` | Research documents | When exploring ideas |
| `reviews/*.md` | Review logs | When reviewing |
| `specs/*/architecture.md` | Architecture specs | When building |
| `reports/*/report.md` | Venture reports | When evaluating |

---

## Evolution Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| `EVOLUTION.md` | Evolution mechanisms | When expanding |
| `EVOLUTIONARY-MECHANICS.md` | Detailed mechanics | When implementing |
| `COORDINATOR.md` | Sub-factory coordination | When scaling |
| `SUBFACTORY-VISIONS.md` | Vision options | When choosing vision |

---

## Patterns Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| `SNATCHABLE-PATTERNS.md` | Patterns from repos | When building |
| `binarythesis.md` | What actually works | When deciding |

---

## How to Use

### For New Agent

1. Read `AGENTS.md` first
2. Read `REFERENCE.md` for system overview
3. Read `STANDARD.md` for schemas
4. Check `kanban list` for current tasks
5. Start working on ready tasks

### For Building MVP

1. Read `specs/{product}/architecture.md`
2. Read `reports/{product}/report.md`
3. Follow `FACTORY-FULL.md` pattern
4. Use skills: `factory-build`, `factory-verify`, `certify`
5. Log to `data/runs/`

### For Reviewing

1. Read `reviews/log{N}.md` for previous reviews
2. Follow `SCORING-RUBRIC.md` for scoring
3. Check `CERTIFICATE.json` for validation
4. Log new review to `reviews/log{N+1}.md`

---

*Documentation index v1.0*
