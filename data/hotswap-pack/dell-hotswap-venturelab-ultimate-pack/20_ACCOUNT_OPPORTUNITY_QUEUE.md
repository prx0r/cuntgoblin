# Account / Deal Opportunity Queue

Dell may discover a great free or promotional route that is not yet configured.

Do NOT silently exclude it forever.

Create `AccountOpportunity`.

## States

```text
DISCOVERED
USER_ACTION_REQUIRED
CONFIGURED
VERIFYING
ACTIVE
DEGRADED
EXPIRED
REJECTED
```

## Score whether setup is worth it

```text
monthly_value =
forecast_eligible_tasks
× (baseline_ECPS - candidate_ECPS)

setup_value =
monthly_value
× promo_survival_probability
× evidence_confidence
- setup_friction_cost
```

Setup friction can be ordinal rather than invented dollars:

```text
0 automatic/API key already available
1 simple API key
2 email/OAuth/manual click
3 card/phone/manual approval
4 KYC/contract/sales process
```

Rank opportunities by value / friction.

## Output

```yaml
provider: ...
deal: ...
why:
  expected_savings: ...
  tasks_covered: ...
setup:
  friction: 2
  manual: true
  recipe: [...]
expires_at: ...
confidence: ...
```

## User action

Do not attempt to automate around provider signup restrictions.

The queue tells the operator what is worth configuring.

After setup:
- add credential through LiteLLM/Hermes's supported setup path;
- run verification;
- mark ACTIVE.

## Dashboard

Use CLI/MCP first:

```text
hotswap accounts opportunities
hotswap accounts active
hotswap accounts verify <id>
```

LiteLLM UI remains the credential/spend dashboard.
