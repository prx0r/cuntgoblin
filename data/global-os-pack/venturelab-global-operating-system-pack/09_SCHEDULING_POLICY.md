# Scheduling Policy

Schedules are versioned data in Postgres.

Fields:
- schedule ID
- WorkflowSpec/version
- cron/interval
- timezone
- deterministic jitter
- max overlap
- catch-up policy
- budget envelope
- enabled
- next due

## Suggested rhythms

### 15–60 minutes
- source/provider health
- queue health
- high-value deal/endpoint changes where useful

### Daily
- AI market observations
- Dell deal refresh
- evidence gap refresh
- product health
- account/deal opportunities

### Weekly
- Topic Radar
- Opportunity mining
- cross-Oracle joins
- product outcomes
- router shadow benchmark sample
- AgentHub research/repo ingest

### Monthly/epoch
- factory portfolio review
- spawn/retire proposals
- router calibration
- benchmark refresh
- pattern promotion
- bounded evolution experiment
- archival/checkpoint export

## Jitter

Use deterministic jitter derived from schedule ID + logical date.

## Catch-up

High frequency telemetry: latest-only.
Daily snapshots: at most one missing period by default.
Release/compliance steps: never silently skip.

Default `max_overlap=1`.
