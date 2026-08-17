#!/usr/bin/env python3
"""autonomous_loop.py — Continuous autonomous venture research loop.

This script runs continuously, seeding ideas, investigating them, assessing them,
and expanding outwards to find related opportunities.

Usage:
  python3 autonomous_loop.py --iterations 5
  python3 autonomous_loop.py --continuous
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
import urllib.request
import urllib.parse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def log(msg=""):
    """Print with timestamp."""
    if msg:
        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}")
    else:
        print()


def search_arxiv(query, max_results=5):
    """Search arxiv for related papers."""
    encoded_query = urllib.parse.quote(query)
    url = f'http://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending'
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'venturelab/1.0'})
        resp = urllib.request.urlopen(req, timeout=30)
        content = resp.read().decode()
        
        results = []
        entries = content.split('<entry>')[1:]
        for entry in entries[:max_results]:
            title = entry.split('<title>')[1].split('</title>')[0] if '<title>' in entry else ''
            summary = entry.split('<summary>')[1].split('</summary>')[0] if '<summary>' in entry else ''
            published = entry.split('<published>')[1].split('</published>')[0] if '<published>' in entry else ''
            
            results.append({
                'title': title.strip(),
                'summary': summary.strip()[:200],
                'published': published.strip()[:10],
            })
        return results
    except Exception as e:
        return [{'error': str(e)}]


def search_github(query, max_results=5):
    """Search github for related repos."""
    encoded_query = urllib.parse.quote(query)
    url = f'https://api.github.com/search/repositories?q={encoded_query}&sort=stars&per_page={max_results}'
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'venturelab/1.0'})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        
        results = []
        for item in data.get('items', [])[:max_results]:
            results.append({
                'name': item.get('full_name', ''),
                'description': item.get('description', ''),
                'stars': item.get('stargazers_count', 0),
                'url': item.get('html_url', ''),
            })
        return results
    except Exception as e:
        return [{'error': str(e)}]


def seed_ideas_from_gaps():
    """Seed new ideas from research gaps."""
    log("Seeding ideas from research gaps...")
    
    # Load existing research
    research_file = ROOT / "data" / "research.jsonl"
    if not research_file.exists():
        return []
    
    existing = []
    with open(research_file, encoding='utf-8') as f:
        for line in f:
            existing.append(json.loads(line))
    
    # Find gaps
    gaps = set()
    for r in existing:
        competitors = r.get('competitors', [])
        if len(competitors) < 3:
            gaps.add(r.get('idea', ''))
    
    # Generate new ideas from gaps
    new_ideas = []
    
    idea_templates = [
        "Agent-native {domain} verification API",
        "Machine-readable {domain} receipt protocol",
        "{domain} reputation from grounded receipts",
        "Runtime policy decision point for {domain}",
        "Evidence-backed {domain} attestation service",
    ]
    
    domains = [
        "physical-world",
        "agent-task",
        "human-inference",
        "real-world-execution",
        "cross-platform",
    ]
    
    for domain in domains:
        for template in idea_templates[:2]:
            idea = template.format(domain=domain)
            if idea not in [r.get('idea', '') for r in existing]:
                new_ideas.append({
                    'idea_id': f"VENT_{int(time.time())}_{len(new_ideas)}",
                    'idea': idea,
                    'status': 'seeded',
                    'created_at': datetime.now(timezone.utc).isoformat(),
                })
    
    return new_ideas


def investigate_idea(idea):
    """Deep investigate an idea."""
    log(f"Investigating: {idea['idea'][:60]}...")
    
    # Search arxiv
    arxiv_results = search_arxiv(idea['idea'])
    
    # Search github
    github_results = search_github(idea['idea'])
    
    # Save research
    research_record = {
        'idea_id': idea['idea_id'],
        'idea': idea['idea'],
        'arxiv': arxiv_results,
        'github': github_results,
        'investigated_at': datetime.now(timezone.utc).isoformat(),
    }
    
    research_file = ROOT / "data" / "research.jsonl"
    with open(research_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(research_record, ensure_ascii=False) + '\n')
    
    return research_record


def assess_idea(research_record):
    """Assess an idea for potential."""
    idea = research_record.get('idea', '')
    arxiv_count = len(research_record.get('arxiv', []))
    github_count = len(research_record.get('github', []))
    
    # Score
    novelty = 10 if github_count < 3 else 7 if github_count < 10 else 4
    research = 10 if arxiv_count >= 5 else 7 if arxiv_count >= 2 else 4
    feasibility = 8 if github_count > 0 else 6
    
    overall = (novelty + research + feasibility) / 3
    
    assessment = {
        'idea_id': research_record.get('idea_id'),
        'idea': idea,
        'scores': {
            'novelty': novelty,
            'research': research,
            'feasibility': feasibility,
            'overall': overall,
        },
        'verdict': 'STRONG' if overall >= 7 else 'MODERATE' if overall >= 5 else 'WEAK',
        'assessed_at': datetime.now(timezone.utc).isoformat(),
    }
    
    # Save assessment
    eval_file = ROOT / "data" / "evaluations.jsonl"
    with open(eval_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(assessment, ensure_ascii=False) + '\n')
    
    return assessment


def expand_ideas(assessment):
    """Expand from an assessment to find related ideas."""
    idea = assessment.get('idea', '')
    
    # Extract keywords
    keywords = idea.lower().split()
    
    # Search for related
    related_queries = []
    if 'verification' in keywords:
        related_queries.append('agent verification protocol')
    if 'receipt' in keywords:
        related_queries.append('signed work receipt')
    if 'reputation' in keywords:
        related_queries.append('agent reputation system')
    if 'policy' in keywords:
        related_queries.append('agent authorization policy')
    
    # Search
    related = []
    for query in related_queries[:2]:
        results = search_arxiv(query)
        related.extend(results)
    
    return related


def run_loop(iterations=5):
    """Run the autonomous loop."""
    log("=== AUTONOMOUS LOOP STARTED ===")
    log(f"Iterations: {iterations}")
    log()
    
    for i in range(iterations):
        log(f"--- Iteration {i+1}/{iterations} ---")
        
        # Seed ideas
        new_ideas = seed_ideas_from_gaps()
        log(f"Seeded {len(new_ideas)} new ideas")
        
        # Investigate each
        for idea in new_ideas[:3]:
            research = investigate_idea(idea)
            
            # Assess
            assessment = assess_idea(research)
            log(f"  Assessed: {assessment['verdict']} (score={assessment['scores']['overall']:.1f})")
            
            # Expand
            related = expand_ideas(assessment)
            log(f"  Found {len(related)} related ideas")
        
        log()
    
    log("=== AUTONOMOUS LOOP COMPLETE ===")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--continuous", action="store_true")
    args = parser.parse_args()
    
    if args.continuous:
        iteration = 0
        while True:
            iteration += 1
            log(f"\n=== CONTINUOUS LOOP: Cycle {iteration} ===\n")
            run_loop(iterations=1)
            log(f"Sleeping 60 seconds before next cycle...")
            time.sleep(60)
    else:
        run_loop(args.iterations)
