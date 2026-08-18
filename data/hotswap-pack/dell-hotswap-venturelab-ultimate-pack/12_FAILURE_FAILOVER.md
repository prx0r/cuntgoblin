# Failure Taxonomy and Failover

The router should not treat every failure as "try another model".

## AUTH
401/403 credential failure.

Action:
- mark credential/account DEGRADED
- no repeated retry
- same-model alternate credential/deployment
- then fallback

## TRANSIENT_RATE_LIMIT
429 with short Retry-After / provider transient limit.

Action:
- respect Retry-After
- cooldown exact deployment/key
- use same model elsewhere immediately if available
- do not globally blacklist model

## QUOTA_EXHAUSTED
daily/session/weekly/account allowance exhausted.

Action:
- mark affected quota window exhausted
- cooldown until known reset
- re-resolve route
- do not retry the same exhausted account

## SERVER
5xx / overload / connection failure.

Action:
- increment endpoint breaker
- fail over same model deployment
- breaker opens after policy threshold

## CONTEXT
request exceeds context/output capability.

Action:
- this is not a transient retry
- re-resolve with higher context requirement
- optionally compress if TaskSpec allows

## INVALID_RESPONSE
malformed/empty response or repeated tool protocol failure.

Action:
- bounded retry
- record route quality failure
- then fallback

## TASK_FAILURE
API succeeded but factory evaluator failed.

Action:
- record success=0 in task-cell outcome
- escalate according to plan
- this is the most important learning signal

## SAFETY/POLICY REFUSAL
Do not automatically use fallback to circumvent a provider safety refusal.
Classify separately and return to task policy.

## Circuit breaker

Per exact deployment/account:
CLOSED → OPEN → HALF_OPEN.

Use rolling recent failures and cooldown, not permanent provider labels.
