# Verified Research / Documentation Notes — 2026-08-18

Primary/current sources used by this design:

## Hermes Cron
https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/cron.md

Provides one-shot/recurring scheduled tasks, isolated fresh sessions, gateway scheduling,
and scheduler locking. Used here as a trigger/delivery primitive rather than global truth.

## Hermes Kanban
https://github.com/nousresearch/hermes-agent/blob/main/website/docs/user-guide/features/kanban.md

Durable SQLite-backed multi-profile task collaboration. Used as a per-run projection.

## Temporal
https://docs.temporal.io/

Durable workflow execution infrastructure. Kept as an optional later adapter.

## PostgreSQL queue semantics
https://www.postgresql.org/docs/current/sql-select.html

`SKIP LOCKED` supports queue-like concurrent consumers.

## Paper2Agent
https://github.com/jmiao24/Paper2Agent
https://arxiv.org/abs/2509.06917

Paper/repository tutorials to executable tools/MCP/agent with tests/evaluation.

## Paper2Code
https://github.com/going-doer/paper2code
https://arxiv.org/abs/2504.17192

Multi-agent planning/analysis/code-generation pipeline for reconstructing paper implementations.

## LLMRouterBench
https://github.com/ynulihao/LLMRouterBench

Unified routing benchmark including Avengers/Avengers-Pro and other router families.

## Avengers / AvengersPro
https://github.com/ZhangYiqun018/Avengers
https://github.com/ZhangYiqun018/AvengersPro

Embedding/clustering and performance-efficiency routing families.

## MTRouter
https://github.com/ZhangYiqun018/MTRouter

Multi-turn/history-aware router research.

## VL-RouterBench
https://github.com/K1nght/VL-RouterBench

Vision-language routing benchmark used as a candidate VisionTruth lab adapter.

## Video-Bench
https://github.com/Video-Bench/Video-Bench

Video-generation evaluation research/tooling candidate.

## RFC 8785
https://www.rfc-editor.org/rfc/rfc8785.html

JSON Canonicalization Scheme.

## RFC 9162
https://www.rfc-editor.org/rfc/rfc9162.html

Certificate Transparency append-only Merkle design; domain-separated hashing informs
the ledger construction.

## MCP transport
https://modelcontextprotocol.io/specification/2025-06-18/basic/transports

stdio and Streamable HTTP; hosted HTTP transport security informs the MCP standard.

## Astro Islands
https://docs.astro.build/en/concepts/islands/

Static HTML with selective islands informs the frontend default.

## Google Search documentation
https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
https://developers.google.com/search/docs/appearance/structured-data/sd-policies

Used for sitemap/canonical/structured-data publishing rules.

## OCI
https://specs.opencontainers.org/image-spec/

Interoperable image/descriptor packaging and content addressing.
