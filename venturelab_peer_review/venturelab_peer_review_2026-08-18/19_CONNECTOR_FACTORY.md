# Connector Factory

This is probably the cleanest second factory after API/Agent.

## Inputs
- OpenAPI,
- API docs,
- SDK,
- known HTTP contract/auth.

## Outputs
- typed Python client,
- optional TypeScript client,
- CLI,
- MCP server,
- auth/config,
- retries/rate limits/pagination,
- tests,
- capability manifest.

## Why it is strong

It is objectively verifiable and compounds the platform: each connector becomes a reusable tool for future factories.
