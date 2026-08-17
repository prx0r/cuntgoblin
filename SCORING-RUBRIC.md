# Scoring Rubric — Anti-Hallucination Reference

*Every score must be justified against this rubric. No guessing.*

---

## How Scoring Works

1. **Look up the factor** in this rubric
2. **Find the evidence** that matches
3. **Assign the score** based on evidence
4. **Log the evidence** in the score record

If you can't find evidence, the score is 0.

---

## Factor 1: Novelty (0-10)

| Score | Definition | Evidence Required |
|-------|------------|-------------------|
| 0-2 | Many competitors exist | ≥5 similar products on GitHub |
| 3-4 | Some competitors exist | 2-4 similar products |
| 5-6 | Few competitors | 1 similar product |
| 7-8 | Very few competitors | 0 similar products, but concept exists |
| 9-10 | No competitors | 0 similar products, concept is new |

**Check:** GitHub search for similar repos. If ≥5 exist, score ≤2.

---

## Factor 2: Research (0-10)

| Score | Definition | Evidence Required |
|-------|------------|-------------------|
| 0-2 | No research exists | 0 arxiv papers |
| 3-4 | Some research | 1-2 arxiv papers |
| 5-6 | Moderate research | 3-5 arxiv papers |
| 7-8 | Strong research | 6-10 arxiv papers |
| 9-10 | Extensive research | >10 arxiv papers |

**Check:** arxiv search. Count papers. If ≥6, score ≥7.

---

## Factor 3: Feasibility (0-10)

| Score | Definition | Evidence Required |
|-------|------------|-------------------|
| 0-2 | Extremely hard | Requires PhD + 10 engineers |
| 3-4 | Very hard | Requires 5+ engineers |
| 5-6 | Hard | Requires 2-3 engineers |
| 7-8 | Moderate | Requires 1 engineer |
| 9-10 | Easy | Can build in a weekend |

**Check:** Similar projects on GitHub. If others built it, score ≥7.

---

## Factor 4: Market Timing (0-10)

| Score | Definition | Evidence Required |
|-------|------------|-------------------|
| 0-2 | Too early | No market demand visible |
| 3-4 | Early | Some demand, but niche |
| 5-6 | Right time | Clear demand, growing |
| 7-8 | Perfect timing | Strong demand, growing fast |
| 9-10 | Urgent | Critical demand, must build now |

**Check:** Market size, growth rate, competitor activity.

---

## Factor 5: Monetization (0-10)

| Score | Definition | Evidence Required |
|-------|------------|-------------------|
| 0-2 | No clear path | Cannot identify buyers |
| 3-4 | Unclear path | Possible buyers, unclear pricing |
| 5-6 | Clear path | Known buyers, standard pricing |
| 7-8 | Strong path | Multiple buyers, proven pricing |
| 9-10 | Obvious path | Many buyers, premium pricing |

**Check:** Who pays for this? How much? How often?

---

## Factor 6: Defensibility (0-10)

| Score | Definition | Evidence Required |
|-------|------------|-------------------|
| 0-2 | No moat | Anyone can copy in a week |
| 3-4 | Weak moat | Takes a month to copy |
| 5-6 | Moderate moat | Takes 3 months to copy |
| 7-8 | Strong moat | Takes 6+ months to copy |
| 9-10 | Very strong moat | Data/ network effects compound |

**Check:** What's the moat? Data? Network effects? Switching costs?

---

## Factor 7: Futureproof (0-10)

| Score | Definition | Evidence Required |
|-------|------------|-------------------|
| 0-2 | Will be obsolete soon | Technology changing rapidly |
| 3-4 | May become obsolete | Some risk of obsolescence |
| 5-6 | Stable for 2-3 years | Reasonably stable |
| 7-8 | Stable for 5+ years | Very stable |
| 9-10 | Evergreen | Will always be needed |

**Check:** Technology trend. Is this getting more or less important?

---

## Scoring Process

For each factor:
1. **Look up** the factor in this rubric
2. **Find evidence** (GitHub repos, arxiv papers, market data)
3. **Assign score** based on evidence
4. **Log evidence** in the score record

Example:
```json
{
  "factor": "novelty",
  "score": 8,
  "evidence": "GitHub search found 0 similar repos for 'brainwave MCP server'",
  "checked_at": "2026-08-18T09:00:00Z"
}
```

---

## Anti-Hallucination Rules

1. **Never score without evidence**
2. **Always log what you checked**
3. **If uncertain, score lower**
4. **If evidence contradicts score, lower the score**

---

*Scoring rubric v1.0*
