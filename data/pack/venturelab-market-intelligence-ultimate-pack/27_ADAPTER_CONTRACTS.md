# Source Adapter Contract

Every adapter must implement conceptually:

```python
class OracleAdapter:
    manifest() -> OracleManifest
    health() -> SourceHealth
    discover(cursor=None) -> list[RawArtifactRef]
    fetch(ref) -> RawArtifact
    normalize(artifact) -> list[MarketObservation]
```

## RawArtifact

Must retain:
- exact response bytes or a content-addressed stored representation
- request URL/query
- response headers useful for freshness/rate limits
- fetched_at
- adapter version
- SHA-256
- source status

## SourceStatus

Use:
- OK
- DEGRADED
- RATE_LIMITED
- AUTH_REQUIRED
- UNAVAILABLE
- SCHEMA_CHANGED

No failure state maps to an observation value of zero.

## Caching

Cache keyed by:
`source + normalized request + adapter version`.

Use source-specific TTL.

## Rate limits

Rate limits are source metadata, not hard-coded across adapters.

On rate limit:
- persist RATE_LIMITED;
- respect retry headers if provided;
- do not spin/retry aggressively;
- continue other source work.

## Source versioning

Every observation records:
`adapter_version`.

If parser logic changes, historical observations remain reproducible.

## Snapshot-first for mutable public databases

If a source only exposes the latest revision (e.g. some statistics services),
snapshot raw responses used in decisions.

This gives VentureLab its own temporal history.
