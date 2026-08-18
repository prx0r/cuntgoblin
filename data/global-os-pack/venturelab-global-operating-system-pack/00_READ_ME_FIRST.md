# VentureLab Global Operating System — Ultimate Run / Manage / Expand Pack

Targets:
- prx0r/cuntgoblin
- prx0r/dell
- Unignorant / Oracle providers
- HotSwap
- AgentHub / Agent Factory
- Hermes Agent
- LiteLLM

Reviewed VentureLab head:
`2fcc6abcce78d4fac8c516e62069827d0e8cf931`

Dell functional hardening observed:
`f3927b261b3f6e52a61ae4723a9b92774d393eb9`

Important Dell caveat:
the default-branch `MANIFEST.json` observed during this review still describes an
older SHA and `mutation_kill_rate: 0.9`. The pack therefore makes generated
manifest freshness a release gate.

## Purpose

Turn the accumulated architecture into a system that can actually be left running.

This pack specifies:
- what `venturelab go` means;
- global scheduling;
- queues, leases and idempotency;
- where Hermes Kanban and Cron fit;
- budgets and concurrency;
- content-addressed artifacts;
- schema validation;
- Merkle checkpoints;
- GitHub/deployment release transactions;
- Paper → Code → MCP → AgentHub workflows;
- router research labs and HotSwap promotion;
- Dell go-to-market and modality expansion;
- canonical product/API/MCP/SEO/backend conventions;
- chaos tests and failure recovery.

## Core decision

Postgres is the canonical operational ledger.

Hermes Kanban is a per-run collaboration projection.
Hermes Cron may trigger workflows, but it is not the global schedule database.
HotSwap is the sole cross-model selector.
LiteLLM/provider routers handle credentials/transport/same-model deployment failover.
Hermes executes agent sessions.

## Do not press GO on the old architecture

Implement CP-G0 through CP-G7 first.

Without them, the system can duplicate work, overspend, race free quotas, fork state
between Kanban/files/DB, retry through multiple routing layers, and partially publish
products while claiming success.
