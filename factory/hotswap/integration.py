"""HotSwap integration with VentureLab factory."""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from factory.hotswap.types import TaskSpec, Route, ExecutionPlan
from factory.hotswap.router import HotSwapRouter
from factory.hotswap.quota import QuotaLedger
from factory.hotswap.bandit import BanditStore


class FactoryHotSwap:
    """HotSwap integration for VentureLab factory."""
    
    def __init__(self):
        self.router = HotSwapRouter()
        self.quotas = QuotaLedger()
        self.bandits = BanditStore()
    
    def create_task_spec(self, task_kind: str, difficulty: str = "medium") -> TaskSpec:
        """Create a TaskSpec for a factory task."""
        return TaskSpec(
            task_id=f"task_{int(time.time())}",
            task_kind=task_kind,
            difficulty=difficulty,
            criticality="routine",
            quality_floor=0.76,
            free_policy="prefer",
            paid_allowed=True,
            tools_required=True,
        )
    
    def route_task(self, task: TaskSpec, routes: list) -> dict:
        """Route a task to the best model."""
        # Use HotSwap router
        plan = self.router.plan(task, routes)
        
        # Calculate estimated cost
        estimated_cost = 0.0
        if plan.primary:
            estimated_cost = plan.primary.expected_completion_cost
        
        return {
            "task_id": task.task_id,
            "primary_route": plan.primary.route.route_id if plan.primary else None,
            "fallback_routes": [f.route.route_id for f in plan.fallbacks],
            "estimated_cost": estimated_cost,
        }


def test_integration():
    """Test the integration."""
    print("=== TESTING HOTSWAP INTEGRATION ===")
    print()
    
    factory = FactoryHotSwap()
    
    # Create a task
    task = factory.create_task_spec("coding_patch", "medium")
    print(f"Created task: {task.task_id}")
    
    # Create routes
    routes = [
        Route(route_id="free_model", model_id="deepseek-v3", provider_id="provider-x", free=True, prior_success=0.9),
        Route(route_id="paid_model", model_id="gpt-4o", provider_id="openai", free=False, prior_success=0.95),
    ]
    
    # Route task
    result = factory.route_task(task, routes)
    print(f"Routed to: {result['primary_route']}")
    print(f"Estimated cost: ${result['estimated_cost']:.4f}")
    
    print()
    print("=== INTEGRATION TEST PASSED ===")


if __name__ == "__main__":
    test_integration()
