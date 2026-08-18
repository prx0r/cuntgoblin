# Global State Machines

## Job

```text
PENDING -> READY -> LEASED -> RUNNING -> VERIFYING -> SUCCEEDED
                              |            |
                              |            +-> RETRY_WAIT -> READY
                              +-> BLOCKED
                              +-> FAILED
                              +-> DEADLETTER
                              +-> CANCELLED
```

Allowed transitions are validated in code.

## Workflow run

`CREATED -> QUEUED -> RUNNING -> VERIFYING -> SUCCEEDED | PARTIAL | FAILED | CANCELLED`

## Product release

```text
DRAFT
-> CERTIFIED
-> GITHUB_STAGED
-> GITHUB_PUBLISHED
-> DEPLOYING
-> LIVE_VERIFIED
-> RELEASED
```

`GITHUB_PUBLISHED` is not `RELEASED`.

## Factory

`PROPOSED -> EXPERIMENTAL -> ACTIVE -> PAUSED -> RETIRED`

## Architecture build

`EXPERIMENTAL -> VALIDATED -> REUSABLE_CANDIDATE -> VERIFIED`

## Event rule

Every state change emits an append-only event with:
actor, cause, correlation ID, schema version and evidence/artifact references.
