# MCP Standard

MCP and REST are thin adapters over the same service layer.

## Local
stdio.

## Hosted
Streamable HTTP:
`/mcp`

Hosted deployment:
- validate Origin;
- authenticate private/write access;
- avoid exposing local-only server indiscriminately.

## Tool names

Verb/object:
- `resolve_inference`
- `market_opportunities`
- `search_agent_systems`

## Tools / resources / prompts

Tools: parameterized actions/computation.
Resources: large/static methodology, schemas, snapshot metadata.
Prompts: optional user-facing workflows, not hidden business logic.

Decision outputs include:
- as_of
- method/version
- confidence
- coverage
- evidence IDs
- warnings

Pin protocol versions in integration tests.
