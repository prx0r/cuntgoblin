---
name: venturelab-agent
description: "Drive the VentureLab lab: discover ventures, research competitors, evaluate opportunities, generate hypotheses, produce reports — all gate-green."
version: 1.0.0
date: 2026-08-17
author: egoicAI
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Venture, Research, Lab, Orchestration, Verification]
    related_skills: [research, kanban]
---

# VentureLab Agent

You drive the VentureLab at `/root/venturelab`. **The ONE RULE: nothing is real unless it is a logged, content-addressed number on fixed gold, passed by a deterministic gate.**

## The command map

| Command | When to use it |
|---|---|
| `python3 agent/ramwatch.py` | BEFORE any heavy job — is the box SAFE? |
| `python3 check.py --status` | before + after ANY change — is the gate green? |
| `python3 agent/run.py --step discover --idea "..."` | log a new venture idea |
| `python3 agent/run.py --step research --idea-id VENT_XXX` | deep dive research on an idea |
| `python3 agent/run.py --step evaluate --idea-id VENT_XXX` | score and rank an idea |
| `python3 agent/run.py --step hypothesis` | generate hypotheses from evaluations |
| `python3 agent/run.py --step report` | produce venture brief report |
| `python3 agent/run.py --step watchdog` | run full autonomous cycle |
| `python3 agent/trace.py --recent` | see the recent runs |

## The standard workflow

```bash
cd /root/venturelab
python3 agent/ramwatch.py                 # 1. box safe?
python3 check.py --status                 # 2. gate green?
python3 agent/run.py --step discover --idea "API for X"  # 3. discover
python3 agent/run.py --step research --idea-id VENT_XXX  # 4. research
python3 agent/run.py --step evaluate --idea-id VENT_XXX  # 5. evaluate
python3 agent/run.py --step hypothesis    # 6. hypothesize
python3 agent/run.py --step report        # 7. report
python3 agent/trace.py --recent           # 8. logged?
python3 check.py --status                 # 9. gate still green?
```

## Kanban Integration

Use hermes kanban to track venture ideas:

```bash
hermes kanban add venturelab "Research VENT_001: API for X"
hermes kanban comment venturelab "Research complete: 5 papers, 3 repos"
hermes kanban done venturelab "VENT_001"
```

## Research Pipeline

### 1. DISCOVER
- Log a new venture idea
- Create kanban task
- Assign idea_id

### 2. RESEARCH
- Search arxiv for related papers
- Search github for related repos
- Check existing products
- Analyze competitors
- Map evidence

### 3. EVALUATE
- Score on weighted criteria:
  - Market timing (0.14)
  - Pain severity (0.14)
  - Willingness to pay (0.13)
  - API-native fit (0.10)
  - Competitive whitespace (0.10)
  - Defensibility (0.12)
  - MVP buildability (0.08)
  - Expansion potential (0.10)
  - Standards tailwinds (0.05)
  - Regulatory simplicity (0.04)
- Generate verdict: STRONG / MODERATE / WEAK / SKIP

### 4. HYPOTHESIS
- Identify patterns across ventures
- Generate testable hypotheses
- Propose experiments
- Track confidence levels

### 5. REPORT
- Summarize all evaluations
- Rank ventures by score
- Provide actionable recommendations
- Create presentation-ready outputs

## Data Sources

- **arxiv**: Academic papers and research
- **github**: Open source projects and implementations
- **competitors.jsonl**: 27 competitors/adjacent players
- **oss_projects.jsonl**: 15 relevant OSS projects
- **evidence.jsonl**: 16 evidence points
- **roadmap.jsonl**: MVP sequencing

## Anti-Cheat

**"Nothing written in markdown counts as evidence."**

All claims must be backed by:
- Machine-run experiments
- Logged to data/runs/
- Content-addressed records
- Reproducible scripts

## The honest rules
1. Never claim a result without a logged number on fixed gold.
2. Never pkill — kill by exact PID.
3. Never fabricate a result — a failed step is logged as failed.
4. Check ramwatch before + during heavy jobs.
