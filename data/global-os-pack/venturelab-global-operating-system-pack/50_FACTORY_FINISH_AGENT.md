# Finish Agent / Release Optimization

Before release:
- remove TODO/placeholders
- remove dead code
- dependency cleanup
- formatting/type/lint
- tests
- package/container build
- migration/bootstrap
- API pagination/filter contract
- MCP parity
- ETag/cache headers
- README clean-room
- security/secret scan
- license/changelog
- sitemap/canonical/structured data for sites
- generated MANIFEST
- release certificate

Performance acceptance is measured:
- p50/p95 endpoint latency
- no obvious N+1
- no unbounded list endpoints
- static pages remain static
- expensive network calls removed from hot request path where precomputation is possible.
