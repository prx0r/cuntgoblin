#!/usr/bin/env python3
"""Score all ideas with evidence.

Replaces hallucinated scores with deterministic scores.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
import urllib.request
import urllib.parse

DB_PATH = Path("data/venturelab.db")


def search_github(query, max_results=5):
    """Search GitHub for similar repos."""
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&per_page={max_results}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        return [
            {"name": item.get("full_name", ""), "stars": item.get("stargazers_count", 0)}
            for item in data.get("items", [])[:max_results]
        ]
    except:
        return []


def search_arxiv(query, max_results=5):
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
    except:
        return []


def score_idea(idea_id, idea_text):
    """Score an idea with evidence."""
    # GitHub search
    github = search_github(idea_text)
    repo_count = len(github)
    
    # arxiv search
    arxiv = search_arxiv(idea_text)
    paper_count = len(arxiv)
    
    # Novelty score
    if repo_count == 0:
        novelty = 10
        novelty_evidence = "No similar repos on GitHub"
    elif repo_count == 1:
        novelty = 7
        novelty_evidence = f"1 similar repo on GitHub"
    elif repo_count <= 3:
        novelty = 5
        novelty_evidence = f"{repo_count} similar repos on GitHub"
    elif repo_count <= 5:
        novelty = 3
        novelty_evidence = f"{repo_count} similar repos on GitHub"
    else:
        novelty = 1
        novelty_evidence = f"{repo_count} similar repos (many competitors)"
    
    # Research score
    if paper_count == 0:
        research = 2
        research_evidence = "No papers on arxiv"
    elif paper_count <= 2:
        research = 4
        research_evidence = f"{paper_count} papers on arxiv"
    elif paper_count <= 5:
        research = 6
        research_evidence = f"{paper_count} papers on arxiv"
    elif paper_count <= 10:
        research = 8
        research_evidence = f"{paper_count} papers on arxiv"
    else:
        research = 10
        research_evidence = f"{paper_count} papers on arxiv (extensive)"
    
    # Feasibility score
    if repo_count >= 3:
        feasibility = 8
        feasibility_evidence = f"{repo_count} similar projects exist"
    elif repo_count >= 1:
        feasibility = 7
        feasibility_evidence = f"{repo_count} similar project exists"
    else:
        feasibility = 5
        feasibility_evidence = "No similar projects"
    
    # Overall
    overall = (novelty + research + feasibility) / 3
    
    return {
        "idea_id": idea_id,
        "idea": idea_text,
        "scores": {
            "novelty": {"score": novelty, "evidence": novelty_evidence, "repo_count": repo_count},
            "research": {"score": research, "evidence": research_evidence, "paper_count": paper_count},
            "feasibility": {"score": feasibility, "evidence": feasibility_evidence, "repo_count": repo_count},
        },
        "overall": round(overall, 2),
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    """Score all ideas."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get all ideas
    cur.execute("SELECT idea_id, idea FROM ideas")
    ideas = cur.fetchall()
    
    print(f"Scoring {len(ideas)} ideas...")
    print()
    
    scored = []
    for idea in ideas:
        result = score_idea(idea['idea_id'], idea['idea'])
        scored.append(result)
        
        # Update database
        cur.execute("""
            UPDATE ideas SET scores = ?, updated_at = datetime('now')
            WHERE idea_id = ?
        """, (json.dumps(result['scores']), idea['idea_id']))
        
        print(f"{idea['idea_id']}: {result['overall']}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print()
    print(f"Scored {len(scored)} ideas")


if __name__ == "__main__":
    main()
