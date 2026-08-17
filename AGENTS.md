# AGENTS.md — VentureLab

*The rules for agents working on this project*

---

## THE ONE RULE

> **Nothing is "real" because a file exists. It is real only when an independently defined task,
> human-grounded gold, and a reproducible, LOGGED gate show it does what it claims.**

---

## THE ANTI-MESS STANDARD

### 1. Every build note is TIMESTAMPED
- Files must carry dates
- No undated notes

### 2. Every hermes run is TRACKED
- Log to data/runs/agent-steps.jsonl
- Content-addressed records

### 3. Every NUMBER is content-addressed
- sha256 hashes
- Nanopublications: {assertion, evidence, provenance}

### 4. Every doc is REGISTERED
- MANIFEST.json entries
- check.py must PASS

---

## WORKFLOW

1. Read this file first
2. Read STANDARD.md for schemas
3. Use skills: factory-build, factory-verify, factory-spec
4. Follow kanban: create → specify → decompose → dispatch → build → verify → done

---

## BOX RULES

- **Never `sleep` to wait** — background long jobs
- **Never `pkill`** — find exact PID, kill <PID>
- **RAM is scarcest resource** — check free -h before heavy jobs
- **Reuse, don't rebuild** — check what exists first

---

*Version 1.0*
