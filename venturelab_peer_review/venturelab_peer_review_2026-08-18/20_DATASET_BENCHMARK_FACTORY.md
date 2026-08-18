# Dataset / Benchmark Factory

```text
source registry
→ license/provenance
→ extraction
→ normalization
→ dedupe
→ leakage checks
→ annotation/gold
→ split policy
→ baseline runners
→ metrics
→ error analysis
→ release
```

Outputs:
- manifest,
- immutable source references,
- schema,
- splits,
- runner,
- baselines,
- error taxonomy,
- versioned results.

Strategically, this factory creates the evaluation assets required by Agent Factory, HotSwap, Research-Transfer and skill promotion.
