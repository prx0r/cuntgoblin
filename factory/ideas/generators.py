"""Idea generation with multiple generators."""

from typing import List, Dict, Any
from datetime import datetime, timezone


class GapGenerator:
    """Generate ideas from market gaps."""
    
    def generate(self, market_intelligence) -> List[Dict]:
        ideas = []
        
        # Find problems with weak/no solutions
        claims = market_intelligence.query_claims(predicate="has_problem")
        for claim in claims:
            problem = claim["object"]
            solutions = market_intelligence.query_claims(
                subject=problem, predicate="solved_by"
            )
            
            if len(solutions) < 2:
                ideas.append({
                    "type": "gap",
                    "problem": problem,
                    "existing_solutions": len(solutions),
                    "suggestion": f"Build solution for: {problem}",
                })
        
        return ideas


class ArbitrageGenerator:
    """Generate ideas from price arbitrage."""
    
    def generate(self, market_intelligence) -> List[Dict]:
        ideas = []
        
        # Find expensive services with cheaper alternatives
        prices = market_intelligence.query_claims(predicate="market.price")
        for price_claim in prices:
            service = price_claim["subject"]
            price = price_claim["object"]
            
            # Look for cheaper alternatives
            alternatives = market_intelligence.query_claims(
                subject=service, predicate="has_alternative"
            )
            
            for alt in alternatives:
                alt_price = market_intelligence.query_claims(
                    subject=alt["object"], predicate="market.price"
                )
                if alt_price and alt_price[0]["object"] < price * 0.5:
                    ideas.append({
                        "type": "arbitrage",
                        "expensive_service": service,
                        "cheap_alternative": alt["object"],
                        "savings": f"{(1 - alt_price[0]['object']/price)*100:.0f}%",
                    })
        
        return ideas


class ResearchTransferGenerator:
    """Generate ideas from research transfer."""
    
    def generate(self, market_intelligence) -> List[Dict]:
        ideas = []
        
        # Find new papers with techniques
        papers = market_intelligence.query_claims(predicate="paper.technique")
        for paper in papers:
            technique = paper["object"]
            
            # Look for markets where this could apply
            markets = market_intelligence.query_claims(predicate="market.growth")
            for market in markets:
                if market["object"] == "high":
                    ideas.append({
                        "type": "research_transfer",
                        "technique": technique,
                        "target_market": market["subject"],
                        "suggestion": f"Apply {technique} to {market['subject']}",
                    })
        
        return ideas


class PortfolioCompositionGenerator:
    """Generate ideas from existing products."""
    
    def generate(self, market_intelligence, existing_products: List[str]) -> List[Dict]:
        ideas = []
        
        # Find combinations of existing products
        for i, prod_a in enumerate(existing_products):
            for prod_b in existing_products[i+1:]:
                ideas.append({
                    "type": "portfolio_composition",
                    "product_a": prod_a,
                    "product_b": prod_b,
                    "suggestion": f"Combine {prod_a} and {prod_b}",
                })
        
        return ideas


class IdeaGenerator:
    """Generate ideas using multiple generators."""
    
    def __init__(self):
        self.generators = [
            GapGenerator(),
            ArbitrageGenerator(),
            ResearchTransferGenerator(),
            PortfolioCompositionGenerator(),
        ]
    
    def generate(self, market_intelligence, existing_products: List[str] = None) -> List[Dict]:
        all_ideas = []
        
        for generator in self.generators:
            if isinstance(generator, PortfolioCompositionGenerator):
                ideas = generator.generate(market_intelligence, existing_products or [])
            else:
                ideas = generator.generate(market_intelligence)
            all_ideas.extend(ideas)
        
        return all_ideas
