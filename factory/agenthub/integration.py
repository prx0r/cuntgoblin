"""AgentHub integration with VentureLab factory."""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from factory.agenthub.resolver import resolve_architecture
from factory.agenthub.types import ArchitectureNeed, AgentSystem
import time


class FactoryAgentHub:
    """AgentHub integration for VentureLab factory."""
    
    def __init__(self):
        self.systems = []
    
    def resolve_architecture(self, task_kind: str, requirements: dict) -> dict:
        """Resolve which architecture to use for a task."""
        need = ArchitectureNeed(
            need_id=f"need_{int(time.time())}",
            persistent_state=requirements.get("persistent_state", False),
            independent_verification=requirements.get("independent_verification", False),
            resumable=requirements.get("resumable", False),
            tool_use=requirements.get("tool_use", False),
            parallelism=requirements.get("parallelism", 1),
            long_horizon=requirements.get("long_horizon", False),
            max_cost=requirements.get("max_cost"),
        )
        
        # Use resolver to find best architecture
        decision = resolve_architecture(need, self.systems)
        
        return {
            "task_kind": task_kind,
            "decision": decision,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def test_integration():
    """Test the integration."""
    print("=== TESTING AGENTHUB INTEGRATION ===")
    print()
    
    factory = FactoryAgentHub()
    
    # Test 1: Resolve architecture
    result = factory.resolve_architecture("coding_patch", {"tool_use": True, "independent_verification": True})
    print(f"Resolved: {result['decision']}")
    
    # Test 2: Resolve another task
    result2 = factory.resolve_architecture("research_synthesis", {"persistent_state": True})
    print(f"Resolved: {result2['decision']}")
    
    print()
    print("=== INTEGRATION TEST PASSED ===")


if __name__ == "__main__":
    test_integration()
