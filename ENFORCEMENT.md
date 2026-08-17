# VentureLab Enforcement System

*Using hermes kanban features to enforce quality*

---

## How to Enforce Flow

### 1. Use `hermes kanban specify` to flesh out tasks

Before building, hermes must specify:
- What exactly to build
- What tests must pass
- What evidence must be produced
- What the certificate must contain

```bash
hermes kanban specify <task_id>
```

This forces hermes to think through the requirements before coding.

### 2. Use `hermes kanban decompose` to break into subtasks

Complex tasks get broken into:
- Build subtask
- Test subtask
- Verify subtask
- Certify subtask

```bash
hermes kanban decompose <task_id>
```

### 3. Use dependencies to enforce order

```bash
hermes kanban link <build_task> <test_task>
hermes kanban link <test_task> <verify_task>
hermes kanban link <verify_task> <certify_task>
```

Workers can't start testing until build is done.
Workers can't certify until tests pass.

### 4. Use skills to enforce patterns

Skills loaded by workers enforce:
- Code structure
- Test requirements
- Evidence logging
- Certificate format

### 5. Use certification to enforce completion

Every MVP must pass certification:
- Clean install
- Deterministic fixtures
- Schema valid
- Unit tests pass
- Integration tests
- Provenance
- Observations logged
- API contract
- MCP contract (if applicable)
- Documentation

---

## Enforcement Checklist

For every task, hermes must:

1. **Specify** — flesh out requirements
2. **Decompose** — break into subtasks
3. **Build** — write code
4. **Test** — run tests
5. **Verify** — check evidence
6. **Certify** — generate certificate
7. **Log** — write to data/runs/

Only then is the task "done".

---

## Quality Gates

### Gate 1: Specification
- [ ] Task has clear requirements
- [ ] Tests are defined
- [ ] Evidence is defined
- [ ] Certificate format is defined

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
- [ ] Clean install works
- [ ] Deterministic fixtures
- [ ] Schema valid
- [ ] API contract valid
- [ ] MCP contract valid (if applicable)
- [ ] Documentation exists
- [ ] Certificate generated

---

## Anti-Cheat

**"Nothing written in markdown counts as evidence."**

The only thing that counts is:
- Tests that actually pass
- API that actually responds
- Certificate that actually exists
- Evidence that actually has content hashes

---

*Enforcement system v1.0*
