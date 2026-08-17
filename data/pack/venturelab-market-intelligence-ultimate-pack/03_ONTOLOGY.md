# Canonical Ontology

## Oracle

A machine-readable provider of observations.

Examples:

- `oracle:ai-market`
- `oracle:unignorant`
- `oracle:research`
- `oracle:labour-uk`

An Oracle is NOT a factory.

## Observation

A source-grounded statement of something observed.

Example:

```json
{
  "entity": "technology:mcp",
  "metric": "registry.new_servers",
  "value": 31,
  "period": "2026-W33"
}
```

Observations do not say "MCP is booming." That is a derived Signal.

## Signal

A method-versioned transformation over observations.

Examples:

- 30-day velocity
- 7d/30d acceleration
- burst z-score
- research velocity
- supply contraction
- policy support
- pain frequency

## MarketTopic

A normalized subject around which signals cluster.

Can be:

- technology
- product category
- industry
- occupation
- geography
- regulation/policy
- customer problem

## Opportunity

An evidence-backed unmet condition.

Not yet a solution.

Example:

> Demand for X is rising while qualified supply in Y is falling and a public
> subsidy lowers acquisition/training cost.

## SolutionHypothesis

A possible economic response.

Example:
- training discovery API
- contractor marketplace
- subsidy eligibility tool
- agentic lead generator

One Opportunity can generate many solutions.

## Factory

A repeatable search/build strategy for a CLASS of opportunities.

A Factory has:
- versioned vision
- market scope
- allowed solution/product archetypes
- source preferences
- scoring policy
- completion metrics

## ProductArchetype

Packaging/build form:
- API/MCP
- benchmark
- agent system
- dataset
- registry
- library
- information system
- SaaS

## Product

A concrete built/deployed artifact.

## Pattern

Reusable architecture/process learned by one product/factory and reusable by others.

## Outcome

Real-world result:
- usage
- repeat use
- revenue
- conversion
- stars/forks
- API calls
- uptime
- defects
- maintenance burden
- benchmark performance

## Relationships

```text
Oracle PRODUCES Observation
Observation SUPPORTS Signal
Signal DESCRIBES MarketTopic
MarketTopic SUPPORTS Opportunity
Opportunity GENERATES SolutionHypothesis
SolutionHypothesis ROUTED_TO Factory
Factory USES ProductArchetype
Factory PRODUCES Product
Product DISCOVERS Pattern
Product PRODUCES Outcome
Outcome UPDATES MarketTopic
Outcome UPDATES Factory
Pattern ADOPTED_BY Factory
```
