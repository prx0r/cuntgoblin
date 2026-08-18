# Hermes Kanban and Cron

## Kanban

Use one board per substantial factory/architecture run:

`vl:<factory_slug>:<run_short_id>`

The manager projects Hermes-executable jobs onto the board.

Manager flow:
1. create global Job;
2. project it to Kanban;
3. worker claims/completes;
4. adapter collects artifacts/evaluator result;
5. manager commits global transition.

Reconciliation detects:
- orphan board tasks;
- global jobs missing board projections;
- state disagreement.

Global ledger wins.

## Cron

Hermes Cron is useful for fresh isolated scheduled sessions and delivery. It should
trigger a named manager workflow rather than directly mutate global business state.

Example:
`Hermes Cron -> POST manager trigger market-cycle -> canonical Run/Job creation`

This prevents separate cron JSON and workflow DB from becoming two authoritative clocks.
