# Source Strategy

## Do not build "one trend score"

Preserve source families because each measures a different phenomenon.

### Behavioral usage
Strongest direct adoption proxies.
- OpenRouter token/request usage
- MCP marketplace use counts if available
- product/API telemetry

### Implementation adoption
- dependency usage
- package activity
- GitHub/ecosyste.ms activity
- Hugging Face repo/download activity

### Research
- OpenAlex
- arXiv for very recent technical papers

### Attention
- Cloudflare Radar
- Google Trends
- Hacker News
- news/search discussion

### Economic / social reality
- Unignorant
- World Bank
- Eurostat
- national statistics APIs
- trade/labour/education datasets

### Policy
- official government publications/datasets only as canonical policy evidence

## Evidence weighting

Do NOT directly use:
`market_score = 0.4 * GoogleTrends + 0.6 * GitHubStars`.

Instead:
1. normalize within each source/metric;
2. derive source-specific signals;
3. preserve the source-family label;
4. require independent families for important decisions;
5. combine only at Signal/Opportunity layer.

## Independence rule

Two signals are NOT independent merely because they came through two endpoints.

Examples:
- GitHub stars and ecosyste.ms GitHub stars share a parent source.
- OpenRouter app tokens and OpenRouter model tokens share a platform family.
- two newspaper articles quoting the same press release share an origin.

Track:
`source_family`
and optionally:
`origin_id`.

## PyTrends

`pytrends` is archived and is an unofficial pseudo-API. It may break when Google's
backend changes.

Policy:

```text
Google Trends official API available?
  YES → use official API
  NO  → optional pytrends adapter
          status = EXPERIMENTAL
          never sole evidence
          aggressive cache
          backoff
          raw response hash
          connector failure != zero interest
```

Never allow a pytrends failure to become a zero signal.

## arXiv

For broad topic counts and historical research velocity, prefer OpenAlex's structured
topic/keyword graph.

Use arXiv as:
- very-recent-paper discovery
- paper details
- frontier watch

Do not count a failed arXiv request as "no research".
