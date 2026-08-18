# Benchmark Philosophy

The central research problem is separating:

```text
architecture effect
from
model effect
from
tool/environment effect
```

Therefore AgentHub supports three modes.

## Mode A — Architecture-controlled

Freeze:
- same model/model policy
- same tool set
- same task/environment
- same token/time budget

Vary architecture.

This is the most important mode for architecture research.

## Mode B — Production system

Each architecture may use its intended HotSwap policy.

Measures practical total system value.

## Mode C — Component ablation

Take one architecture and mutate exactly one structural feature:
- verifier on/off
- parallelism 1/4
- persistent memory on/off
- planner on/off
- context compaction on/off

This produces causal-ish controlled mechanism evidence better than arbitrary repo comparison.

## No single global score

Primary output is a metric vector + Pareto frontier.

Leaderboards are suite-specific.

Popularity is separate.
