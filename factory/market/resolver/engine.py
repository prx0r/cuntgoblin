"""Factory Resolver - decides whether to use existing, extend, or genesis new factory."""

from typing import List, Dict, Any, Tuple


class FactoryResolver:
    """Resolver for factory decisions."""
    
    def resolve(self, opportunity: Dict, existing_factories: List[Dict]) -> Tuple[str, Dict]:
        """Resolve which factory to use."""
        # Compute FactoryFit for each existing factory
        for factory in existing_factories:
            fit = self.compute_factory_fit(opportunity, factory)
            if fit >= 0.75:
                return "USE_EXISTING", {"factory": factory["id"], "fit": fit}
        
        # Check for extension
        for factory in existing_factories:
            fit = self.compute_factory_fit(opportunity, factory)
            if fit >= 0.60:
                return "EXTEND", {"factory": factory["id"], "fit": fit}
        
        # Check for genesis
        genesis_score = self.compute_genesis_score(opportunity)
        if genesis_score >= 0.72:
            return "SPAWN_CANDIDATE", {"score": genesis_score}
        elif genesis_score >= 0.58:
            return "FACTORY_EXPERIMENT", {"score": genesis_score}
        else:
            return "NO_FACTORY", {"score": genesis_score}
    
    def compute_factory_fit(self, opportunity: Dict, factory: Dict) -> float:
        """Compute how well an opportunity fits a factory."""
        # Simple fit calculation
        opp_type = opportunity.get("type", "")
        factory_types = factory.get("allowed_types", [])
        
        if opp_type in factory_types:
            return 0.8
        return 0.4
    
    def compute_genesis_score(self, opportunity: Dict) -> float:
        """Compute genesis score for new factory."""
        # Simple genesis scoring
        return 0.5
