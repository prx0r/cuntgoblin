"""Deterministic scoring engine with evidence."""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.score import ScoreDimension, Scorecard


def search_github(query: str, max_results: int = 10) -> List[Dict]:
    """Search GitHub for similar repos."""
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&per_page={max_results}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        return [
            {
                "name": item.get("full_name", ""),
                "stars": item.get("stargazers_count", 0),
                "description": item.get("description", "")[:100],
            }
            for item in data.get("items", [])[:max_results]
        ]
    except Exception as e:
        return [{"error": str(e)}]


def search_arxiv(query: str, max_results: int = 10) -> List[Dict]:
    """Search arxiv for papers."""
    encoded_query = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results={max_results}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        content = resp.read().decode()
        results = []
        entries = content.split("<entry>")[1:]
        for entry in entries[:max_results]:
            title = entry.split("<title>")[1].split("</title>")[0] if "<title>" in entry else ""
            results.append({"title": title.strip()})
        return results
    except Exception as e:
        return [{"error": str(e)}]


class ScoringEngine:
    """Deterministic scoring engine."""
    
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
    
    def score_idea(self, idea_id: str, idea_text: str) -> Scorecard:
        """Score an idea with evidence."""
        # GitHub search
        github = search_github(idea_text)
        repo_count = len([r for r in github if "error" not in r])
        
        # arxiv search
        arxiv = search_arxiv(idea_text)
        paper_count = len([r for r in arxiv if "error" not in r])
        
        dimensions = []
        
        # Novelty
        if repo_count == 0:
            novelty_score = 1.0
            novelty_evidence = ["No similar repos on GitHub"]
        elif repo_count == 1:
            novelty_score = 0.7
            novelty_evidence = [f"1 similar repo on GitHub"]
        elif repo_count <= 3:
            novelty_score = 0.5
            novelty_evidence = [f"{repo_count} similar repos on GitHub"]
        elif repo_count <= 5:
            novelty_score = 0.3
            novelty_evidence = [f"{repo_count} similar repos on GitHub"]
        else:
            novelty_score = 0.1
            novelty_evidence = [f"{repo_count} similar repos (many competitors)"]
        
        dimensions.append(ScoreDimension(
            name="novelty",
            weight=0.15,
            score=novelty_score,
            confidence=0.9,
            evidence=novelty_evidence,
            method="github_search",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Research
        if paper_count == 0:
            research_score = 0.2
            research_evidence = ["No papers on arxiv"]
        elif paper_count <= 2:
            research_score = 0.4
            research_evidence = [f"{paper_count} papers on arxiv"]
        elif paper_count <= 5:
            research_score = 0.6
            research_evidence = [f"{paper_count} papers on arxiv"]
        elif paper_count <= 10:
            research_score = 0.8
            research_evidence = [f"{paper_count} papers on arxiv"]
        else:
            research_score = 1.0
            research_evidence = [f"{paper_count} papers on arxiv (extensive)"]
        
        dimensions.append(ScoreDimension(
            name="research",
            weight=0.10,
            score=research_score,
            confidence=0.9,
            evidence=research_evidence,
            method="arxiv_search",
            checked_at=datetime.now(timezone.utc).isoformat(),
        ))
        
        # Feasibility
        if repo_count >= 3:
            feasibility_score = 0.8
            feasibility_evidence = [f"{repo_count} similar projects exist"]
        elif repo_count >= 1:
            feasibility_score = 0.7
            feasibility_evidence = [f"{repo_count} similar project exists"]
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
        
        # For other dimensions, use placeholder scores
        # In production, these would come from actual research
        for dim in self.DIMENSIONS[3:]:
            dimensions.append(ScoreDimension(
                name=dim["name"],
                weight=dim["weight"],
                score=0.5,  # Default score
                confidence=0.5,
                evidence=["Requires manual research"],
                method="placeholder",
                checked_at=datetime.now(timezone.utc).isoformat(),
            ))
        
        # Create scorecard
        scorecard = Scorecard(
            idea_id=idea_id,
            dimensions=dimensions,
        )
        scorecard.calculate_overall()
        
        return scorecard
