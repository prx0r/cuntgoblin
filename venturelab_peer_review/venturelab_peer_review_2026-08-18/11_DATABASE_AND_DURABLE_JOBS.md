# Database and Durable Jobs

## SQLite first

Use WAL and transactions until workload proves a multi-host database is required.

## Job states

```text
PENDING
 → READY
 → LEASED
 → RUNNING
 → VERIFYING
    ├→ SUCCEEDED
    ├→ RETRY_WAIT → READY
    └→ FAILED

nonterminal → CANCELLED
```

## Required semantics

- atomic claim,
- lease expiry,
- bounded retry,
- validated transition,
- idempotent side effects,
- restart/resume.

## Event log

Every transition appends a structured event. The current job row is a projection.

## Idempotency

Derive from:
```text
factory + task kind + canonical input hash + policy version
```

Publication has its own idempotency key so a crash cannot create two external objects.
