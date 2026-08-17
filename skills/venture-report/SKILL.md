---
name: venture-report
description: "Generate comprehensive venture reports from the VentureLab database."
version: 1.0.0
date: 2026-08-18
author: venturelab
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Venture, Research, Report]
    related_skills: [research, browser]
---

# Venture Report Skill

You generate venture reports. Read ideas from database, research with browser, write structured reports.

## Workflow

1. Read idea from `data/venturelab.db`
2. Search arxiv/github/web with browser
3. Write report to `reports/{product}/report.md`
4. Update database

## Report Template

```markdown
# {NAME} — {One Line}

## Thesis
{What and why}

## Product Spec
```http
POST /endpoint
```
Input/Output JSON

## Competitors
| Name | Does | Gap |

## arXiv Research
1. **Paper** (year) - finding

## GitHub
| Repo | Stars | Does |

## Why Cool
1. reason

## Monetization
1. method

## Path to Market
1. Week 1-2: phase

## Rating: X/10
Why: reasons
```

## Browser Searches
- arxiv: `https://arxiv.org/search/?query={q}`
- github: `https://github.com/search?q={q}&type=repositories`
- web: `https://www.google.com/search?q={q}+competitors`
