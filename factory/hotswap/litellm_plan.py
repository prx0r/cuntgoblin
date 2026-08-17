from __future__ import annotations
from .types import ExecutionPlan


def to_litellm_request(plan: ExecutionPlan, task_metadata: dict) -> dict:
    if plan.primary is None:
        raise ValueError("no primary route")
    r = plan.primary.route
    return {
        "model": f"route/{r.route_id}",
        "metadata": {
            **task_metadata,
            "hotswap_route_id": r.route_id,
            "hotswap_task_id": plan.task_id,
        },
    }


def hotswap_fallback_model_names(plan: ExecutionPlan) -> list[str]:
    return [f"route/{x.route.route_id}" for x in plan.fallbacks]
