# API + MCP Rebuild

## REST should be thin

Suggested surface:

```text
GET  /health
GET  /status
POST /opportunities
GET  /opportunities/{id}
POST /jobs
GET  /jobs/{id}
POST /jobs/{id}/cancel
GET  /artifacts/{id}
GET  /factories
POST /factories/{type}/build
```

Long Hermes work never runs synchronously in an HTTP request. `POST /jobs` persists and returns `202`.

## MCP

Replace handwritten dispatch with official Python SDK.

As of the review date, official SDK v2 is current stable and its high-level server is `MCPServer`.

Expose small composable tools:
- `venturelab_search_opportunities`
- `venturelab_get_evidence`
- `venturelab_submit_job`
- `venturelab_get_job`
- `venturelab_list_factories`
- `venturelab_route_preview`

## Auth before public exposure

- API keys/bearer auth,
- per-key quota,
- read/build/publish separation,
- no arbitrary host filesystem paths,
- explicit connector/secret scopes.
