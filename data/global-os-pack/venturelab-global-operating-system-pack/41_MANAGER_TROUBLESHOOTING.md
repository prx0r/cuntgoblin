# Manager Troubleshooting

Duplicate jobs:
check unique trigger and dedupe keys.

Two active manager leaders:
use a Postgres application/advisory singleton lease, not only a PID file.

Lease stuck:
inspect heartbeat/attempt evidence; reconcile before requeue.

Retry loop:
classify failure; deterministic errors must not retry indefinitely.

Schedule fires twice:
unique `(schedule_id, logical_due_time)` trigger.

Kanban complete / global RUNNING:
adapter reconciliation failed; validate artifact/evaluator then commit global state.

Global SUCCEEDED / Kanban open:
repair projection. Do not reverse global state merely to match UI.

Budget below zero:
pause paid queue immediately and audit reservation reconciliation.

Merkle mismatch:
stop publication/promotion until event sequence/artifacts are verified.
