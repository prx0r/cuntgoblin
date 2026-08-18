# HotSwap Roadmap

## Keep the current router

Its core decision is good: select the cheapest route likely to complete the task while respecting capabilities, quality, budgets and quota scarcity.

## Fix integration

Current integration is mostly planning. Wire actual execution:

```text
plan
→ primary execute
→ verify
→ accepted? done
→ retryable? fallback
→ verify
→ record route outcome
```

Also ensure `FactoryHotSwap` shares the exact router's bandit/quota instances rather than constructing disconnected side objects.

## Reward hierarchy

Never reward HTTP 200.

Prefer:
1. deterministic contract,
2. independent verifier,
3. build/product acceptance,
4. delayed downstream metric.

## Implement next

### Workload budget
A factory run with 100 jobs needs a total budget, not only per-request caps.

### Contextual features
Gradually add:
- task type,
- difficulty,
- criticality,
- context/output,
- tools,
- modality,
- provider live health,
- quota remaining,
- workload budget remaining.

### Preference frontier
Allow cost-vs-quality preference without retraining separate policies.

Do not train a neural router until you have trustworthy local outcomes.
