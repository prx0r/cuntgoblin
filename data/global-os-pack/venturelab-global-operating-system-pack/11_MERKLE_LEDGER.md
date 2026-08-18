# Merkle Ledger

Individual hashes prove artifact identity. A Merkle checkpoint commits the ordered
accepted event set for an epoch.

## Leaf

Canonical record:

```json
{
  "seq": 123,
  "event_id": "...",
  "artifact_digest": "sha256:...",
  "event_type": "...",
  "occurred_at": "..."
}
```

Canonicalize using RFC 8785 JCS.

Domain separation:
- leaf = SHA256(0x00 || canonical_leaf)
- node = SHA256(0x01 || left || right)

Leaves are ordered by global event sequence.

Odd unpaired nodes are promoted unchanged to the next level. This rule is part of the
VentureLab ledger version and must never be changed silently.

## Checkpoint

```json
{
  "tree_size": 10000,
  "first_seq": 1,
  "last_seq": 10000,
  "root": "sha256:...",
  "previous_checkpoint_id": "...",
  "created_at": "..."
}
```

Optional later: sign canonical checkpoint JSON with Ed25519.

A Merkle root proves commitment/integrity of included records, not the truth of the
external facts those records claim.
