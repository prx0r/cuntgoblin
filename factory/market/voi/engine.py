"""Value of Information Engine - determines next research action."""

from typing import List, Dict, Any


class VOIEngine:
    """Value of Information engine."""
    
    def compute_voi(self, uncertainty: Dict[str, float], action_costs: Dict[str, float]) -> str:
        """Compute value of information for next research action."""
        best_action = None
        best_voi = -1
        
        for action, cost in action_costs.items():
            # VOI = expected information gain / cost
            info_gain = uncertainty.get(action, 0.5)
            voi = info_gain / max(cost, 0.001)
            
            if voi > best_voi:
                best_voi = voi
                best_action = action
        
        return best_action
    
    def decompose_uncertainty(self, research_state: Dict) -> Dict[str, float]:
        """Decompose uncertainty into components."""
        return {
            "market_size": research_state.get("market_size_uncertainty", 0.5),
            "competition": research_state.get("competition_uncertainty", 0.5),
            "technical_feasibility": research_state.get("feasibility_uncertainty", 0.5),
            "customer_demand": research_state.get("demand_uncertainty", 0.5),
        }
