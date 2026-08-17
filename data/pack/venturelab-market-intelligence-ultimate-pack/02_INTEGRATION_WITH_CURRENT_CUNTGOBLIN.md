# Integration With Current VentureLab

The current repo already expects:

```text
factory/
  domain/
  scoring/
  market/
  ideas/
  vision/
```

and already enforces:

- logged evidence
- content hashes
- provenance
- deterministic gates
- Hermes-driven research/build
- no synthetic evidence

Do not create a second parallel project.

## Target tree

```text
factory/
├── domain/
│   ├── market.py
│   ├── oracle.py
│   ├── opportunity.py
│   ├── factory.py
│   └── outcome.py
│
├── market/
│   ├── registry.py
│   ├── ingest.py
│   ├── normalize.py
│   ├── signals.py
│   ├── topics.py
│   ├── joins.py
│   ├── opportunity_miners.py
│   ├── scoring.py
│   ├── voi.py
│   └── snapshots.py
│
├── oracles/
│   ├── registry.py
│   ├── unignorant.py
│   ├── openrouter.py
│   ├── huggingface.py
│   ├── ecosystems.py
│   ├── openalex.py
│   ├── trends.py
│   ├── cloudflare_radar.py
│   ├── hackernews.py
│   ├── mcp_registry.py
│   └── worldbank.py
│
├── metafactory/
│   ├── resolver.py
│   ├── genesis.py
│   ├── portfolio.py
│   └── pattern_promotion.py
│
├── ideas/
│   ├── generators/
│   └── solution_lab.py
│
├── vision/
│   ├── schema.py
│   └── versioning.py
│
└── evolution/
    ├── representation.py
    ├── bounded_search.py
    └── archive.py

schemas/
config/
skills/
tests/
data/
  market/
    artifacts/
    observations/
    snapshots/
    signals/
    topics/
    opportunities/
    decisions/
```

## Existing scoring engine

Do not inject hard-coded market values into generic `score_idea()`.

Replace that path with:

```text
Opportunity
  references Signal IDs
  references Observation IDs
        ↓
OpportunityScorecard
```

The idea scorer may consume the OpportunityScorecard, but it cannot fabricate
market context.

## Existing Hermes discipline

Preserve current operational rules.

This pack adds Hermes skills; it does not supersede `AGENTS.md` or `CODING-AGENT.md`.
