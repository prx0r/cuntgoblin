# Worked Example — Trades / Training / Subsidy Opportunity

This is an illustrative pipeline showing how the system should reason.
It is NOT evidence that a specific UK trade shortage/subsidy opportunity currently exists.
The agent must fetch current official observations.

## Step 1 — Labour Oracle

Possible official observations:
- employment by occupation
- vacancies if available
- earnings by occupation
- age profile
- workforce change

Normalize to:

```text
occupation_supply_velocity
earnings_pressure
vacancy_pressure
retirement_risk
```

## Step 2 — Training Oracle

Use official education/apprenticeship datasets.

Normalize:

```text
apprenticeship_starts
apprenticeship_achievements
subject_route
regional_training_supply
training_velocity
```

## Step 3 — Policy Oracle

Primary-source-only:
- funding rules
- apprenticeship funding
- skills programs
- grants/subsidies

Normalize:

```text
policy_support.active
policy_support.amount_or_scope
eligibility_complexity
policy_expiry
```

## Step 4 — Join

Rule:

```text
occupation supply ↓
AND wage/vacancy pressure ↑
AND training supply insufficient
AND policy support active
```

## Step 5 — Opportunity, not solution

Output:

> There may be a persistent friction between workforce demand, entrant supply
> and access to subsidized training in [occupation/geography].

## Step 6 — Solution Lab

Generate multiple hypotheses:

1. subsidy eligibility / discovery API
2. local apprenticeship/training matcher
3. employer lead intelligence
4. contractor productivity agent
5. training-provider demand forecast
6. procurement/workforce planning data product

## Step 7 — Score separately

Do NOT jump from shortage directly to "build marketplace".

Each solution gets:
- buyer
- pain
- existing competitors
- distribution
- willingness-to-pay evidence
- buildability
- maintenance burden
- data moat

## Step 8 — Cheapest falsification

Example:
- create a data-only regional shortage/subsidy report;
- expose a small API;
- recruit a handful of real users/businesses;
- measure repeated queries/signups;
- only then promote.

This pattern generalizes to hundreds of country/sector combinations.
