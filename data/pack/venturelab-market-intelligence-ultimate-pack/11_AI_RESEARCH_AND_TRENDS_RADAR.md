# AI Research + Trends Radar

## Purpose

Continuously propose topics worth market research.

## Preferred stack

### Research backbone — OpenAlex
Use for:
- topic/keyword IDs
- works counts by window
- citation counts
- institution counts
- funder activity
- country diffusion

### Frontier freshness — arXiv
Use for:
- latest papers
- exact paper metadata
- very new terminology not yet well represented elsewhere

### Search attention
1. Google Trends official API when access exists.
2. PyTrends only as experimental fallback.

### Developer attention
Hacker News.

### Implementation
Hugging Face + ecosyste.ms + GitHub data.

### Behavioral usage
OpenRouter.

## Research velocity

For topic T:

```text
papers_short = works in recent 30/90d
papers_prior = comparable previous window

research_velocity =
percentile(log_growth(papers_short, papers_prior))

institution_breadth =
percentile(unique institutions recent)

cross_field_diffusion =
number of OpenAlex fields/subfields with meaningful recent work
```

High paper count alone is NOT emerging research.

## Research→market lag score

```text
RML =
research_velocity
× institution_breadth
× technical_reproducibility
× (1 - implementation_adoption)
```

This directly feeds the Research→Implementation opportunity miner.

## PyTrends connector contract

When used:
- max 5 terms per comparison group;
- anchor comparisons with a stable reference term when possible;
- cache raw payloads;
- retry with exponential backoff;
- detect HTTP/rate-limit errors;
- NEVER return zero on connector error;
- store `source_status=DEGRADED` when backend changes;
- official API supersedes pytrends automatically.

## Topic-expansion loop

For each seed:
1. exact normalized topic;
2. aliases/synonyms;
3. related OpenAlex keywords/topics;
4. HN co-mentions;
5. Hugging Face tags/models;
6. MCP/package/repo co-occurrence;
7. only retain expansions with evidence.

This avoids an LLM inventing arbitrary market categories.
