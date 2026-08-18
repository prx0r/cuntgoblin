# Backend Optimization Notes

Optimize in this order:

1. avoid unnecessary LLM calls;
2. incremental recomputation;
3. batch source/API operations;
4. deterministic transforms outside LLM;
5. cache immutable/public projections;
6. database indexes/query plans;
7. profile serialization/network hot paths;
8. only then consider lower-level rewrites.

Database:
- normalize hot filter columns;
- JSONB for extensions;
- bulk observation inserts;
- cursor pagination;
- precomputed read projections where expensive.

API:
- ETags
- no N+1 evidence retrieval
- no unbounded list endpoints
- precompute common public aggregates.

LLM:
- cheap auxiliary routes
- artifact references instead of full transcript copies
- deterministic validators to terminate early.

Large artifacts never live inline in Postgres.
