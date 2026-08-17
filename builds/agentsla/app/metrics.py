"""app/metrics.py — SLA metrics per spec (section 'Metrics').

Core:  success_rate, cost_per_attempt, cost_per_success, duration_per_success,
       tokens_per_success, tool_calls_per_success, retry_rate
Derived: efficiency = success_probability / expected_cost

All metrics are computed solely from rows in the runs/model_calls/cost_events
tables. No LLM anywhere. Sample counts are always surfaced so nobody can read
"80%" as fact from 4/5.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

_WILSON_Z = 1.959963984540054  # 95% two-sided normal quantile


def wilson_lower_bound(successes: int, trials: int, z: float = _WILSON_Z) -> float:
    """Wilson score lower bound for a binomial proportion. 0 if trials == 0.

    Core truthfulness guard: never claim 90% from 9/10.
    """
    if trials <= 0:
        return 0.0
    p = successes / trials
    denom = 1 + z * z / trials
    centre = p + z * z / (2 * trials)
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * trials)) / trials)
    return max(0.0, (centre - margin) / denom)


def wilson_interval(successes: int, trials: int) -> tuple[float, float]:
    if trials <= 0:
        return (0.0, 0.0)
    p = successes / trials
    denom = 1 + _WILSON_Z * _WILSON_Z / trials
    centre = p + _WILSON_Z * _WILSON_Z / (2 * trials)
    margin = _WILSON_Z * math.sqrt((p * (1 - p) + _WILSON_Z * _WILSON_Z / (4 * trials)) / trials)
    return (max(0.0, (centre - margin) / denom), min(1.0, (centre + margin) / denom))


@dataclass
class _RunRow:
    success: bool
    cost_usd: float
    duration_seconds: float
    input_tokens: int
    output_tokens: int
    tool_calls: int
    retries: int


@dataclass
class Slasummary:
    n: int
    successes: int
    success_rate: float
    success_rate_ci: tuple[float, float]  # wilson 95%
    cost_per_attempt: float
    cost_per_success: float
    duration_per_success: float
    tokens_per_success: float
    tool_calls_per_success: float
    retry_rate: float
    total_cost_usd: float
    efficiency: float  # success_probability / expected_cost
    basis: str = "price_table_estimate"
    insufficient_evidence: bool = field(default=False)


def _denominator(n_successes: int, n_attempts: int, per_success: bool, per_attempt: bool) -> int:
    """Helper that keeps the denominator logic legible: a per-success metric is
    undefined (0) when no successes exist, and 0 when no attempts exist."""
    if per_success:
        return n_successes
    if per_attempt:
        return n_attempts
    return n_attempts


def sla_summary(runs: list[_RunRow], min_samples: int = 3) -> Slasummary:
    """Aggregate a list of run rows into an SLA summary.

    min_samples: the minimum number of runs before success_rate is treated as
    a usable estimate. Below it, insufficient_evidence=True so downstream
    consumers (Knee, ArchOracle) must NOT act on the success rate."""
    n = len(runs)
    if n == 0:
        return Slasummary(
            n=0, successes=0, success_rate=0.0, success_rate_ci=(0.0, 0.0),
            cost_per_attempt=0.0, cost_per_success=0.0, duration_per_success=0.0,
            tokens_per_success=0.0, tool_calls_per_success=0.0, retry_rate=0.0,
            total_cost_usd=0.0, efficiency=0.0, insufficient_evidence=True,
        )
    successes = sum(1 for r in runs if r.success)
    total_cost = sum(r.cost_usd for r in runs)
    total_retries = sum(r.retries for r in runs)
    succ_runs = [r for r in runs if r.success]

    success_rate = successes / n
    ci = wilson_interval(successes, n)
    state = Slasummary(
        n=n,
        successes=successes,
        success_rate=success_rate,
        success_rate_ci=ci,
        cost_per_attempt=total_cost / n,
        cost_per_success=(total_cost / successes) if successes else 0.0,
        duration_per_success=(sum(r.duration_seconds for r in succ_runs) / successes) if successes else 0.0,
        tokens_per_success=(sum(r.input_tokens + r.output_tokens for r in succ_runs) / successes) if successes else 0.0,
        tool_calls_per_success=(sum(r.tool_calls for r in succ_runs) / successes) if successes else 0.0,
        retry_rate=total_retries / n,
        total_cost_usd=total_cost,
        efficiency=(success_rate / total_cost) if total_cost > 0 else 0.0,
        insufficient_evidence=n < min_samples,
    )
    return state


def knee_from_runs(
    grouped: list[tuple[str, Slasummary]],
    min_success: float,
    min_samples: int = 3,
) -> dict:
    """Spec (Product 3) eligibility rule, applied to AgentSLA data:

    1. Drop candidates below min sample count.
    2. Keep only candidates whose WILSON LOWER BOUND >= min_success.
    3. Sort ascending cost; the first valid one is the recommendation.
    4. Report the cheaper neighbor's success drop.

    Returns:
      {"status": "OK", "recommended": {...}, "quality_cliff": {...}}
      or {"status": "INSUFFICIENT_EVIDENCE", "candidates": [...]}
      or {"status": "NO_QUALIFYING", "nearest": {...}}
    """
    eligible = [(aid, s) for aid, s in grouped if not s.insufficient_evidence]
    qualifying = [
        (aid, s) for aid, s in eligible
        if wilson_lower_bound(s.successes, s.n) >= min_success
    ]
    qualifying.sort(key=lambda x: x[1].cost_per_attempt)
    result = {
        "status": "OK" if qualifying else "NO_QUALIFYING",
        "min_success": min_success,
        "candidates": [
            {
                "architecture_id": aid,
                "n": s.n,
                "successes": s.successes,
                "success_rate": s.success_rate,
                "wilson_lb": wilson_lower_bound(s.successes, s.n),
                "cost_per_attempt_usd": s.cost_per_attempt,
            }
            for aid, s in sorted(grouped, key=lambda x: x[1].cost_per_attempt)
        ],
    }
    if qualifying:
        rec_id, rec = qualifying[0]
        result["recommended"] = {
            "architecture_id": rec_id,
            "expected_success": rec.success_rate,
            "wilson_lb": wilson_lower_bound(rec.successes, rec.n),
            "expected_cost_usd": rec.cost_per_attempt,
            "n": rec.n,
        }
        cheaper = [(aid, s) for aid, s in eligible if s.cost_per_attempt < rec.cost_per_attempt]
        if cheaper:
            cheaper.sort(key=lambda x: -x[1].cost_per_attempt)
            c_id, c = cheaper[0]
            result["quality_cliff"] = {
                "next_cheaper": {
                    "architecture_id": c_id,
                    "expected_cost_usd": c.cost_per_attempt,
                    "expected_success": c.success_rate,
                    "wilson_lb": wilson_lower_bound(c.successes, c.n),
                    "n": c.n,
                },
                "success_drop": rec.success_rate - c.success_rate,
            }
    return result