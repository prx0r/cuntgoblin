---
name: venture-report
description: "Generate comprehensive venture reports from the VentureLab database. Research ideas, find competitors, analyze markets, and produce structured reports."
version: 1.0.0
date: 2026-08-18
author: venturelab
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Venture, Research, Report, Analysis]
    related_skills: [research, browser]
---

# Venture Report Skill

You generate comprehensive venture reports from the VentureLab database.

## The command map

| Command | When to use it |
|---|---|
| `python3 db.py init` | Initialize database |
| `python3 db.py report` | Generate summary report |
| Research an idea | Use browser to search arxiv/github/web |
| Generate report | Write structured report to reports/ folder |

## How to generate a report

### Step 1: Load the idea from database

```python
import sqlite3
import json

conn = sqlite3.connect('data/venturelab.db')
cur = conn.cursor()
cur.execute("SELECT * FROM ideas WHERE idea_id = ?", (idea_id,))
idea = dict(cur.fetchone())
```

### Step 2: Research using browser

Search for:
- arxiv papers related to the idea
- GitHub repos implementing similar things
- Existing products/companies
- Market size and trends

### Step 3: Write the report

Use this exact structure for every report:

```markdown
# {PRODUCT_NAME} — {One Line Description}

*Report generated: {timestamp}*

---

## Thesis

{What the product does and why it matters}

---

## Product Spec

### Core Endpoint

```http
POST /endpoint
```

Input:
```json
{request format}
```

Response:
```json
{response format}
```

---

## Current Competitors

| Competitor | What They Do | Gap |
|------------|--------------|-----|
| {name} | {description} | {what's missing} |

---

## arXiv Research

1. **{Paper Title}** ({year})
   - {Key finding}
   - {Product implication}

---

## GitHub Projects

| Project | Stars | What It Does |
|---------|-------|--------------|
| {owner/repo} | {stars} | {description} |

---

## Why It's Cool

1. {Reason 1}
2. {Reason 2}
3. {Reason 3}

---

## Monetization

1. {Method 1}
2. {Method 2}
3. {Method 3}

---

## Path to Market

1. **Week 1-2**: {Phase 1}
2. **Week 3-4**: {Phase 2}
3. **Month 2**: {Phase 3}
4. **Month 3**: {Phase 4}

---

## Final Rating

**Score: {X}/10**

**Why:**
- {Reason 1}
- {Reason 2}
- {Reason 3}

---

*End of report*
```

### Step 4: Save the report

Save to `reports/{product-name}/report.md`

### Step 5: Update database

```python
cur.execute("""
    INSERT INTO research (idea_id, github_results, arxiv_results, competitors)
    VALUES (?, ?, ?, ?)
""", (idea_id, json.dumps(github), json.dumps(arxiv), json.dumps(competitors)))
```

## Browser usage

Use browser to search:
- `https://arxiv.org/search/?query={query}` — search arxiv
- `https://github.com/search?q={query}&type=repositories` — search github
- `https://www.google.com/search?q={query}+competitors` — search web

## Report quality checklist

- [ ] Thesis is clear and compelling
- [ ] Product spec has working endpoints
- [ ] Competitors are real and analyzed
- [ ] arXiv papers are recent and relevant
- [ ] GitHub projects are real with star counts
- [ ] Monetization is specific
- [ ] Path to market is actionable
- [ ] Rating is justified

## Anti-cheat

**"Nothing written in markdown counts as evidence."**

All claims must be backed by:
- Real arxiv papers with URLs
- Real GitHub repos with star counts
- Real competitors with descriptions
- Machine-run experiments logged to database
