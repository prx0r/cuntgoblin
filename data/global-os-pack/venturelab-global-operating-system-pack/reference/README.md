# Reference Core

Pure reference implementation for:
- state transitions
- idempotency keys
- scheduling trigger IDs
- DAG readiness
- retry classification
- priority
- Merkle roots/inclusion proofs
- release saga

Important: the test serializer is deterministic but does NOT claim RFC8785 compliance.
Production must use a proper RFC8785 implementation.
