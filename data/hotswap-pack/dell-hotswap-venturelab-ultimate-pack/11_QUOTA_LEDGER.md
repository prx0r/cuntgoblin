# Runtime Quota Ledger

Dell stores published/observed quota policies.
HotSwap stores CURRENT LOCAL CONSUMPTION and reservations.

## Tables

See `sql/hotswap.sql`.

Core:
- accounts
- route_accounts
- quota_windows
- quota_usage
- quota_reservations
- route_cooldowns

## Window types

- fixed
- rolling
- sliding
- provider_reported
- unknown

## Reservation state

```text
PENDING
COMMITTED
RELEASED
EXPIRED
```

## Reconciliation sources, strongest first

1. provider explicit remaining/reset headers
2. LiteLLM actual request token/spend logs
3. response usage tokens
4. local tokenizer estimate
5. Dell published allowance only

Do not treat provider marketing quota as current remaining balance.

## Crash recovery

Reservations have TTL.
Expired orphan reservations are released after checking no matching completed request exists.
