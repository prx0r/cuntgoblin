# VentureLab Skills

Skills enable autonomous research and venture analysis.

## Available Skills

### 1. `venture-research`
Deep dive research on a venture idea.
- Check arxiv for related papers
- Check github for related repos
- Check for existing products
- Analyze competitors
- Identify gaps and opportunities

### 2. `venture-evaluate`
Evaluate a venture for monetization and usefulness.
- Score on weighted criteria
- Compare to competitors
- Assess market timing
- Estimate revenue potential
- Identify risks

### 3. `venture-hypothesis`
Generate hypotheses from evaluations.
- Identify patterns across ventures
- Generate testable hypotheses
- Propose experiments
- Track confidence levels

### 4. `venture-report`
Generate venture brief reports.
- Summarize all evaluations
- Rank ventures by score
- Provide actionable recommendations
- Create presentation-ready outputs

### 5. `venture-watchdog`
Run full autonomous research cycle.
- Discover new ideas
- Research existing landscape
- Evaluate opportunities
- Generate hypotheses
- Produce reports

## Usage

```bash
# Research a specific venture
python3 agent/run.py --step research --idea-id VENT RealityRouter

# Evaluate all ventures
python3 agent/run.py --step evaluate --idea-id VENT RealityRouter

# Generate hypotheses
python3 agent/run.py --step hypothesis

# Produce report
python3 agent/run.py --step report

# Run full autonomous cycle
python3 agent/run.py --step watchdog
```

## Data Sources

- **arxiv**: Academic papers and research
- **github**: Open source projects and implementations
- **competitors.jsonl**: 27 competitors/adjacent players
- **oss_projects.jsonl**: 15 relevant OSS projects
- **evidence.jsonl**: 16 evidence points
- **roadmap.jsonl**: MVP sequencing

## Scoring Criteria

| Criterion | Weight | Meaning |
|-----------|--------|---------|
| Market timing | 0.14 | How strongly 2026-27 agent adoption creates demand now |
| Pain severity | 0.14 | How costly or blocking the problem is |
| Willingness to pay | 0.13 | Likelihood of enterprise buyers paying |
| API-native fit | 0.10 | Can it be consumed as a narrow reusable machine dependency |
| Competitive whitespace | 0.10 | How crowded is the space |
| Defensibility | 0.12 | How hard to replicate |
| MVP buildability | 0.08 | How fast can we ship v1 |
| Expansion potential | 0.10 | How much can this grow |
| Standards tailwinds | 0.05 | Are standards moving in our favor |
| Regulatory simplicity | 0.04 | How complex is compliance |

## Anti-Cheat

**"Nothing written in markdown counts as evidence."**

All claims must be backed by:
- Machine-run experiments
- Logged to data/runs/
- Content-addressed records
- Reproducible scripts
