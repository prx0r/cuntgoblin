# Product Archetype Resolver

A Factory can output multiple product types.

## Decision matrix

### Data Oracle / API-MCP
Use when:
- truth changes over time;
- structured data is central;
- historical observations compound;
- agents are important consumers.

### Benchmark
Use when:
- customer problem is "which system is better?";
- objective/reproducible evaluation exists;
- task corpus can be defined.

### Agent System
Use when:
- solution itself is a long-running autonomous workflow;
- state/roles/tools/verification matter.

### Registry
Use when:
- discovery/versioning/identity/lineage is central.

### Library/CLI
Use when:
- value can be delivered locally;
- no persistent server/data needed.

### Dataset
Use when:
- cleaned/provenanced corpus itself is durable value.

### Evidence Publishing
Use when:
- main consumer is human;
- information demand/search distribution matters;
- claims can be refreshed from structured evidence.

### SaaS
Use only when:
- persistent user state/auth/billing/workflow adds real value;
- do not wrap an API with dashboard merely because SaaS is familiar.

## Resolver output

```json
{
  "recommended": "data-oracle",
  "score": 0.84,
  "basis": [
    "requires changing market data",
    "agents are primary consumers",
    "history compounds"
  ],
  "alternatives": [...]
}
```
