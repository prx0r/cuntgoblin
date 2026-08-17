# Research Packet

*Standardized research output for each idea*

---

## Structure

```text
research/<idea-id>/
├── THESIS.md
├── MARKET.md
├── COMPETITORS.md
├── CUSTOMERS.md
├── TECHNICAL-FEASIBILITY.md
├── MONETIZATION.md
├── RISKS.md
├── SOURCES.json
└── SCORECARD.json
```

---

## THESIS.md

```markdown
# Thesis: [Idea Name]

## Customer
Who is the buyer?

## Pain
What problem does this solve?

## Wedge
Why is this the right approach?

## Evidence
- [Evidence 1]
- [Evidence 2]
```

---

## MARKET.md

```markdown
# Market Analysis

## Market Size
$X billion

## Growth Rate
Y% CAGR

## Segments
- Segment 1
- Segment 2

## Trends
- Trend 1
- Trend 2
```

---

## COMPETITORS.md

```markdown
# Competitors

| Name | What They Do | Gap |
|------|--------------|-----|
| Comp 1 | ... | ... |
| Comp 2 | ... | ... |
```

---

## SCORECARD.json

```json
{
  "idea_id": "...",
  "dimensions": [
    {
      "name": "pain",
      "score": 0.81,
      "confidence": 0.72,
      "evidence": ["..."]
    }
  ],
  "overall_score": 0.75,
  "overall_confidence": 0.68
}
```

---

*Research packet v1.0*
