# VentureLab Market Intelligence + MetaFactory — Ultimate Build Pack

Target: `prx0r/cuntgoblin`
Reviewed factory head: `3ac795ab5b55f5643a1aeafc9a004c1b96a6ead9`
Reviewed oracle seed: `prx0r/unignorant` @ `836f1b269004f039b11dd952d660918f02e26595`
Pack date: 2026-08-18

This pack is an implementation handoff for adding the layer that should sit ABOVE VentureLab's existing idea/build machinery:

```text
WORLD / MARKETS / RESEARCH / GOVERNMENT DATA
                   ↓
              ORACLE LAYER
                   ↓
           MARKET INTELLIGENCE
                   ↓
           OPPORTUNITY GRAPH
                   ↓
              METAFACTORY
       ┌───────────┼────────────┐
       ↓           ↓            ↓
 use factory   extend factory   spawn factory
       ↓           ↓            ↓
             PRODUCT SEARCH
                   ↓
          ARCHETYPE COMPILERS
                   ↓
       BUILD → CERTIFY → GITHUB
                   ↓
             REAL OUTCOMES
                   ↓
           OUTCOME ORACLE
                   ↓
       MARKET / FACTORY LEARNING
```

## Core correction

Do NOT make `unignorant` a "misc data factory".

`unignorant` is an **Oracle Provider**: a global reality/data graph with country, trade,
cost-of-living, development, aid, local-life and other streams. Factories consume Oracle Providers.

The central abstractions become:

1. `Oracle`
2. `Observation`
3. `Signal`
4. `MarketTopic`
5. `Opportunity`
6. `Factory`
7. `Product`
8. `Pattern`
9. `Outcome`

## What this pack contains

- exact ontology and schemas
- verified source catalogue
- source adapter policy
- PyTrends policy (experimental fallback only)
- OpenAlex/arXiv research radar design
- topic discovery algorithms
- trend/change/burst algorithms
- cross-oracle join engine
- opportunity miners
- anti-spurious-correlation gates
- granular opportunity scoring
- value-of-information research selection
- product-type resolver
- explicit factory-spawn tipping point
- Factory Genesis lifecycle
- portfolio resource allocator
- outcome feedback
- pattern registry
- Hermes skill contracts
- API/MCP contract
- unignorant integration
- AI Market Oracle integration
- government-data opportunity examples
- evolutionary endgame based on agentic computation graphs, DGM,
  ShinkaEvolve, AlphaEvolve and Red Queen-style evaluator evolution
- reference Python implementation for the pure decision algorithms
- deterministic contract tests
- phased implementation manifest

## Non-negotiable rule

Research prose is NOT market truth.

Every score must point to structured observations/signals. If evidence is absent,
the state is `UNKNOWN`, not zero and not an invented neutral prior.

## Build target

The first proof is NOT "generate many ideas."

The first proof is:

> Given real cross-source observations, can VentureLab identify an emerging market
> topic, derive one evidence-backed opportunity, decide whether an existing factory
> fits, and either route it or produce a justified FactoryProposal?

Only after this passes should the system autonomously spawn factories.
