from __future__ import annotations
from typing import Any

from factory.hotswap.router import HotSwapRouter
from factory.hotswap.types import Route, TaskSpec

class VentureLabSystem:
    """Minimal replacement shape for the missing composition root.

    Production should inject store/scheduler/artifacts/Hermes/verifiers/
    factory registry rather than constructing everything here.
    """
    def __init__(
        self,
        *,
        router: HotSwapRouter | None = None,
        routes: list[Route] | None = None,
    ):
        self.router = router or HotSwapRouter()
        self.routes = routes or []

    def route_task(
        self, task_kind: str, requirements: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        r = requirements or {}
        task = TaskSpec(
            task_id=r.get("task_id", "preview"),
            task_kind=task_kind,
            difficulty=r.get("difficulty", "medium"),
            criticality=r.get("criticality", "routine"),
            quality_floor=float(r.get("quality", .70)),
            free_policy=r.get("free_policy", "prefer"),
            paid_allowed=bool(r.get("paid_allowed", True)),
            tools_required=bool(r.get("tools_required", False)),
            json_required=bool(r.get("json_required", False)),
            context_tokens_min=int(r.get("context_tokens_min", 0)),
            estimated_input_tokens=int(r.get("estimated_input_tokens", 1000)),
            estimated_output_tokens=int(r.get("estimated_output_tokens", 500)),
            task_budget_usd=r.get("budget_usd"),
        )
        plan = self.router.plan(task, self.routes)

        def c(x):
            if x is None:
                return None
            return {
                "route_id": x.route.route_id,
                "model_id": x.route.model_id,
                "provider_id": x.route.provider_id,
                "p_success": x.p_success,
                "p_lower": x.p_lower,
                "expected_completion_cost": x.expected_completion_cost,
            }

        return {
            "task_id": task.task_id,
            "primary": c(plan.primary),
            "fallbacks": [c(x) for x in plan.fallbacks],
            "excluded": plan.excluded,
            "reason_codes": plan.reason_codes,
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "service": "venturelab",
            "ready": True,
            "route_count": len(self.routes),
        }
