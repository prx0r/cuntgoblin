# Market Intelligence REST/MCP

## REST

Recommended endpoints:

```text
GET  /v1/oracles
GET  /v1/entities
GET  /v1/topics
GET  /v1/topics/{id}
GET  /v1/signals
GET  /v1/trends/emerging
GET  /v1/trends/declining

GET  /v1/opportunities
GET  /v1/opportunities/{id}
POST /v1/opportunities/search

POST /v1/joins/search
POST /v1/research/next-action

POST /v1/factory/resolve
POST /v1/factory/propose

GET  /v1/evidence/{id}
GET  /v1/snapshots/{id}
```

## MCP tools

Keep tools goal-oriented:

1. `market_search`
2. `market_topic`
3. `market_trends`
4. `market_compare`
5. `market_signals`
6. `market_opportunities`
7. `market_join_search`
8. `market_evidence`
9. `market_next_research`
10. `factory_resolve`
11. `factory_propose`
12. `oracle_status`

## Example

```json
{
  "tool": "market_opportunities",
  "arguments": {
    "domain": "agent infrastructure",
    "min_confidence": 0.7,
    "max_crowdedness": 0.45
  }
}
```

## Critical agent semantics

Every result includes:

```json
{
  "as_of": "...",
  "method": "...",
  "method_version": "...",
  "coverage": 0.0,
  "confidence": 0.0,
  "source_families": [],
  "evidence_ids": [],
  "warnings": []
}
```

No score without evidence.
