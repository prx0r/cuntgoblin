# Schema Registry

Use JSON Schema Draft 2020-12 for durable JSON contracts.

Every durable object has:
- apiVersion
- kind
- stable object ID
- schema version

Example:

```json
{
  "apiVersion": "venturelab.ai/v1",
  "kind": "MarketObservation",
  "metadata": {
    "id": "obs_...",
    "schemaVersion": "1.2.0"
  }
}
```

## Versioning

Patch: semantic clarification/non-breaking fix.
Minor: backward-compatible optional fields.
Major: incompatible shape/meaning.

Never rewrite old historical artifacts merely because schema changes.
Use projection/reprocessing adapters.

Validate:
- ingress
- commit
- release bundle

Critical core objects reject ambiguous unknown fields.
Extension payloads may preserve future fields under `extensions`.
