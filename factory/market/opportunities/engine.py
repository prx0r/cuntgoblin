"""Opportunity Engine - mines opportunities from market signals."""

from typing import List, Dict, Any
from datetime import datetime, timezone


class OpportunityMiner:
    """Mine opportunities from market signals."""
    
    def mine(self, signals: Dict[str, Any], topics: List[Dict]) -> List[Dict]:
        """Mine opportunities from signals and topics."""
        opportunities = []
        
        # Pain × Growth × Undersupply
        for topic in topics:
            if topic.get("count", 0) > 5 and topic.get("source_breadth", 0) > 0.5:
                opportunities.append({
                    "type": "pain_growth_undersupply",
                    "topic": topic["keyword"],
                    "evidence": f"High count ({topic['count']}) with broad sources ({len(topic['sources'])})",
                    "confidence": 0.7,
                })
        
        # Supply-Demand mismatch
        for topic in topics:
            if topic.get("count", 0) > 3 and topic.get("source_breadth", 0) < 0.3:
                opportunities.append({
                    "type": "supply_demand_mismatch",
                    "topic": topic["keyword"],
                    "evidence": f"High count ({topic['count']}) but narrow sources ({len(topic['sources'])})",
                    "confidence": 0.6,
                })
        
        return opportunities


class OpportunityScorer:
    """Score opportunities based on evidence."""
    
    def score(self, opportunity: Dict) -> float:
        """Score an opportunity."""
        base_score = opportunity.get("confidence", 0.5)
        
        # Boost for strong evidence
        if opportunity.get("type") == "pain_growth_undersupply":
            base_score *= 1.2
        
        return min(base_score, 1.0)
