# Global Budget Manager

HotSwap optimizes one task.
Global Manager allocates scarce money/compute across all tasks.

Budgets:
- daily total paid LLM
- per factory
- per product
- per workflow run
- per task
- premium free-quota reserve

Before execution, reserve estimated paid cost.
After execution, reconcile actual cost.

Parallel tasks cannot all spend the same remaining balance.

Budget states:
- HEALTHY
- TIGHT
- EXHAUSTED

When TIGHT:
- pause low-value paid exploration;
- continue free-qualified bulk work;
- preserve reserved verification/release capacity.

When EXHAUSTED:
- no hidden paid overdraft.
