# Build Plan — VentureLab Market Intelligence + MetaFactory

*Based on venturelab-market-intelligence-ultimate-pack*
*Date: 2026-08-18*

---

## Overview

The pack formalizes the complete hierarchy:

```text
WORLD
 ↓
ORACLE REGISTRY
 ↓
OBSERVATIONS
 ↓
SIGNAL ENGINE
 ↓
TOPIC RADAR
 ↓
OPPORTUNITY MINERS
 ↓
CROSS-ORACLE JOIN LAB
 ↓
VALUE-OF-INFORMATION RESEARCH
 ↓
SOLUTION LAB
 ↓
FACTORY RESOLVER
 ↓
┌───────────────────────┐
│ existing │ extend │ genesis │
└───────────────────────┘
 ↓
PRODUCT ARCHETYPE COMPILER
 ↓
BUILD / CERTIFY / GITHUB / DEPLOY
 ↓
OUTCOME ORACLE
 ↓
METAFACTORY
 ↓
BOUNDED EVOLUTION
```

---

## Checkpoints (from pack)

### CP-MI0 — Freeze contracts
- [ ] Add schemas
- [ ] Add source registry
- [ ] Add immutable artifact/observation store
- [ ] No idea scoring changes yet

### CP-MI1 — Oracle Registry
- [ ] Implement OracleManifest
- [ ] Source-family identity
- [ ] Connector status
- [ ] Registry queries
- [ ] Initial adapters: OpenRouter, OpenAlex, ecosyste.ms, Hacker News, Unignorant

### CP-MI2 — AI-specific adapters
- [ ] Hugging Face
- [ ] MCP Registry
- [ ] Cloudflare Radar
- [ ] Google Trends official (if access)
- [ ] PyTrends fallback only

### CP-MI3 — Signal Engine
- [ ] Robust velocity
- [ ] Acceleration
- [ ] Robust burst
- [ ] Persistence
- [ ] Source breadth
- [ ] Initial CUSUM/change signal

### CP-MI4 — Topic Radar
- [ ] Candidate generation from each source family
- [ ] Entity/topic normalization
- [ ] TDS v1
- [ ] WATCH/ACTIVE_RESEARCH

### CP-MI5 — Opportunity Engine
- [ ] pain × growth × undersupply
- [ ] supply-demand
- [ ] policy shock
- [ ] research → implementation
- [ ] fragmentation

### CP-MI6 — Cross-Oracle Join Lab
- [ ] Canonical dimension bridges
- [ ] Semantic rule templates
- [ ] Anti-spurious gates
- [ ] Unignorant joins

### CP-MI7 — Value of Information
- [ ] Uncertainty decomposition
- [ ] Next research action

### CP-MI8 — Solution Lab
- [ ] Generate multiple solution mechanisms
- [ ] Product archetype resolver
- [ ] Cheapest falsification experiment

### CP-MI9 — Factory Resolver
- [ ] FactoryFit
- [ ] Use/extend/genesis routing

### CP-MI10 — Factory Genesis
- [ ] Hard gates
- [ ] FGS v1
- [ ] Candidate factory manifest
- [ ] Reference-product requirement

### CP-MI11 — Outcome Oracle
- [ ] Existing generated products become feedback sources

### CP-MI12 — Historical Replay
- [ ] Calibrate thresholds
- [ ] Measure false positives
- [ ] Revise method versions

### CP-MI13 — Bounded Evolution
- [ ] Representation
- [ ] Archive
- [ ] Controlled mutation surfaces
- [ ] Shadow tests

---

## File Structure

```text
venturelab/
├── factory/
│   ├── market/
│   │   ├── intelligence/      # Oracle registry, observations, claims
│   │   ├── signals/           # Signal engine (velocity, burst, etc.)
│   │   ├── topics/            # Topic radar
│   │   ├── opportunities/     # Opportunity miners
│   │   ├── joins/             # Cross-oracle joins
│   │   ├── voi/               # Value of information
│   │   └── solutions/         # Solution lab
│   ├── vision/                # Vision boundaries
│   └── genesis/               # Factory genesis
├── schemas/
│   ├── market_observation.schema.json
│   ├── signal.schema.json
│   ├── market_topic.schema.json
│   ├── opportunity.schema.json
│   ├── factory_proposal.schema.json
│   ├── oracle_manifest.schema.json
│   └── outcome.schema.json
├── config/
│   ├── source_catalog.yaml
│   ├── topic_discovery.yaml
│   ├── opportunity_scoring.yaml
│   └── factory_genesis.yaml
├── skills/
│   ├── market-scout/
│   ├── topic-radar/
│   ├── opportunity-miner/
│   ├── voi-researcher/
│   ├── solution-lab/
│   ├── factory-resolver/
│   ├── factory-genesis/
│   └── market-auditor/
└── reference_implementation/
    ├── market_algorithms.py
    └── test_market_algorithms.py
```

---

## Key Algorithms (from pack)

1. **Robust log-growth** — not naive percentage growth
2. **Median-absolute-deviation burst detection**
3. **Velocity, acceleration, persistence, source breadth**
4. **TopicDiscoveryScore**
5. **OpportunityScore** (evidence-aware)
6. **JoinScore** for cross-oracle hypotheses
7. **FactoryFit**
8. **Factory Genesis tipping point**
9. **Value of Information**

---

## Factory Genesis Policy

```text
Existing FactoryFit >= .75 → USE EXISTING
.60–.75 → EXTEND / FORK EXISTING
< .60 → MAY CONSIDER NEW FACTORY
```

New factory requires:
- >= 3 separate opportunities
- repeatability >= .65
- shared infrastructure reuse >= .60
- evidence confidence >= .70
- >= 3 independent source families
- opportunity mass >= .65
- reuse ROI >= .50

Then:
```text
FactoryGenesisScore >= .72 → SPAWN_CANDIDATE
.58–.72 → FACTORY_EXPERIMENT
< .58 → NO_FACTORY
```

---

## First Proof

NOT "generate many ideas."

The first proof is:

> Given real cross-source observations, can VentureLab identify an emerging market topic, derive one evidence-backed opportunity, decide whether an existing factory fits, and either route it or produce a justified FactoryProposal?

Only after this passes should the system autonomously spawn factories.

---

## Build Order

1. CP-MI0: Freeze contracts (schemas, source registry)
2. CP-MI1: Oracle Registry (5 adapters)
3. CP-MI2: AI-specific adapters (5 more)
4. CP-MI3: Signal Engine
5. CP-MI4: Topic Radar
6. CP-MI5: Opportunity Engine
7. CP-MI6: Cross-Oracle Join Lab
8. CP-MI7: Value of Information
9. CP-MI8: Solution Lab
10. CP-MI9: Factory Resolver
11. CP-MI10: Factory Genesis
12. CP-MI11: Outcome Oracle
13. CP-MI12: Historical Replay
14. CP-MI13: Bounded Evolution

---

*Build plan v1.0*
