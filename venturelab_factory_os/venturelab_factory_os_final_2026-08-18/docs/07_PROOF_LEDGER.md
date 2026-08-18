# Proof ledger

Designed to detect:
- artifact mutation
- deletion/reordering of recorded work
- fake done claims without gates
- later rewriting of decision inputs
- unverifiable timestamps

Each ledger event stores:
- sequence
- UTC timestamp
- kind/subject
- canonical payload hash
- previous event hash
- event hash

Periodic epochs collect event hashes into RFC6962-style SHA-256 Merkle trees.

Store:
- epoch range
- leaf count
- Merkle root
- timestamp
- optional Ed25519 signature
- optional external RFC3161/Rekor anchor

A production certificate commits:
- artifact hashes
- source commit
- factory version
- WorkGraph
- gate-result hashes
- cost-summary hash
- ledger epoch/root
- verifier identity
- timestamp

This proves the recorded work history and bytes, not that an LLM's reasoning was philosophically correct.
