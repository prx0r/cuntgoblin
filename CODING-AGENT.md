# CODING-AGENT.md — Strict operational discipline for VentureLab

*How to actually work autonomously. Read this after AGENTS.md.*

---

## 1. THE #1 RULE — NEVER TIMEOUT, ALWAYS KEEP WORKING

### 1.1 The rule
**NEVER run a long job in the foreground.** Start it backgrounded with `setsid nohup`, write to a log, note the PID, then DO OTHER REAL WORK while it runs.

```
GOOD:  setsid nohup python3 /tmp/task.py > /tmp/task.log 2>&1 &  echo "PID $!"
       # ...do real work...
       tail /tmp/task.log     # check on it later

BAD:   python3 /tmp/task.py    # foreground — shell times out
BAD:   sleep 60; python3 ...      # idle waiting = wasted time
```

### 1.2 Kill by PID (never pkill)
```bash
# Find exact PID
ps -eo pid,etime,cmd | grep python | grep task

# Kill by PID
kill <PID>

# NEVER: pkill python
```

---

## 2. FILE CONVENTIONS

### Canonical locations (one per concern)

| Thing | Location | Rule |
|-------|----------|------|
| Current dev plan | `DEV-PLAN.md` | Always current, never create new |
| Current handover | `HANDSOVER-YYYY-MM-DD.md` | One current, old ones archived |
| Schema spec | `schemas/` | Source of truth for data contracts |
| Manifest | `MANIFEST.json` | Every file registered |
| Rules | `AGENTS.md` | Governing file |
| How to work | `CODING-AGENT.md` | This file |

### File lifecycle
```
NEW → CURRENT → STALE → LEGACY
```

- **Stale files**: Fix or mark `⚠️ STALE`
- **Legacy files**: Keep timestamped, don't delete
- **Orphaned files**: Wire it or register it

---

## 3. THE WORKFLOW

### Before any change
```bash
python3 check.py --status        # gate green?
python3 agent/ramwatch.py        # box safe?
```

### During work
```bash
# Start long jobs backgrounded
setsid nohup python3 script.py > /tmp/output.log 2>&1 &
echo "PID $!"

# Do real work while it runs
# Check log later with tail, not sleep
```

### After any change
```bash
python3 agent/run.py --step verify    # content-addressed audit
python3 agent/trace.py --recent       # logged?
python3 check.py --status             # gate still green?
```

---

## 4. EVIDENCE STANDARD

**"Nothing written in markdown counts as evidence."**

Evidence must be:
- Machine-produced from code
- Logged to `data/runs/`
- Content-addressed (SHA-256)
- Timestamped
- Reproducible

Every run record:
```json
{
  "run_id": "...",
  "step": "...",
  "gold_hash": "...",
  "code_hash": "...",
  "config_hash": "...",
  "out_hash": "...",
  "ts": "..."
}
```

---

## 5. VERIFICATION GATE

Before any claim:
```bash
python3 agent/verify.py --registry    # audit all runs
python3 agent/verify.py --all         # gate + trace check
```

Pillars:
1. Deterministic proof gate
2. Content-addressed run record
3. Golden audit
4. Anti-circularity

---

## 6. RAM/CPU BUDGET

Check before EVERY heavy job:
```bash
python3 agent/ramwatch.py
free -h | head -2 && uptime
```

- SAFE (avail ≥1GiB): OK to start
- CAUTION (avail <1GiB): light work only
- CRITICAL (avail <400MiB): STOP heavy work

---

## 7. CHECKPOINT SYSTEM

```bash
python3 agent/run.py --step checkpoints   # what's next
python3 agent/run.py --step report        # summary
```

Every checkpoint:
- Has a deterministic gate
- Is content-addressed
- Logs to trace

---

## 8. ANTI-CHEAT RULES

1. No synthetic data
2. No mock certificates
3. Content hashes required
4. Provenance required
5. "Nothing in markdown counts as evidence"
6. Always use mimo v2.5
7. Every score MUST have evidence
8. Use hermes for all research and building
9. Background processes with nohup
10. Kill by PID, never pkill

---

*Version 1.0*
