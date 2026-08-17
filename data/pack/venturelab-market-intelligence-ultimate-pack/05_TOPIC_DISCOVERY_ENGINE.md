# Topic Discovery Engine

## The actual question

Before the factory has ideas, how does it decide what deserves investigation?

Use a **multi-generator candidate pool**.

No single trending endpoint gets to decide.

## Candidate generators

### G1 — Behavioral-growth seeds

From:
- OpenRouter app/model usage
- internal product telemetry
- MCP use counts when reliable

Seed a topic when:
- short-window usage growth > cohort 75th percentile; OR
- growth acceleration > cohort 80th percentile; OR
- change-point detector fires.

### G2 — Developer-adoption seeds

From:
- package/dependency activity
- GitHub/ecosyste.ms
- Hugging Face
- MCP registry

Seed when:
- dependent projects rising;
- release/contributor activity rising;
- multiple new serious implementations emerge.

### G3 — Research-frontier seeds

From OpenAlex + recent arXiv.

Seed when:
- paper count velocity high;
- citations/works breadth increases;
- institutions entering topic increases;
- research growth materially exceeds implementation adoption.

### G4 — Pain seeds

From:
- GitHub issues
- HN discussions
- support/review sources where terms allow

Seed when a coherent complaint/problem cluster has:
- frequency burst;
- high engagement;
- persistence;
- multiple independent communities.

### G5 — Policy/event seeds

Official policy/data sources.

Examples:
- subsidy launched
- funding rules changed
- procurement program opened
- compliance deadline introduced
- tax/credit/incentive changed

A verified policy shock can seed research even without two source families because
the primary source itself is the event.

### G6 — Reality anomaly seeds

From Unignorant/global/national statistics.

Examples:
- occupation supply falling
- wages accelerating
- import dependency increasing
- population cohort changing
- training participation diverging
- cost-of-living pressure
- infrastructure access improving

### G7 — Cross-oracle seeds

Candidate is generated when two seemingly separate source domains create a
predefined economically meaningful relation:

```text
supply↓ + demand↑
shortage↑ + subsidy↑
research↑ + implementations↓
price↑ + cheaper technical substitute appears
trade dependency↑ + domestic policy support↑
aging workforce↑ + training starts↓
public spend↑ + vendor supply low
```

## Per-source normalization

Raw metrics are NOT directly comparable.

For every source metric derive:

- `level_percentile`
- `velocity_percentile`
- `acceleration_percentile`
- `burst_score`
- `change_score`
- `persistence`
- `source_quality`

within its own historical distribution or relevant cohort.

## Robust velocity

Prefer log growth:

```text
g = log(1 + current) - log(1 + baseline)
```

Then convert `g` to percentile within a comparable entity cohort.

Do not use percent growth when the baseline is near zero without a floor.

## Robust burst score

Use median absolute deviation:

```text
median = median(history)
MAD = median(|x - median|)
robust_z = 0.6745 * (x - median) / MAD
```

Map:
- robust_z <= 1 → weak
- 1–2 → notable
- 2–3 → strong
- >3 → extreme

Use as a feature, not proof.

## Acceleration

```text
acceleration =
  short_window_velocity_percentile
  - long_window_velocity_percentile
```

Map [-1,1] to [0,1].

## Change point

Implementation choices:
- simple CUSUM first;
- optional Bayesian online change-point detector later.

The signal means:
`distribution appears to have shifted`,
not:
`market opportunity proven`.

## Source breadth

Count independent source families, not endpoints.

```text
breadth = min(1, independent_source_families / 4)
```

## Persistence

For last N periods:

```text
persistence = periods_above_signal_floor / N
```

Recommended N:
- daily sources: 14 or 30
- weekly: 8
- monthly: 6

## Topic Discovery Score v1

```text
TDS =
  .20 velocity
+ .15 acceleration
+ .15 change_point
+ .15 source_breadth
+ .10 persistence
+ .10 magnitude
+ .10 novelty
+ .05 source_quality
```

Hard requirements:

- at least 2 independent source families, OR one primary policy/event source;
- evidence coverage >= .50;
- no connector error coerced to zero.

Operational initial thresholds:

```text
TDS >= .68 and confidence >= .65 → ACTIVE_RESEARCH
TDS >= .55                     → WATCH
otherwise                      → store but do not spend agent budget
```

These are **starting priors**, not universal truths. Version them and backtest them.

## Research-budget allocation

For top candidates:

```text
priority =
TDS
× decision_relevance
× uncertainty_reducibility
/ expected_research_cost
```

This prevents the system from spending all its time on high-noise trendy subjects.
