# Event Model

Append-only events are the audit spine.

Examples:
- workflow.created
- job.enqueued
- job.leased
- job.started
- artifact.created
- evaluation.completed
- job.failed
- job.succeeded
- product.certified
- product.published
- checkpoint.created

Fields:
- sequence
- event_id
- aggregate_type
- aggregate_id
- event_type
- occurred_at
- actor
- causation_id
- correlation_id
- payload
- artifact_digest
- schema_version

Operational projection tables can be rebuilt from events plus permanent identity data
where practical.
