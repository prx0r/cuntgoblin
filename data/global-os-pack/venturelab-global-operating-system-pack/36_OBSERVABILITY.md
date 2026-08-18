# Observability

Propagate IDs:
- request_id
- correlation_id
- workflow_run_id
- job_id
- attempt_id
- Hermes session/task ID
- HotSwap plan ID
- Dell route ID

Manager metrics:
- queue depth
- lease expiration
- retries/dead letters
- job latency
- spend/reserved

HotSwap:
- cost per successful task
- free completion %
- fallback rate
- quota pressure

Factories:
- time to certified output
- human intervention
- failure stage

AgentHub:
- benchmark throughput
- architecture cost/success
- promotion/rejection

Use structured JSON logs. Add OpenTelemetry once cross-service debugging justifies it.
