#!/usr/bin/env python3
"""Deterministic scoring with evidence.

Every score MUST have evidence attached.
No guessing allowed.
"""

import json
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/venturelab.db")


def search_github(query, max_results=10):
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


def search_arxiv(query, max_results=10):
    """Search arxiv for papers."""
    import urllib.parse
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


def score_novelty(idea_text):
    """Score novelty based on GitHub repos."""
    github_results = search_github(idea_text)
    
    # Filter out errors
    valid_results = [r for r in github_results if "error" not in r]
    repo_count = len(valid_results)
    
    # Score based on evidence
    if repo_count == 0:
        score = 10
        evidence = f"GitHub search for '{idea_text}' returned 0 results"
    elif repo_count == 1:
        score = 7
        evidence = f"GitHub search found 1 similar repo"
    elif repo_count <= 3:
        score = 5
        evidence = f"GitHub search found {repo_count} similar repos"
    elif repo_count <= 5:
        score = 3
        evidence = f"GitHub search found {repo_count} similar repos"
    else:
        score = 1
        evidence = f"GitHub search found {repo_count} similar repos (many competitors)"
    
    return {
        "factor": "novelty",
        "score": score,
        "evidence": evidence,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "method": "github_search",
        "repo_count": repo_count,
        "repos": valid_results[:5],
    }


def score_research(idea_text):
    """Score research based on arxiv papers."""
    arxiv_results = search_arxiv(idea_text)
    
    # Filter out errors
    valid_results = [r for r in arxiv_results if "error" not in r]
    paper_count = len(valid_results)
    
    # Score based on evidence
    if paper_count == 0:
        score = 2
        evidence = f"arxiv search for '{idea_text}' returned 0 papers"
    elif paper_count <= 2:
        score = 4
        evidence = f"arxiv search found {paper_count} papers"
    elif paper_count <= 5:
        score = 6
        evidence = f"arxiv search found {paper_count} papers"
    elif paper_count <= 10:
        score = 8
        evidence = f"arxiv search found {paper_count} papers"
    else:
        score = 10
        evidence = f"arxiv search found {paper_count} papers (extensive research)"
    
    return {
        "factor": "research",
        "score": score,
        "evidence": evidence,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "method": "arxiv_search",
        "paper_count": paper_count,
        "papers": valid_results[:5],
    }


def score_feasibility(idea_text):
    """Score feasibility based on similar projects."""
    github_results = search_github(idea_text)
    
    # Filter out errors
    valid_results = [r for r in github_results if "error" not in r]
    repo_count = len(valid_results)
    
    # Check if similar projects exist
    if repo_count >= 3:
        score = 8
        evidence = f"Found {repo_count} similar projects on GitHub - feasible"
    elif repo_count >= 1:
        score = 7
        evidence = f"Found {repo_count} similar project - likely feasible"
    else:
        score = 5
        evidence = "No similar projects found - uncertain feasibility"
    
    return {
        "factor": "feasibility",
        "score": score,
        "evidence": evidence,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "method": "github_analysis",
        "repo_count": repo_count,
    }


def score_all(idea_text):
    """Score all factors for an idea."""
    novelty = score_novelty(idea_text)
    research = score_research(idea_text)
    feasibility = score_feasibility(idea_text)
    
    # Calculate overall
    overall = (novelty["score"] + research["score"] + feasibility["score"]) / 3
    
    return {
        "idea": idea_text,
        "scores": {
            "novelty": novelty,
            "research": research,
            "feasibility": feasibility,
        },
        "overall": round(overall, 2),
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
    else:
        idea = "brainwave MCP server"
    
    result = score_all(idea)
    print(json.dumps(result, indent=2))
