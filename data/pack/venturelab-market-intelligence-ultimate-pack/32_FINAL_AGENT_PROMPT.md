# COPY INTO THE CUNTGOBLIN REPO AGENT

You are integrating the VentureLab Market Intelligence + MetaFactory architecture.

Target repo baseline reviewed: 3ac795ab5b55f5643a1aeafc9a004c1b96a6ead9.
Related Oracle seed: prx0r/unignorant @ 836f1b269004f039b11dd952d660918f02e26595.

Read the entire pack before editing.

## Mission

Build the missing upstream economic-intelligence layer:

WORLD DATA
→ ORACLES
→ OBSERVATIONS
→ SIGNALS
→ TOPICS
→ OPPORTUNITIES
→ SOLUTION LAB
→ FACTORY RESOLVER
→ FACTORY GENESIS
→ PRODUCT FACTORIES
→ OUTCOMES

## Preserve repo doctrine

Follow the repo's AGENTS.md and CODING-AGENT.md.
Nothing in Markdown is evidence.
No synthetic data as evidence.
All runs are logged and content-addressed.

## Critical architecture

1. Unignorant is an Oracle Provider, not a factory.
2. Research prose is not evidence.
3. Connector failure is UNKNOWN/DEGRADED, never zero.
4. Source families are explicit.
5. Opportunity != solution.
6. Factory != product archetype.
7. New factories require Factory Genesis hard gates.
8. Market scores always include confidence + coverage + evidence IDs.
9. Cross-oracle joins cannot claim causality.
10. Evolution cannot modify provenance/safety/truth invariants.

## Implement in checkpoint order

Use `26_IMPLEMENTATION_PLAN.md` and `tasks.json`.

## First adapters

Must implement/test these first:
- OpenRouter
- OpenAlex
- ecosyste.ms
- Hacker News
- Unignorant

Then:
- Hugging Face
- MCP Registry
- Cloudflare Radar
- Google Trends official API if available
- PyTrends fallback only

## Required proof

Before claiming complete, conduct a real end-to-end run:

1. ingest live observations from >=5 Oracle adapters;
2. derive signals;
3. find >=1 MarketTopic using Topic Discovery v1;
4. independently audit it;
5. derive >=1 Opportunity;
6. generate >=3 different SolutionHypotheses;
7. run VOI to choose next research;
8. compute FactoryFit against current factories;
9. route to existing/extend OR produce FactoryProposal;
10. if FactoryProposal, prove every Genesis hard gate with evidence;
11. store all artifacts and hashes;
12. expose result through REST and MCP;
13. external Hermes agent must reproduce the evidence chain.

## Do not fake Factory Genesis

If real data does not justify a new factory, the correct output is:
NO_FACTORY.

The system must prove it can say no.

## Final report

Create a machine-readable run bundle and `MARKET-INTELLIGENCE-FINAL.md` containing:
- source health
- source manifests
- observations count by source family
- signal results
- topic results
- opportunities
- rejected opportunities
- VOI decisions
- FactoryFit results
- Factory Genesis results
- test results
- live external-agent test
- known limitations
- exact Git SHA
- GO/NO-GO
