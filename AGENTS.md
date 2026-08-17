# AGENTS.md — VentureLab Factory

*How agents actually work here. Read this first.*

---

## THE ONE RULE

> **Nothing is "real" because a file exists. It is real only when an independently defined task,
> human-grounded gold, and a reproducible, LOGGED gate show it does what it claims.**

---

## GOOD AGENT BEHAVIOR

### 1. Use Hermes for Everything

```bash
# Research with hermes
hermes chat -q "Research this market trend"

# Browser with hermes
hermes chat -q "Find trend reports from Gartner/Forrester"

# Score with hermes
hermes chat -q "Score this idea against rubric: {rubric}"

# Build with hermes
hermes chat -q "Build MVP from spec: {spec}"
```

### 2. Background Processes

```bash
# Start long jobs as background
setsid nohup python3 script.py > output.log 2>&1 &

# Then continue working
# Check later with:
tail -f output.log
```

### 3. Kill by PID (never pkill)

```bash
# Find PID
ps aux | grep python | grep script.py

# Kill by PID
kill <PID>

# NEVER: pkill python
```

### 4. Monitor with timeout

```bash
# Only timeout when monitoring
timeout 300 tail -f output.log

# Never: sleep 300
```

### 5. Use Browser for Research

```bash
# Search trend reports
hermes chat -q "Find Gartner/Forrester reports on AI agents 2026"

# Search market data
hermes chat -q "Find market size data for LLM infrastructure"

# Search competitors
hermes chat -q "Find competitors in MCP space"
```

---

## BAD AGENT BEHAVIOR

### ❌ Creating empty Python files
```python
# BAD: This does nothing
def some_function():
    pass
```

### ❌ Saying "done" without doing work
```bash
# BAD: Just creating files and claiming done
echo "Done" > output.txt
```

### ❌ Using pkill
```bash
# BAD: Can kill other processes
pkill python
pkill node

# GOOD: Kill specific PID
kill $(ps aux | grep script.py | grep -v grep | awk '{print $2}')
```

### ❌ Sleeping to wait
```bash
# BAD: Wastes time
sleep 300

# GOOD: Monitor with timeout
timeout 300 tail -f output.log
```

### ❌ Creating synthetic data
```python
# BAD: Fake data
data = {"score": 0.8}  # No evidence

# GOOD: Real data with evidence
data = {"score": 0.8, "evidence": "GitHub search found 0 repos"}
```

### ❌ Saying "done" without testing
```bash
# BAD: Just creating files
touch file.txt
echo "Done"

# GOOD: Actually test
python3 -m pytest tests/
python3 -m app.certify
```

---

## HERMES WORKFLOW

### 1. Research Phase

```bash
# Start hermes in background
setsid nohup hermes chat -q "Research market trends for AI agents" > /tmp/research.log 2>&1 &

# Continue other work
# Check results later
tail -f /tmp/research.log
```

### 2. Scoring Phase

```bash
# Use hermes to score with rubric
hermes chat -q "Score this idea: {idea}. Rubric: {rubric}. Be granular."
```

### 3. Building Phase

```bash
# Use hermes to build from spec
hermes chat -q "Build MVP from spec: {spec}. Follow template: {template}"
```

### 4. Verification Phase

```bash
# Use hermes to verify
hermes chat -q "Verify this build passes all checks: {checks}"
```

---

## MARKET INTELLIGENCE

### How to Gather

```bash
# Use hermes to find trend reports
hermes chat -q "Find legitimate trend reports from Gartner/Forrester/McKinsey on AI agents 2026"

# Use hermes to find market data
hermes chat -q "Find market size data for LLM infrastructure 2026"

# Use hermes to find competitors
hermes chat -q "Find competitors in MCP space with their features"
```

### How to Structure

```yaml
topic: agent-infrastructure
window: 2026-Q3
signals:
  competition:
    active_projects: 38
    serious_projects: 9
  demand:
    github_growth: high
    enterprise_interest: medium-high
meta_tags: ["mcp", "agents", "2026"]
```

### How to Verify

- Link to source
- Content hash
- Timestamp
- Confidence score

---

## FILE STRUCTURE

```
venturelab/
├── AGENTS.md              # THIS FILE
├── factory/
│   ├── domain/            # Domain models
│   ├── scoring/           # Scoring engine
│   ├── market/            # Market intelligence
│   ├── ideas/             # Idea generation
│   └── vision/            # Vision boundaries
├── builds/                # Built MVPs
├── data/                  # Data and runs
├── ideas/                 # Research documents
├── specs/                 # Architecture specs
├── reports/               # Venture reports
└── reviews/               # Review logs
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
8. **Use hermes for all research and building**
9. **Background processes with nohup**
10. **Kill by PID, never pkill**

---

*Version 2.0*
