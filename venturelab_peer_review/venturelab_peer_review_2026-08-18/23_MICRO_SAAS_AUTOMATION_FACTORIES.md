# Micro-SaaS / Automation / Data Pipeline Factories

## Micro-SaaS
Validated narrow workflow pain → minimal app → tests → deployment → usage telemetry.

Do not generate generic feature-rich SaaS.

## Automation
```text
trigger → state → action → approval → retry → audit
```

Use Hermes/LLMs for fuzzy transformations. Use deterministic code for schedules, state, validation, writes and accounting.

## Data Pipeline
Inputs → schema/profiling → normalization → quality gates → lineage → API/warehouse/export.

This factory is highly machine-verifiable and can underpin many data-oracle products.
