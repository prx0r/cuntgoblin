# Queue / Leases / Idempotency

## Queue selection

Workers atomically lease READY rows ordered by priority using Postgres row locking
with `SKIP LOCKED`.

Conceptual query:

```sql
SELECT job_id
FROM jobs
WHERE state='READY'
  AND available_at <= now()
ORDER BY priority DESC, created_at ASC, job_id ASC
FOR UPDATE SKIP LOCKED
LIMIT :n;
```

## Logical job dedupe key

```text
sha256(
  workflow_id
  + workflow_version
  + trigger_id
  + logical_input_digest
  + semantic_stage
)
```

Unique DB constraint.

## Job != Attempt

A retry creates a new Attempt under the same logical Job.

## Lease

On lease:
- `leased_by`
- `lease_expires_at`
- attempt ID

Worker heartbeat interval <= one third of lease time.

If lease expires, manager reconciles output/commit evidence. Only then may the Job
return to READY.

## Dead letter

Non-retryable errors or exhausted attempts move to DEADLETTER with reason/evidence.
