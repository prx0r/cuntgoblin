# Dell Integration

## HotSwap asks Dell for facts and candidate routes

Preferred API:

`POST /v1/resolve/candidates` or equivalent query service.

Return candidates BEFORE final ranking.

Required fields:

```text
route_id
model_id
endpoint_id
provider_id
offer_id

input price
output price
economic access class
quota policies
promo expiry

context
max output
tools/json/vision/streaming
automation/card/phone/KYC

availability/freshness
TTFT/TPS/reliability measurements

task-quality evidence
evidence confidence
evidence IDs

activation recipe
```

## Dell must expose activation information

HotSwap Account Opportunity Queue needs:
- account required?
- API key setup?
- OAuth?
- card?
- phone?
- KYC?
- region?
- manual steps?
- estimated setup friction
- promo expiry

## Runtime observations back to Dell

Do not directly overwrite Dell facts.

Send as observations:
- route success/failure
- 429 / quota exhausted
- latency
- TTFT/TPS
- actual model/provider
- observed token usage

Dell may reconcile those into measured route state.

## HotSwap-local state

Keep local:
- task-cell posteriors
- quota reservations
- active circuit breakers
- per-factory forecasts

These are execution state rather than provider truth.
