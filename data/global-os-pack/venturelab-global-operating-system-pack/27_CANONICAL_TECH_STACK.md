# Canonical Performance Stack

Default golden path. A factory may deviate only with a recorded reason.

## Backend
- Python 3.12+
- FastAPI
- Pydantic/domain models
- PostgreSQL
- Alembic
- psycopg
- S3-compatible immutable artifact store

## Global workflow
V1: Postgres event/queue manager.
Later: optional Temporal adapter if operational triggers justify it.

## LLM gateway
LiteLLM.

## MCP
- stdio for local tools
- Streamable HTTP `/mcp` for hosted service
- hosted auth + Origin validation

REST and MCP call the same domain service.

## Frontend / SEO
Astro:
- static HTML first
- islands only for interaction
- pre-render factual public entity pages

CDN/edge cache:
Cloudflare-compatible deployment.

## Analytics
Parquet + zstd snapshots/changefiles for bulk analytical outputs.

## Containers
OCI.

## Rust
Only after profiling identifies a genuine CPU/latency hot path. Do not rewrite domain
logic for aesthetics.
