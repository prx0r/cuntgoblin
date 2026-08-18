# Global Manager Architecture

## Three orchestration scopes

### Global Manager — canonical
Stores:
- WorkflowSpecs
- schedules
- workflow runs
- jobs/dependencies
- attempts/leases
- budgets
- artifacts
- events
- release transactions
- Merkle checkpoints

### Hermes Kanban — per-run collaboration
Use for:
- visible agent tasks
- worker profiles
- comments/handoffs
- heartbeat
- local blockers

It mirrors global jobs. It does not own product or portfolio truth.

### Hermes Cron — trigger/delivery
Use for:
- reminders
- simple scheduled Hermes sessions
- ingress into manager workflows
- delivery of generated reports

The canonical schedule remains in Postgres.

## Why Postgres first

It keeps the current stack small and inspectable and can support queue-like concurrent
workers using row leases. Add a Temporal execution adapter only when the system genuinely
becomes distributed/long-lived enough to justify it.

## Temporal adoption trigger

Consider Temporal when at least two are true:
- more than three independently deployed worker/manager services;
- many workflows last days/weeks;
- compensation/timers become complex;
- thousands of concurrent durable workflow instances;
- retry/timer code is becoming a major maintenance burden;
- multi-region workflow recovery is needed.
