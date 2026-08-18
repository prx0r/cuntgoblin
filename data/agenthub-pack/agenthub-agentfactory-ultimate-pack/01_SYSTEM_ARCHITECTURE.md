# System Architecture

```text
                    MARKET INTELLIGENCE
                            │
                            ▼
                       OPPORTUNITY
                            │
                            ▼
                       SOLUTION LAB
                            │
                solution needs autonomy?
                    │               │
                   no              yes
                    │               │
          normal ProductFactory     ▼
                            ARCHITECTURE NEED
                                    │
                                    ▼
                          AGENTHUB RESOLVER
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
             REUSE                FORK              SYNTHESIZE
                │                   │                   │
                └───────────────────┼───────────────────┘
                                    ▼
                          ARCHITECTURE BUILD
                                    │
                      role/task model slots
                                    │
                                    ▼
                                 HOTSWAP
                                    │
                                    ▼
                           HERMES ADAPTER
                                    │
                                    ▼
                             SANDBOX / RUN
                                    │
                                    ▼
                           BENCHMARK LAB
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
             outcome            failure/recovery       cost
                │                   │                   │
                └───────────────────┼───────────────────┘
                                    ▼
                                AGENTHUB
                           registry + lineage
                                    │
                                    ▼
                          ARCHITECTURE FACTORY
                         search / mutate / evolve
                                    │
                                    ▼
                               better builds
```

## AgentHub planes

### Catalog plane
What systems/builds/patterns exist?

### Execution plane
How do I install/start/stop/resume/inspect one?

### Evaluation plane
What evidence shows it works?

### Decision plane
Which architecture should solve this task/solution?

### Evolution plane
How can existing architectures be mutated or recombined?

Keep these logically separated even if they share one DB initially.
