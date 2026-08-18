# Chaos Tests Before Autonomous GO

Inject:
1. manager death during lease
2. Hermes worker death mid-task
3. DB connection restart
4. duplicate scheduler tick
5. source 429
6. malformed/empty source response
7. provider daily quota exhaustion
8. LiteLLM outage
9. Git push succeeds, deployment fails
10. deployment succeeds, smoke fails
11. artifact blob missing
12. artifact blob corrupt
13. schema upgrade while job queued
14. opportunity superseded while being researched
15. Dell price changes during task
16. two workers race for remaining free quota
17. verifier crashes
18. timezone/system clock error
19. stale/missing Kanban projection
20. Merkle recomputation mismatch

PASS:
- no duplicated durable side effect
- no lost logical job
- no false RELEASED
- no budget violation
- explicit recoverable/terminal state
- audit evidence exists.
