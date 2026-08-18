# P1 / P2 Debt

## P1

- UUIDv7/ULID IDs instead of second-resolution timestamp IDs.
- real Python package; remove `sys.path.insert` hacks.
- `pyproject.toml` + `uv.lock`.
- repository/data-access layer.
- timeout + cancellation for all agent/tool runs.
- leases and stale-worker recovery.
- idempotency for all writes/publication.
- attempt outcome separate from job outcome.
- immutable/versioned evidence.
- scoring-policy versions.
- schema versions on artifacts/events.
- explicit rate-limit/cache behavior.
- source failure distinct from empty result.
- build certificates.
- publication only from accepted certificate.

## P2 / later

Only introduce after demonstrated need:
- Postgres,
- Redis/distributed queue,
- LangGraph,
- Agent Lightning,
- neural router,
- vector DB,
- knowledge graph,
- Kubernetes.

Infrastructure is not evidence of product progress.
