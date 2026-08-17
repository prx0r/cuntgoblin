---
name: factory-verify
description: "Verify builds pass tests and meet quality standards."
version: 1.0.0
date: 2026-08-18
author: venturelab
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Verify, Test, Quality]
    related_skills: [factory-build]
---

# Factory Verify Skill

You verify builds pass tests and meet quality standards.

## When to use

When a kanban task is in "review" status

## What to verify

1. **Code quality**
   - No syntax errors
   - Follows patterns
   - Has docstrings

2. **Tests pass**
   - Run pytest
   - Check coverage
   - Verify edge cases

3. **Documentation exists**
   - README.md
   - API docs
   - Setup instructions

4. **Evidence logged**
   - data/runs/ has entries
   - Content-addressed
   - Timestamped

## Verification commands

```bash
cd builds/{product}
python -m pytest tests/ -v
python -m py_compile app/*.py
```

## After verifying

If pass:
```bash
hermes kanban complete {task_id} --result "All tests pass"
```

If fail:
```bash
hermes kanban request-changes {task_id} "Tests failing: {error}"
```
