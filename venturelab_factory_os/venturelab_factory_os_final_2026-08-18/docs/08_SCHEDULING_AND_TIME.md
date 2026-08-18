# Scheduling

Schedules are canonical OS objects.

Fields:
- schedule id
- target factory/team/formula
- trigger type
- interval/cron/event metadata
- timezone
- budget window
- concurrency cap
- freshness requirement
- last run
- next eligibility
- idempotency template

Triggers:
- manual
- interval
- calendar/cron
- source event
- threshold
- freshness expiry
- post-release delay
- maintenance window

Hermes cron may execute a mirrored job; it does not own canonical scheduling state.
