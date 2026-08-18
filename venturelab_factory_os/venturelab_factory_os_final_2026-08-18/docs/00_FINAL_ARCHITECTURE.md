# Final Architecture

```text
WORLD / SOURCES
      |
      v
OBSERVATIONS ---> EVIDENCE / CLAIMS
      |                  |
      +--------+---------+
               v
       INTELLIGENCE LENSES
 frontier | agent pain | API gaps
 global/country | commerce | directories
               |
               v
        OPPORTUNITY GRAPH
               |
               v
      ECONOMIC ORACLE / PORTFOLIO
 expected value | uncertainty | cost | timing
               |
               v
           FACTORY FIT
    reuse | extend | spawn | reject
               |
               v
        CANONICAL WORKGRAPH
 dependencies | gates | budgets | deadlines
               |
               v
       FACTORY OS SCHEDULER
      "what runs next, and why?"
               |
      +--------+--------+
      |                 |
      v                 v
 HOTSWAP ROUTING    GLOBAL TEAMS
 worker/model/      research/red-team/
 provider           QA/publish/security/etc.
      |                 |
      +--------+--------+
               v
          EXECUTORS
   Hermes default | deterministic
   optional coding workers | Beads mirror
               |
               v
          ARTIFACTS
               |
               v
 VERIFY -> CERTIFY -> PUBLISH
               |
               v
            OUTCOMES
               |
               v
      PORTFOLIO LEARNING
```

## Canonical objects

- Observation
- Evidence
- Claim
- Opportunity
- FactoryDefinition
- FactoryRun
- WorkGraph
- WorkNode
- TeamDefinition
- ExecutionRoute
- Artifact
- GateResult
- Certificate
- Release
- Outcome
- CostEvent
- Decision
- Schedule
- LedgerEvent

## Authority

VentureLab's database owns lifecycle truth.

Hermes Kanban is a default execution/operations adapter. Beads is an optional dependency/coding
mirror. Neither gets to independently decide canonical completion.

Workers return artifacts, evidence and structured results. Independent gates commit success.

## Economic hierarchy

1. Portfolio: should this opportunity/factory receive resources?
2. Work scheduler: which ready node has highest marginal value now?
3. HotSwap: given a node should run, which worker/model/provider satisfies quality at minimum expected cost?

This makes orchestration an extension of HotSwap without collapsing every decision into model routing.

## Durability

Start with SQLite WAL + explicit transactions.

```text
PENDING -> READY -> LEASED -> RUNNING -> VERIFYING -> SUCCEEDED
                         |                    |
                         |                    +-> RETRY_WAIT -> READY
                         +------------------------> FAILED
```

Leases expire. Stale work is reclaimed. Every durable transition emits a ledger event.

## Proof

Each event is hash-chained. Event hashes are periodically committed into RFC6962-style
SHA-256 Merkle trees. Epoch roots can be signed with Ed25519 and optionally anchored using
RFC3161 or a transparency log.

## Factory types

1. API / Data Oracle
2. App / Micro-SaaS
3. Connector / Integration
4. Agent / MCP / A2A service
5. Directory / Vertical Intelligence
6. Shop / Marketplace
7. Developer Tool / CLI
8. Browser Extension
9. Dataset / Benchmark
10. Data Pipeline / Automation

No YouTube/content factory.

## Global teams

- research/evidence
- architecture
- builder
- QA/test
- red team
- security/privacy
- provenance/certification
- cost/FinOps
- docs/publisher
- release/deploy
- observability
- post-release audit
- maintenance/refactor
- portfolio review
