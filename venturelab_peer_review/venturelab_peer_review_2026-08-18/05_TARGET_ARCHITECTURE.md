# Target Architecture — Factory Kernel

```text
Opportunity
   │
   ▼
Research Plan → Evidence → Verified Evidence Bundle
   │                         │
   └─────────────────────────┤
                             ▼
                       Opportunity Score
                             │
                     factory fit/genesis
                             │
                             ▼
                         Build Plan DAG
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
           Job              Job              Job
            └────────────────┼────────────────┘
                             ▼
                         Artifacts
                             │
                             ▼
                    independent verifier
                     fail /       \ pass
                      ▼             ▼
                    replan       certificate
                                    │
                                    ▼
                                  publish
                                    │
                                    ▼
                                  observe
                                    │
                                    ▼
                       route/factory/skill learning
```

## Responsibilities

### Canonical store
SQLite first, WAL, transactional leases. Metadata in DB; large artifacts content-addressed externally/filesystem.

### Scheduler
Deterministic:
- dependency readiness,
- atomic claim,
- lease,
- retry,
- budgets,
- cancellation,
- terminal state.

### Hermes
One bounded reasoning/tool job at a time.

### HotSwap
Chooses route before execution; receives verifier outcome after.

### Verifier
Deterministic tests first, semantic verifier only where needed.

### Factory plugins
Domain logic only. No private queue/database/model stack.

### Interfaces
REST/MCP/CLI/Hermes/cron all call the same kernel.
