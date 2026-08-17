"""Cross-Oracle Join Lab - finds connections between different oracles."""

from typing import List, Dict, Any


class JoinEngine:
    """Engine for cross-oracle joins."""
    
    # Semantic rule templates
    RULE_TEMPLATES = [
        "SHORTAGE + POLICY_SUPPORT",
        "IMPORT_DEPENDENCY + DOMESTIC_SUPPORT",
        "DEMAND + LOW_DIGITAL_SUPPLY",
        "RESEARCH + IMPLEMENTATION_LAG",
        "REGULATION + TOOL_GAP",
        "AGING_SUPPLY + TRAINING_DECLINE",
    ]
    
    def find_joins(self, oracle_a_data: Dict, oracle_b_data: Dict) -> List[Dict]:
        """Find joins between two oracles."""
        joins = []
        
        # Simple keyword matching for now
        keywords_a = set(self._extract_keywords(oracle_a_data))
        keywords_b = set(self._extract_keywords(oracle_b_data))
        
        overlap = keywords_a & keywords_b
        
        if overlap:
            joins.append({
                "type": "keyword_overlap",
                "keywords": list(overlap),
                "confidence": len(overlap) / max(len(keywords_a), len(keywords_b), 1),
            })
        
        return joins
    
    def _extract_keywords(self, data: Dict) -> List[str]:
        """Extract keywords from data."""
        keywords = []
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 3:
                keywords.append(value.lower())
        return keywords
    
    def validate_join(self, join: Dict) -> bool:
        """Validate a join (anti-spurious gates)."""
        # Check semantic plausibility
        if join.get("confidence", 0) < 0.3:
            return False
        
        # Check source diversity
        if len(join.get("sources", [])) < 2:
            return False
        
        return True
