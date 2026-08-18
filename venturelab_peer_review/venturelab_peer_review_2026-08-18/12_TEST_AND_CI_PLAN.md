# Test & CI Plan

## One root command

```bash
pytest -q
```

Do not rely on changing directories into copied reference packs.

## Required tests

### Import smoke
Catches missing modules immediately.

### API smoke
- empty DB startup,
- health,
- submit/get/cancel,
- restart persistence.

### MCP smoke
Use official SDK test client.

### Scheduler
- dependencies,
- claim race,
- lease expiry,
- retry limit,
- cancellation,
- idempotency,
- restart.

### Hermes adapter
Fake:
- good JSON,
- bad JSON,
- timeout,
- nonzero exit,
- cancellation,
- provider failure.

Opt-in real Hermes test separately.

### HotSwap
- actual fallback execution,
- verifier outcome updates posterior,
- workload budget,
- quota concurrency,
- provider health.

### Factory contract
Every factory plugin runs the same contract suite.

### Container
Build, start, query `/health`.

CI only counts as evidence when it runs on a clean checkout and attaches a green status to the commit.
