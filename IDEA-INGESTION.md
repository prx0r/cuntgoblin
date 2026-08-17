# Idea Ingestion

*How ideas enter the factory*

---

## Sources

```text
your notes
ChatGPT conversations
GitHub trending/repos
arXiv
HN
Reddit
Product Hunt
API directories
MCP registries
new standards
new model releases
company launches
customer complaints
existing portfolio gaps
```

---

## Ingestion Format

Every idea comes in as:

```json
{
  "raw_text": "...",
  "source": "...",
  "observed_at": "...",
  "author": "...",
  "tags": []
}
```

---

## Normalization

Ideas are normalized into `IdeaCandidate`:

```python
idea = Idea(
    id="idea_...",
    title="...",
    description="...",
    source="...",
    status="inbox",
)
```

---

## Deduplication

Use:
- Embedding similarity
- LLM semantic adjudication
- Shared customer/problem/features

Keep provenance:

```text
idea_cluster
 ├ source idea A
 ├ source idea B
 └ source idea C
```

Do not delete duplicates — they indicate repeated signal.

---

## Clustering

Group similar ideas:

```text
MCP Health
MCP Truth
MCP Reliability
MCP Endpoint Monitor
```

becomes one cluster.

---

*Idea ingestion v1.0*
