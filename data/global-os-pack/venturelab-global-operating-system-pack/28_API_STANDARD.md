# API Standard

## OpenAPI
Generate an OpenAPI 3.1-family description from actual routes.

CI:
- no undocumented route;
- no accepted-but-ignored filter;
- generated client smoke tests.

## Envelope

```json
{
  "data": {},
  "meta": {
    "as_of": "...",
    "dataset_version": "...",
    "request_id": "...",
    "method_version": "..."
  }
}
```

## Errors

```json
{
  "error": {
    "code": "CONTEXT_UNKNOWN",
    "message": "...",
    "details": {}
  }
}
```

## Pagination
Cursor based for high-volume/mutable collections with stable sort.

## Mutations
Support `Idempotency-Key` when duplicate effects matter.

## Time
RFC3339 UTC externally; `timestamptz` internally.

## Money
Decimal/numeric + explicit currency/unit. Never permanent binary float economics.

## Caching
Use ETag/Last-Modified/Cache-Control on public projections.
