# Scoring Review

*Date: 2026-08-18T14:00:00Z*

---

## Issue Found

GitHub API is rate limited (403 error). This causes:
- All GitHub searches return 0 results
- Novelty scores are artificially high (10/10)
- Feasibility scores are artificially low (5/10)

## Impact

The scoring is **deterministic** but **not accurate** because:
1. GitHub API returns 0 results due to rate limiting
2. This makes novelty appear higher than it is
3. This makes feasibility appear lower than it is

## Evidence

```
GitHub API Response:
  Error: HTTP Error 403: rate limit exceeded
```

## Recommendation

1. Use authenticated GitHub API (with token)
2. Cache GitHub results
3. Add rate limit handling
4. Use alternative data sources

## Current Scores (with rate limiting)

| Idea | Novelty | Research | Feasibility | Overall |
|------|---------|----------|-------------|---------|
| RealityRouter | 10 | 2 | 5 | 0.64 |
| Proof-of-Work | 10 | 6 | 5 | 0.64 |
| Human Escalation | 3 | 6 | 8 | 0.48 |
| Delegated Authority | 10 | 6 | 5 | 0.64 |
| Work Receipt | 10 | 6 | 5 | 0.64 |
| AI Credits | 10 | 6 | 5 | 0.64 |
| SameModel | 10 | 6 | 5 | 0.64 |
| Search API | 3 | 6 | 8 | 0.51 |
| Sandbox Deals | 10 | 6 | 5 | 0.64 |
| Rate Limits | 10 | 6 | 5 | 0.64 |

## Verdict

**Scoring is deterministic but not accurate due to GitHub rate limiting.**

Need to:
1. Fix GitHub API access
2. Cache results
3. Add fallback data sources

---

*Scoring review v1.0*
