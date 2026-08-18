# Day-One Runbook

1. Create Postgres DB and apply migrations.
2. Configure content-addressed artifact store.
3. Run Dell final certificate and regenerate its MANIFEST from current HEAD.
4. Start Dell API/MCP.
5. Configure provider credentials in LiteLLM using secret references.
6. Run HotSwap doctor; prove one free primary + paid fallback path.
7. Run Hermes doctor and one Kanban test board.
8. Start exactly one manager leader.
9. Run `venturelab go --dry-run`.
10. Start with a tiny paid budget and no publishing.
11. Allow only source refresh/signals first.
12. Create/verify a Merkle checkpoint.
13. Enable Opportunity/Solution flow.
14. Enable one product build.
15. Manually observe one release saga before enabling automatic publication.

Recommended first autonomous command:

```bash
venturelab go --max-workers 2 --daily-llm-budget-usd 0.50
```
