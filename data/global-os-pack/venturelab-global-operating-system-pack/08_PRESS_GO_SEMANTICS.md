# `venturelab go`

## Preflight must pass

- migrations current
- singleton manager lease
- schema registry readable
- Dell current certificate + generated manifest
- HotSwap configured
- at least one usable model route
- artifact store writable
- secrets resolve
- Merkle self-test
- budget policy configured
- no zero-tolerance integrity alert

## Dry run first

```bash
venturelab go --dry-run
```

Outputs:
- workflows due
- jobs that would be created
- projected paid/free model use
- max concurrency
- projected spend
- potential external effects

It performs no external durable effects.

## Autonomous GO

```bash
venturelab go   --max-workers 4   --daily-llm-budget-usd 3   --max-paid-task-usd 0.50
```

GO:
1. starts manager;
2. creates only due triggers;
3. calculates priorities;
4. reserves budget/capacity;
5. leases bounded work;
6. executes/evaluates;
7. retries only classified retryable failures;
8. commits events/artifacts;
9. periodically checkpoints Merkle ledger;
10. automatically pauses affected queues on guardrail failure.

GO does not "run every idea."
