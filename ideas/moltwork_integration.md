# Moltwork Integration Ideas

*2026-08-17T23:30:00Z · Cool ideas from moltwork project*

---

## What Moltwork Is

Moltwork is an **open exchange for verifiable units of machine work**. It's a marketplace where:

1. Someone posts a BatchJob (e.g., "translate 10,000 Sanskrit verses")
2. Workers (agents/humans) lease WorkUnits
3. Workers execute and submit with cryptographic receipts
4. Verifiers evaluate and sign
5. Payment happens via x402

---

## Cool Ideas to Steal

### 1. Model Evidence Grades (M0-M5)

```text
M0 — CLAIMED (worker self-report)
M1 — SIGNED WORKER (runtime signs execution declaration)
M2 — MOLTWORK ROUTED (inference via Moltwork gateway)
M3 — PROVIDER ATTESTED (provider signs request/output/model)
M4 — TEE (measured runtime + model hash + hardware attestation)
M5 — VERIFIABLE INFERENCE (zkML/proof system)
```

**HotLoader integration:** Use these grades to score provider trustworthiness.

### 2. Route Ranking Algorithm

```typescript
function rankRoutes(rewardUsd, routes) {
  return routes
    .filter(r => r.commercialWorkAllowed)
    .map(r => ({
      ...r,
      expectedRevenueUsd: rewardUsd * r.predictedPassProbability,
      expectedProfitUsd: rewardUsd * r.predictedPassProbability - r.estimatedCostUsd
    }))
    .sort((a, b) => b.expectedProfitUsd - a.expectedProfitUsd);
}
```

**HotLoader integration:** Rank routes by expected profit, not just cost.

### 3. Job Economics Tracking

```typescript
function jobEconomics(receipts) {
  return {
    acceptanceRate: accepted / total,
    payoutPerAccepted: totalRewards / accepted,
    productionCostPerAccepted: totalCompute / accepted,
  };
}
```

**HotLoader integration:** Track real economics per provider/model.

### 4. WorkReceipt Schema

```json
{
  "worker": {"agent_id": "...", "identity": "..."},
  "execution": {
    "runtime": "hermes",
    "model_claim": "kimi-k2.6",
    "model_evidence": {"level": "ROUTED_PROVIDER", "provider": "moonshot"},
    "reported_cost_usd": 0.00382
  },
  "evaluation": {
    "verifier": "patala-prove:v4",
    "score": 0.9721,
    "accepted": true
  },
  "payment": {"amount_usd": 0.012}
}
```

**HotLoader integration:** Use receipts to build quality/cost curves.

### 5. Model Policy

```json
{
  "mode": "ALLOWLIST",
  "allowlist": ["gpt-4o", "claude-3.5-sonnet"],
  "minimumEvidence": "ROUTED_PROVIDER"
}
```

**HotLoader integration:** Let users specify model policies.

---

## Integration Plan

### Phase 1: Receipts
- Use Moltwork receipts as quality/cost data points
- Build quality curves from accepted/rejected receipts

### Phase 2: Routing
- Use rankRoutes algorithm for HotLoader
- Add model evidence grades to provider scoring

### Phase 3: Marketplace
- Let workers register via Moltwork
- Use Moltwork for batch jobs

---

## Key Insight

Moltwork solves the **verification problem** — how do you know what model actually ran?

HotLoader solves the **routing problem** — which model should run?

Together they form a complete system:

```text
Moltwork: "This is what happened"
HotLoader: "This is what should happen"
```

---

*This is the integration plan for Moltwork + HotLoader.*
