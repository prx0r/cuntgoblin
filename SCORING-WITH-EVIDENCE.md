# Scoring with Evidence

*Every score MUST have evidence. No guessing.*

---

## The Problem

Current scores are hallucinated:
```json
{
  "novelty": 9,
  "research": 8,
  "feasibility": 9,
  "market_timing": 9
}
```

No evidence attached. Where did these numbers come from?

---

## The Solution

Every score MUST have:

```json
{
  "factor": "novelty",
  "score": 8,
  "evidence": "GitHub search found 0 similar repos for 'brainwave MCP server'",
  "checked_at": "2026-08-18T09:00:00Z",
  "source": "https://github.com/search?q=brainwave+mcp+server"
}
```

---

## Scoring Process (Deterministic)

### Step 1: Check GitHub

```bash
# Search for similar repos
curl "https://api.github.com/search/repositories?q={query}&sort=stars"

# Count results
# If ≥5 repos exist → novelty ≤2
# If 2-4 repos → novelty 3-4
# If 1 repo → novelty 5-6
# If 0 repos → novelty 7-10
```

### Step 2: Check arxiv

```bash
# Search for papers
curl "http://export.arxiv.org/api/query?search_query=all:{query}"

# Count results
# If ≥6 papers → research ≥7
# If 3-5 papers → research 5-6
# If 1-2 papers → research 3-4
# If 0 papers → research 0-2
```

### Step 3: Check Market

```bash
# Search for market data
# Google: "{industry} market size 2026"
# Google: "{industry} growth rate"

# Score based on:
# Market size > $10B → market_timing 9-10
# Market size $1-10B → market_timing 7-8
# Market size $100M-1B → market_timing 5-6
# Market size < $100M → market_timing 0-4
```

### Step 4: Check Competitors

```bash
# Search for competitors
# Google: "{idea} competitors"
# Google: "{idea} alternatives"

# Score based on:
# 0 competitors → defensibility 9-10
# 1-2 competitors → defensibility 7-8
# 3-5 competitors → defensibility 5-6
# >5 competitors → defensibility 0-4
```

---

## Evidence Format

Every score record:

```json
{
  "idea_id": "VENT_BRAINWAVE_MCP",
  "factor": "novelty",
  "score": 10,
  "evidence": "GitHub search for 'brainwave mcp server' returned 0 results",
  "checked_at": "2026-08-18T09:00:00Z",
  "source": "https://github.com/search?q=brainwave+mcp+server",
  "method": "github_search"
}
```

---

## Anti-Hallucination Rules

1. **Never score without evidence**
2. **Always log the source**
3. **Always log the method**
4. **If uncertain, score lower**
5. **If evidence contradicts, lower score**

---

## Verification

Before accepting a score, verify:
- [ ] Evidence exists
- [ ] Source is valid
- [ ] Method is documented
- [ ] Timestamp is recent
- [ ] Score matches evidence

---

*Scoring with evidence v1.0*
