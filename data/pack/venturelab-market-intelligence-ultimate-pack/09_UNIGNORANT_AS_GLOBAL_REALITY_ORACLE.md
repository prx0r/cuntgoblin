# Unignorant Integration

## Classification

`prx0r/unignorant` should become:

```yaml
id: oracle:global-reality
runtime: python
interfaces:
  rest: true
  mcp: true
domains:
  - development
  - trade
  - cost_of_living
  - aid
  - humanitarian
  - household_reality
  - local_information
  - geopolitics
  - attitudes
  - food
  - exchange_rates
```

It currently aggregates many country/global data sources behind REST/MCP.

## Integration principle

Do not flatten all Unignorant outputs into one source family.

For each returned datum preserve upstream origin:

```text
unignorant/worldbank
unignorant/owid
unignorant/comtrade
unignorant/iati
...
```

Otherwise "two Unignorant endpoints" may falsely look like independent evidence.

## Adapter

Create:

`factory/oracles/unignorant.py`

It should use MCP if the factory is Hermes-native, with REST fallback.

Read operations useful to Market Intelligence:

- `country_indicators`
- `country_graph`
- `trajectory`
- `trade_flow`
- `data360_search`
- `owid_search`
- `owid_data`
- `cost_of_living`
- `aid_spending`
- `humanitarian_reports`
- `provenance`

## New opportunity-oriented projection

Do not mutate Unignorant's core vision.

Add a separate Market Intelligence adapter that derives normalized observations like:

```text
geo.trade.import_dependency
geo.cost.food_pressure
geo.population.working_age_change
geo.infrastructure.electricity_access_change
geo.training.participation_change
geo.aid.flow_change
```

Each remains linked to original Unignorant provenance.

## Cross-country mining

Useful patterns:

- same structural problem, different solution coverage;
- policy divergence;
- price/wage divergence;
- trade exposure;
- infrastructure adoption;
- demographic changes.

## Important

"Most suffering" and moral-priority scores should not automatically become
commercial opportunity scores.

Keep:
- humanitarian priority
- commercial opportunity
as separate objectives.

A product may score high on social value and low on monetization; preserve that.
