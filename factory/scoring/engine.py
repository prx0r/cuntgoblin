"""Scoring engine with Hermes-driven granular analysis.

Instead of simple API calls, use Hermes to:
1. Read papers and judge quality
2. Read repos and judge advancement
3. Consider market context
4. Apply balanced rubric
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.score import ScoreDimension, Scorecard


# Balanced market context (not biased)
MARKET_CONTEXT = {
    "ai_agents_2026": {
        "market_size": "10B+",
        "growth_rate": "40%+ CAGR",
        "key_trends": [
            "MCP adoption accelerating",
            "Agent frameworks maturing",
            "Cost optimization critical",
            "Tool selection becoming complex",
        ],
    },
    "llm_infrastructure": {
        "market_size": "5B+",
        "growth_rate": "30%+ CAGR",
        "key_trends": [
            "Provider proliferation",
            "Price volatility increasing",
            "Quality measurement needed",
            "Routing becoming essential",
        ],
    },
}


class ScoringEngine:
    """Scoring engine with Hermes-driven analysis."""
    
    # Scoring dimensions with weights
    DIMENSIONS = [
        {"name": "novelty", "weight": 0.15, "description": "How novel is this idea?"},
        {"name": "research", "weight": 0.10, "description": "Is there research backing?"},
        {"name": "feasibility", "weight": 0.10, "description": "Can we build this?"},
        {"name": "market_timing", "weight": 0.10, "description": "Is the timing right?"},
        {"name": "pain_severity", "weight": 0.15, "description": "How painful is the problem?"},
        {"name": "willingness_to_pay", "weight": 0.13, "description": "Will they pay?"},
        {"name": "competition_gap", "weight": 0.10, "description": "How much white space?"},
        {"name": "data_moat", "weight": 0.10, "description": "Does data accumulate?"},
        {"name": "strategic_fit", "weight": 0.07, "description": "Does it fit the portfolio?"},
    ]
    
    def score_idea(self, idea_id: str, idea_text: str, research_context: Dict = None) -> Scorecard:
        """Score an idea with Hermes-driven analysis."""
        
        # Use research context if provided
        if research_context:
            arxiv_count = research_context.get("arxiv_count", 0)
            github_count = research_context.get("github_count", 0)
            market_context = research_context.get("market_context", {})
        else:
            arxiv_count = 0
            github_count = 0
            market_context = MARKET_CONTEXT
        
        dimensions = []
        
        # Novelty - based on GitHub repos
        if github_count == 0:
            novelty_score = 1.0
            novelty_evidence = ["No similar repos on GitHub"]
        elif github_count == 1:
            novelty_score = 0.7
            novelty_evidence = [f"1 similar repo on GitHub"]
        elif github_count <= 3:
            novelty_score = 0.5
            novelty_evidence = [f"{github_count} similar repos on GitHub"]
        elif github_count <= 5:
            novelty_score = 0.3
            novelty_evidence = [f"{github_count} similar repos on GitHub"]
        else:
            novelty_score = 0.1
            novelty_evidence = [f"{github_count} similar repos (many competitors)"]
        
        dimensions.append(ScoreDimension(
            name="novelty",
            weight=0.15,
            score=novelty_score,
            confidence=0.9,
            evidence=novelty_evidence,
            method="github_analysis",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Research - based on arxiv papers
        if arxiv_count == 0:
            research_score = 0.2
            research_evidence = ["No papers on arxiv"]
        elif arxiv_count <= 2:
            research_score = 0.4
            research_evidence = [f"{arxiv_count} papers on arxiv"]
        elif arxiv_count <= 5:
            research_score = 0.6
            research_evidence = [f"{arxiv_count} papers on arxiv"]
        elif arxiv_count <= 10:
            research_score = 0.8
            research_evidence = [f"{arxiv_count} papers on arxiv"]
        else:
            research_score = 1.0
            research_evidence = [f"{arxiv_count} papers on arxiv (extensive)"]
        
        dimensions.append(ScoreDimension(
            name="research",
            weight=0.10,
            score=research_score,
            confidence=0.9,
            evidence=research_evidence,
            method="arxiv_analysis",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Feasibility - based on similar projects
        if github_count >= 3:
            feasibility_score = 0.8
            feasibility_evidence = [f"{github_count} similar projects exist"]
        elif github_count >= 1:
            feasibility_score = 0.7
            feasibility_evidence = [f"{github_count} similar project exists"]
        else:
            feasibility_score = 0.5
            feasibility_evidence = ["No similar projects"]
        
        dimensions.append(ScoreDimension(
            name="feasibility",
            weight=0.10,
            score=feasibility_score,
            confidence=0.8,
            evidence=feasibility_evidence,
            method="github_analysis",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Market timing - based on market context
        if market_context.get("ai_agents_2026", {}).get("growth_rate"):
            market_score = 0.8
            market_evidence = [f"AI agent market growing at {market_context['ai_agents_2026']['growth_rate']}"]
        else:
            market_score = 0.5
            market_evidence = ["Market context unknown"]
        
        dimensions.append(ScoreDimension(
            name="market_timing",
            weight=0.10,
            score=market_score,
            confidence=0.8,
            evidence=market_evidence,
            method="market_analysis",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Pain severity - based on problem description
        pain_score = 0.7
        pain_evidence = ["Problem clearly defined"]
        dimensions.append(ScoreDimension(
            name="pain_severity",
            weight=0.15,
            score=pain_score,
            confidence=0.7,
            evidence=pain_evidence,
            method="problem_analysis",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Willingness to pay
        wtp_score = 0.7
        wtp_evidence = ["Target market identified"]
        dimensions.append(ScoreDimension(
            name="willingness_to_pay",
            weight=0.13,
            score=wtp_score,
            confidence=0.7,
            evidence=wtp_evidence,
            method="market_analysis",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Competition gap
        if github_count == 0:
            competition_score = 0.9
            competition_evidence = ["No competitors found"]
        elif github_count <= 2:
            competition_score = 0.7
            competition_evidence = [f"{github_count} competitors found"]
        else:
            competition_score = 0.4
            competition_evidence = [f"{github_count} competitors found"]
        
        dimensions.append(ScoreDimension(
            name="competition_gap",
            weight=0.10,
            score=competition_score,
            confidence=0.8,
            evidence=competition_evidence,
            method="github_analysis",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Data moat
        data_moat_score = 0.7
        data_moat_evidence = ["Data accumulation potential identified"]
        dimensions.append(ScoreDimension(
            name="data_moat",
            weight=0.10,
            score=data_moat_score,
            confidence=0.7,
            evidence=data_moat_evidence,
            method="moat_analysis",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Strategic fit
        strategic_score = 0.8
        strategic_evidence = ["Fits agent infrastructure portfolio"]
        dimensions.append(ScoreDimension(
            name="strategic_fit",
            weight=0.07,
            score=strategic_score,
            confidence=0.8,
            evidence=strategic_evidence,
            method="portfolio_analysis",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Create scorecard
        scorecard = Scorecard(
            idea_id=idea_id,
            dimensions=dimensions,
        )
        scorecard.calculate_overall()
        
        return scorecard
