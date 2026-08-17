# Recipes

*Step-by-step guides for common tasks*

---

## Recipe 1: Research an Idea

```bash
# 1. Load idea from database
python3 -c "
import sqlite3, json
conn = sqlite3.connect('data/venturelab.db')
cur = conn.cursor()
cur.execute('SELECT * FROM ideas WHERE idea_id = ?', ('VENT_XXX',))
idea = dict(cur.fetchone())
print(json.dumps(idea, indent=2))
"

# 2. Search GitHub
# Use browser or API to search for similar repos

# 3. Search arxiv
# Use browser or API to search for papers

# 4. Write report
# Save to reports/{product}/report.md

# 5. Update database
# Mark idea as researched
```

---

## Recipe 2: Generate Architecture Spec

```bash
# 1. Read report
cat reports/{product}/report.md

# 2. Research patterns
# Search arxiv/github for architecture patterns

# 3. Design system
# Create ASCII diagram
# Define components
# Define data model
# Define API endpoints

# 4. Write spec
# Save to specs/{product}/architecture.md

# 5. Update database
# Mark spec as complete
```

---

## Recipe 3: Build MVP

```bash
# 1. Create build directory
mkdir -p builds/{product}

# 2. Initialize project
cd builds/{product}
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Write code
# Follow architecture spec
# Use patterns from SNATCHABLE-PATTERNS.md

# 4. Write tests
# Create tests/test_*.py
# Test all endpoints

# 5. Run tests
.venv/bin/python -m pytest tests/ -v

# 6. Generate certificate
.venv/bin/python -m app.certify

# 7. Log evidence
# Save to data/runs/
```

---

## Recipe 4: Certify MVP

```bash
# 1. Clean install
cd builds/{product}
rm -rf data/*.db
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. Run tests
.venv/bin/python -m pytest tests/ -v

# 3. Check API
.venv/bin/python -c "from app.api import app; print(len(app.routes))"

# 4. Generate certificate
.venv/bin/python -m app.certify

# 5. Check certificate
cat data/certificate.json
```

---

## Recipe 5: Score an Idea

```bash
# 1. Read SCORING-RUBRIC.md
# Understand scoring criteria

# 2. Check GitHub for similar repos
# Count repos, stars, activity

# 3. Check arxiv for papers
# Count papers, recency

# 4. Check market size
# Research TAM, growth rate

# 5. Assign scores
# Use rubric to justify each score

# 6. Log scores
# Save to database with evidence
```

---

## Recipe 6: Switch Vision

```bash
# 1. Check performance plateau
# Has performance been flat for 3 months?

# 2. Check market shift
# Has the market changed significantly?

# 3. Compare ROI
# Is another vision higher ROI?

# 4. Make decision
# Stay, pivot, or switch

# 5. Update sub-factory
# Change vision in AGENTS.md
# Clear ideas database
# Start fresh
```

---

*Recipes v1.0*
