# Operations

## Jobs

Dell refresh:
source-specific cadence.

HotSwap:
- per-task plan
- continuous outcome update

Quota:
- reservation GC every few minutes
- provider balance reconciliation periodically
- immediate update after quota/error headers

Account opportunities:
daily Dell scan + deal-change trigger.

Router retraining:
weekly or after enough new outcomes, not every request.

## Health

Expose:
- Dell reachable
- LiteLLM reachable
- configured active routes
- free routes available
- quota ledger consistency
- breakers open
- Hermes runtime available

## Degraded mode

If Dell unavailable:
use last signed/cache snapshot only within freshness policy.

If LiteLLM unavailable:
fail closed unless explicitly configured direct-provider emergency path.

If outcome store unavailable:
execute but mark learning telemetry pending; never invent success.
