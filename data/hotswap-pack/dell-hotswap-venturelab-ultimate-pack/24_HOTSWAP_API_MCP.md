# HotSwap API + MCP

## REST

```text
POST /v1/plan
POST /v1/execute-plan/verify
POST /v1/outcome

GET  /v1/routes/status
GET  /v1/quotas
GET  /v1/accounts
GET  /v1/accounts/opportunities
GET  /v1/task-cells/{id}
GET  /v1/router/stats
```

## MCP

1. `hotswap_plan`
2. `hotswap_explain`
3. `hotswap_quota_status`
4. `hotswap_route_status`
5. `hotswap_account_opportunities`
6. `hotswap_record_outcome`
7. `hotswap_factory_savings`

## `hotswap_plan`

Input:
TaskSpec.

Output:
- primary
- fallbacks
- predicted success
- lower bound
- expected completion cost
- free quota reservation
- Dell evidence IDs
- explanation
- manual setup opportunities not used

## Explainability

Every plan says:
- why selected;
- why paid/free;
- which candidates were excluded;
- quota pressure;
- route outcome evidence;
- Dell evidence;
- exploration state.
