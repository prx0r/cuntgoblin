from __future__ import annotations
import math
from .types import AssessmentVector


def wilson_lower(successes: int, trials: int, z: float = 1.6448536269514722) -> float:
    if trials <= 0: return 0.0
    p = successes/trials
    denom = 1 + z*z/trials
    centre = p + z*z/(2*trials)
    adj = z*math.sqrt((p*(1-p)+z*z/(4*trials))/trials)
    return max(0.0,(centre-adj)/denom)


def cost_per_success(total_cost: float, successes: int) -> float:
    return float("inf") if successes <= 0 else total_cost/successes


def dominates(a: AssessmentVector, b: AssessmentVector) -> bool:
    no_worse = (
        a.success_lower >= b.success_lower
        and a.cost_per_success <= b.cost_per_success
        and a.wall_time <= b.wall_time
        and a.recovery_rate >= b.recovery_rate
        and a.complexity <= b.complexity
    )
    strict = (
        a.success_lower > b.success_lower
        or a.cost_per_success < b.cost_per_success
        or a.wall_time < b.wall_time
        or a.recovery_rate > b.recovery_rate
        or a.complexity < b.complexity
    )
    return no_worse and strict


def pareto_frontier(items: dict[str,AssessmentVector]) -> list[str]:
    out=[]
    for k,v in items.items():
        if not any(dominates(v2,v) for k2,v2 in items.items() if k2 != k):
            out.append(k)
    return sorted(out)
