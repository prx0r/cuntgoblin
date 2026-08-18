# VentureLab / `prx0r/cuntgoblin` Engineering Peer Review

**Date:** 2026-08-18  
**Reviewed branch:** `master`  
**Reviewed head:** `a56716251f4c60a2593e71efc6c88c5c61beb5bf`

This bundle is an engineering recovery and expansion plan for VentureLab.

## Bottom line

The repository contains real, useful engineering—especially the HotSwap router, market/factory-genesis algorithms, and agent architecture resolver—but **the current reviewed head is not an end-to-end working system**.

Several failures are statically provable:

1. `Dockerfile` starts `factory.system:app`, but `factory/system.py` is absent.
2. `api.py` and `mcp/server.py` import `factory.system.VentureLabSystem`, which is absent.
3. `factory/global_os/go.py` imports multiple sibling modules, while the reviewed `factory/global_os/` listing contains only `go.py`.
4. `factory/research/packet.py` imports `search_github` and `search_arxiv` from `factory/scoring/engine.py`; those functions are absent from the reviewed engine.
5. The MCP implementation is a handwritten dispatcher, not an SDK-backed MCP server.
6. GitHub exposed no status checks or workflow run for the reviewed head during inspection.
7. A virtual environment and Python cache state are committed.
8. Legacy research logic confuses search-result counts with actual evidence and contains a product-search stub.

This is repairable without rewriting the strongest modules.

## Preserve

- `factory/hotswap/`
- `factory/market/market_algorithms.py`
- `factory/agenthub/resolver.py`
- content-addressed provenance/evidence intent
- Hermes integration
- reusable templates

## Target architecture

One **Factory Kernel** owns durable state and contracts.

> Deterministic Python owns state, leases, budgets, idempotency, gates and publication. Hermes owns bounded reasoning/tool execution. HotSwap chooses routes. Independent verifiers decide acceptance.

Read:
1. `00_EXECUTIVE_VERDICT.md`
2. `03_P0_BREAKAGES.md`
3. `05_TARGET_ARCHITECTURE.md`
4. `06_HERMES_ORCHESTRATION.md`
5. `25_PRIORITY_ROADMAP.md`
