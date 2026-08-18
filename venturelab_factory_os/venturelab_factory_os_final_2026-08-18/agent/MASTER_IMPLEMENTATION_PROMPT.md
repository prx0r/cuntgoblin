# MASTER IMPLEMENTATION PROMPT

Implement this pack into the existing `prx0r/cuntgoblin` repository.

## Non-negotiable

1. Do not wholesale-rewrite working HotSwap, market algorithms or AgentHub.
2. Read current code before each change.
3. Factory OS DB is canonical.
4. Hermes is the default executor, but an adapter.
5. Beads is optional/mirrored, never a second canonical database.
6. A worker cannot mark canonical success without verification.
7. No empty stubs, fake measurements or mock certificates count.
8. Source errors are explicit errors, not zero.
9. Every write path is idempotent or uniquely keyed.
10. Every phase ends with tests, doctor output and a commit.

## Baseline first

```bash
git status --short
git rev-parse HEAD
python3 -V
find factory -maxdepth 3 -type f | sort
python3 -m pytest -q
```

Save baseline failures.

## Phase 0 — repair current boot

Use the previous peer-review ZIP P0 list first:
- create a working `factory.system`
- repair Docker boot
- repair research imports
- remove/repair broken `global_os` imports
- replace handwritten MCP after core boot
- clean CI
- remove committed venv/cache

Do not build a new OS on a broken composition root.

## Phase 1 — canonical core

Transplant the reference package into `factory/os/`:
- core
- DB/schema/migrations
- proof ledger
- WorkGraph
- unit tests

## Phase 2 — Hermes + HotSwap

Wire canonical WorkNodes to Hermes.
A run must:
1. lease canonical node
2. invoke executor
3. capture exit/timeout/structured result
4. create artifacts
5. run independent gates
6. commit accepted/retry/failed state
7. record cost

Extend existing HotSwap with composite ExecutionRoute:
`executor/profile/model/provider/capabilities`.

Do not rewrite existing route math.

## Phase 3 — factories and teams

Implement immutable manifest registry.
Migrate existing API/AgentHub behavior first.
Add global team expansion.

## Phase 4 — economics/learning/scheduling

Add:
- cost ledger
- release/outcome lineage
- factory posterior stats
- allocation index
- opportunity-cost snapshot
- chronological replay
- canonical schedules

## Phase 5 — factory fixtures

In order:
1. API
2. App
3. Connector
4. Agent service
5. Directory
6. Shop/Marketplace
7. Developer Tool
8. Browser Extension
9. Benchmark
10. Data Pipeline

## Proof of completion

```bash
python3 -m pytest -q
python3 -m factory.os.cli doctor
python3 -m factory.os.cli verify-ledger
python3 -m factory.os.cli list-factories
docker build -t venturelab:test .
```

Then deliberately:
- mutate one certified artifact -> certificate verification MUST fail
- mutate one old ledger event -> chain verification MUST fail
- concurrently claim one ready node -> only one worker MUST win

If those anti-cheat tests do not behave correctly, the phase is not done.
