# Global Market / Opportunity Graph

## Nodes

- MarketTopic
- Company
- Product
- Project/Repo
- Model
- Agent
- MCP Server
- Paper
- Technology
- Occupation
- Industry
- Geography
- Policy
- Dataset
- CustomerProblem
- Factory
- ProductBuild
- Pattern

## Edges

- competes_with
- depends_on
- implements
- uses
- replaces
- adopted_by
- solves
- complains_about
- funded_by
- regulated_by
- subsidized_by
- imported_by
- exported_by
- employed_in
- trained_by
- growing_in
- declining_in
- produced_by_factory
- derived_from_opportunity
- shares_pattern

## Graph rule

Edges from LLM extraction are `PROPOSED` until backed by observation/evidence.

## Opportunity query examples

```text
find topics where:
research_velocity high
AND implementation edges sparse

find occupations where:
training edges declining
AND wage pressure rising
AND policy support active

find agent products where:
usage rising
AND reliability complaints rising
AND current tooling sparse
```
