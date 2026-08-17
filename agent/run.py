#!/usr/bin/env python3
"""agent/run.py — the AGENT-RUN orchestrator for venturelab.

A single entry point an agent (or the watchdog) calls to run ANY lab step:
  - it claims/completes the relevant kanban task
  - runs the underlying lab script
  - logs the result to the experiment registry
  - posts a comment / updates the task

Usage:
  python3 agent/run.py --step discover --idea "API for X"
  python3 agent/run.py --step research --idea-id VENT_001
  python3 agent/run.py --step evaluate --idea-id VENT_001
  python3 agent/run.py --step report
  python3 agent/run.py --step watchdog
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT))


def _sh(*args: str, timeout: int = 600) -> str:
    """Run a shell command (background-safe), return stdout."""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return f"__TIMEOUT__ {' '.join(args)}"


def log_line(record: dict) -> Path:
    """Append a machine-readable result to the lab registry."""
    reg = ROOT / "data" / "runs" / "venture-runs.jsonl"
    reg.parent.mkdir(parents=True, exist_ok=True)
    record["ts"] = datetime.now(timezone.utc).isoformat()
    with open(reg, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return reg


# ── the lab steps ───────────────────────────────────────────────────────────

def step_discover(idea: str) -> dict:
    """Log a new venture idea."""
    idea_id = f"VENT_{int(time.time())}"
    
    idea_record = {
        "idea_id": idea_id,
        "idea": idea,
        "status": "discovered",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    # Save idea to ideas registry
    ideas_file = ROOT / "data" / "ideas.jsonl"
    ideas_file.parent.mkdir(parents=True, exist_ok=True)
    with open(ideas_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(idea_record, ensure_ascii=False) + "\n")
    
    rec = {"step": "discover", "idea_id": idea_id, "idea": idea, "status": "logged"}
    log_line(rec)
    print(f"Idea logged: {idea_id}")
    print(f"Idea: {idea}")
    return rec


def step_research(idea_id: str) -> dict:
    """Deep dive research on an idea."""
    # Load the idea
    ideas_file = ROOT / "data" / "ideas.jsonl"
    if not ideas_file.exists():
        print(f"No ideas file found")
        return {"step": "research", "error": "no ideas file"}
    
    idea_record = None
    with open(ideas_file, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if record.get("idea_id") == idea_id:
                idea_record = record
                break
    
    if not idea_record:
        print(f"Idea {idea_id} not found")
        return {"step": "research", "error": "idea not found"}
    
    idea = idea_record.get("idea", "")
    
    print(f"Researching: {idea_id}")
    print(f"Idea: {idea}")
    print()
    
    # Research 1: Check arxiv
    print("=== ARXIV CHECK ===")
    arxiv_results = check_arxiv(idea)
    print(f"Found {len(arxiv_results)} related papers")
    for r in arxiv_results[:3]:
        print(f"  - {r.get('title', 'Unknown')[:80]}")
    print()
    
    # Research 2: Check github
    print("=== GITHUB CHECK ===")
    github_results = check_github(idea)
    print(f"Found {len(github_results)} related repos")
    for r in github_results[:3]:
        print(f"  - {r.get('name', 'Unknown')}: {r.get('description', '')[:60]}")
    print()
    
    # Research 3: Check existing products
    print("=== EXISTING PRODUCTS ===")
    existing = check_existing_products(idea)
    print(f"Found {len(existing)} existing products")
    for p in existing[:3]:
        print(f"  - {p.get('name', 'Unknown')}: {p.get('description', '')[:60]}")
    print()
    
    # Save research
    research_record = {
        "idea_id": idea_id,
        "idea": idea,
        "arxiv": arxiv_results,
        "github": github_results,
        "existing_products": existing,
        "researched_at": datetime.now(timezone.utc).isoformat(),
    }
    
    research_file = ROOT / "data" / "research.jsonl"
    research_file.parent.mkdir(parents=True, exist_ok=True)
    with open(research_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(research_record, ensure_ascii=False) + "\n")
    
    rec = {"step": "research", "idea_id": idea_id, "arxiv_count": len(arxiv_results), "github_count": len(github_results)}
    log_line(rec)
    return rec


def step_evaluate(idea_id: str) -> dict:
    """Evaluate an idea for monetization and usefulness."""
    # Load research
    research_file = ROOT / "data" / "research.jsonl"
    if not research_file.exists():
        print(f"No research file found")
        return {"step": "evaluate", "error": "no research file"}
    
    research_record = None
    with open(research_file, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if record.get("idea_id") == idea_id:
                research_record = record
                break
    
    if not research_record:
        print(f"Research for {idea_id} not found")
        return {"step": "evaluate", "error": "research not found"}
    
    idea = research_record.get("idea", "")
    arxiv_count = len(research_record.get("arxiv", []))
    github_count = len(research_record.get("github", []))
    existing_count = len(research_record.get("existing_products", []))
    
    print(f"Evaluating: {idea_id}")
    print(f"Idea: {idea}")
    print()
    
    # Scoring
    scores = {}
    
    # Novelty score (less existing = more novel)
    if existing_count == 0:
        scores["novelty"] = 10
    elif existing_count <= 2:
        scores["novelty"] = 8
    elif existing_count <= 5:
        scores["novelty"] = 6
    elif existing_count <= 10:
        scores["novelty"] = 4
    else:
        scores["novelty"] = 2
    
    # Research score (more papers = more validated)
    if arxiv_count >= 10:
        scores["research"] = 10
    elif arxiv_count >= 5:
        scores["research"] = 8
    elif arxiv_count >= 2:
        scores["research"] = 6
    elif arxiv_count >= 1:
        scores["research"] = 4
    else:
        scores["research"] = 2
    
    # Implementation score (more repos = more feasible)
    if github_count >= 10:
        scores["implementation"] = 10
    elif github_count >= 5:
        scores["implementation"] = 8
    elif github_count >= 2:
        scores["implementation"] = 6
    elif github_count >= 1:
        scores["implementation"] = 4
    else:
        scores["implementation"] = 2
    
    # Overall score
    scores["overall"] = sum(scores.values()) / len(scores)
    
    print("=== SCORES ===")
    for key, value in scores.items():
        print(f"  {key}: {value}/10")
    print()
    
    # Verdict
    if scores["overall"] >= 7:
        verdict = "STRONG — Build now"
    elif scores["overall"] >= 5:
        verdict = "MODERATE — Worth investigating"
    elif scores["overall"] >= 3:
        verdict = "WEAK — Saturation risk"
    else:
        verdict = "SKIP — Already solved"
    
    print(f"Verdict: {verdict}")
    
    # Save evaluation
    eval_record = {
        "idea_id": idea_id,
        "idea": idea,
        "scores": scores,
        "verdict": verdict,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    eval_file = ROOT / "data" / "evaluations.jsonl"
    eval_file.parent.mkdir(parents=True, exist_ok=True)
    with open(eval_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(eval_record, ensure_ascii=False) + "\n")
    
    rec = {"step": "evaluate", "idea_id": idea_id, "scores": scores, "verdict": verdict}
    log_line(rec)
    return rec


def step_report() -> dict:
    """Generate a venture brief report."""
    print("=== VENTURE BRIEF REPORT ===")
    print()
    
    # Load all evaluations
    eval_file = ROOT / "data" / "evaluations.jsonl"
    if not eval_file.exists():
        print("No evaluations found")
        return {"step": "report", "error": "no evaluations"}
    
    evaluations = []
    with open(eval_file, encoding="utf-8") as f:
        for line in f:
            evaluations.append(json.loads(line))
    
    # Sort by overall score
    evaluations.sort(key=lambda x: x.get("scores", {}).get("overall", 0), reverse=True)
    
    print(f"Total ideas evaluated: {len(evaluations)}")
    print()
    
    for i, eval_record in enumerate(evaluations[:10], 1):
        idea_id = eval_record.get("idea_id", "")
        idea = eval_record.get("idea", "")
        scores = eval_record.get("scores", {})
        verdict = eval_record.get("verdict", "")
        
        print(f"{i}. {idea_id}")
        print(f"   Idea: {idea[:80]}")
        print(f"   Score: {scores.get('overall', 0):.1f}/10")
        print(f"   Verdict: {verdict}")
        print()
    
    rec = {"step": "report", "total_evaluated": len(evaluations)}
    log_line(rec)
    return rec


def step_watchdog() -> dict:
    """Run a full watchdog cycle."""
    print("=== WATCHDOG CYCLE ===")
    print()
    
    # Load all ideas that need research
    ideas_file = ROOT / "data" / "ideas.jsonl"
    if not ideas_file.exists():
        print("No ideas found")
        return {"step": "watchdog", "error": "no ideas"}
    
    ideas = []
    with open(ideas_file, encoding="utf-8") as f:
        for line in f:
            ideas.append(json.loads(line))
    
    # Research and evaluate each idea
    for idea_record in ideas:
        idea_id = idea_record.get("idea_id", "")
        status = idea_record.get("status", "")
        
        if status == "discovered":
            print(f"Researching {idea_id}...")
            step_research(idea_id)
            step_evaluate(idea_id)
    
    # Generate report
    step_report()
    
    rec = {"step": "watchdog", "processed": len(ideas)}
    log_line(rec)
    return rec


# ── research helpers ─────────────────────────────────────────────────────────

def check_arxiv(idea: str) -> list[dict]:
    """Check arxiv for related papers."""
    import urllib.request
    import urllib.parse
    
    query = urllib.parse.quote(idea)
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=5"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        content = resp.read().decode()
        
        # Simple XML parsing for arxiv results
        results = []
        entries = content.split("<entry>")[1:]  # Skip first empty split
        for entry in entries[:5]:
            title_match = entry.split("<title>")[1].split("</title>")[0] if "<title>" in entry else ""
            summary_match = entry.split("<summary>")[1].split("</summary>")[0] if "<summary>" in entry else ""
            results.append({
                "title": title_match.strip(),
                "summary": summary_match.strip()[:200],
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def check_github(idea: str) -> list[dict]:
    """Check github for related repos."""
    import urllib.request
    import urllib.parse
    
    query = urllib.parse.quote(idea)
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&per_page=5"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        
        results = []
        for item in data.get("items", [])[:5]:
            results.append({
                "name": item.get("full_name", ""),
                "description": item.get("description", ""),
                "stars": item.get("stargazers_count", 0),
                "url": item.get("html_url", ""),
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def check_existing_products(idea: str) -> list[dict]:
    """Check for existing products (simplified)."""
    # In a real implementation, this would search product databases
    # For now, return empty
    return []


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="VentureLab orchestrator")
    parser.add_argument("--step", required=True, choices=["discover", "research", "evaluate", "report", "watchdog"])
    parser.add_argument("--idea", help="Idea text for discover step")
    parser.add_argument("--idea-id", help="Idea ID for research/evaluate steps")
    
    args = parser.parse_args()
    
    if args.step == "discover":
        if not args.idea:
            print("Error: --idea required for discover step")
            sys.exit(1)
        step_discover(args.idea)
    
    elif args.step == "research":
        if not args.idea_id:
            print("Error: --idea-id required for research step")
            sys.exit(1)
        step_research(args.idea_id)
    
    elif args.step == "evaluate":
        if not args.idea_id:
            print("Error: --idea-id required for evaluate step")
            sys.exit(1)
        step_evaluate(args.idea_id)
    
    elif args.step == "report":
        step_report()
    
    elif args.step == "watchdog":
        step_watchdog()


if __name__ == "__main__":
    main()
