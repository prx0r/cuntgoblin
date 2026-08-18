# Artifact / Hash Standard

Every durable external input or important output becomes an Artifact.

Artifact types include:
- raw source payload
- canonical observation JSON
- code patch
- benchmark result
- certificate
- report
- release manifest
- generated schema
- container descriptor

Store DigestSet:
- raw SHA-256
- RFC 8785 canonical JSON SHA-256 when JSON
- normalized text hash where useful
- byte size
- media type

Large blobs live in a content-addressed object store.

Canonical blob path:
`sha256/ab/cd/<full-digest>`

Postgres stores metadata and references, not large payloads.
