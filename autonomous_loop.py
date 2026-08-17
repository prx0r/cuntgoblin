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


def search_arxiv(query, max_results=3):
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


def search_github(query, max_results=3):
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


def load_ideas():
    """Load all ideas."""
    ideas = []
    ideas_file = ROOT / "data" / "ideas.jsonl"
    if ideas_file.exists():
        with open(ideas_file, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    ideas.append(json.loads(line))
    return ideas


def save_ideas(ideas):
    """Save all ideas."""
    ideas_file = ROOT / "data" / "ideas.jsonl"
    with open(ideas_file, 'w', encoding='utf-8') as f:
        for idea in ideas:
            f.write(json.dumps(idea, ensure_ascii=False) + '\n')


def load_investigated():
    """Load investigated idea IDs."""
    investigated = set()
    research_file = ROOT / "data" / "research.jsonl"
    if research_file.exists():
        with open(research_file, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    investigated.add(r.get('idea_id', ''))
    return investigated


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


def expand_from_research(research_record):
    """Expand from research to find related ideas."""
    idea = research_record.get('idea', '')
    arxiv = research_record.get('arxiv', [])
    github = research_record.get('github', [])
    
    new_ideas = []
    
    # Extract keywords
    keywords = idea.lower().split()
    
    # Generate related ideas based on what we found
    if 'verification' in keywords:
        new_ideas.append({
            'idea_id': f"VENT_{int(time.time())}_verification",
            'idea': f"Agent-native {keywords[0] if keywords else 'task'} verification protocol",
            'status': 'seeded',
            'created_at': datetime.now(timezone.utc).isoformat(),
        })
    
    if 'receipt' in keywords:
        new_ideas.append({
            'idea_id': f"VENT_{int(time.time())}_receipt",
            'idea': f"Machine-readable {keywords[0] if keywords else 'task'} receipt standard",
            'status': 'seeded',
            'created_at': datetime.now(timezone.utc).isoformat(),
        })
    
    if 'reputation' in keywords:
        new_ideas.append({
            'idea_id': f"VENT_{int(time.time())}_reputation",
            'idea': f"Grounded reputation from {keywords[0] if keywords else 'task'} receipts",
            'status': 'seeded',
            'created_at': datetime.now(timezone.utc).isoformat(),
        })
    
    # Extract from arxiv papers
    for paper in arxiv[:2]:
        if 'error' not in paper:
            title = paper.get('title', '')
            if title:
                new_ideas.append({
                    'idea_id': f"VENT_{int(time.time())}_paper",
                    'idea': f"Application of: {title[:60]}",
                    'status': 'seeded',
                    'created_at': datetime.now(timezone.utc).isoformat(),
                })
    
    return new_ideas


def run_loop(iterations=5):
    """Run the autonomous loop."""
    log("=== AUTONOMOUS LOOP STARTED ===")
    log(f"Iterations: {iterations}")
    log()
    
    ideas = load_ideas()
    investigated = load_investigated()
    
    log(f"Loaded {len(ideas)} ideas, {len(investigated)} already investigated")
    log()
    
    total_investigated = 0
    total_expanded = 0
    
    for i in range(iterations):
        log(f"--- Iteration {i+1}/{iterations} ---")
        
        # Find ideas that haven't been investigated
        uninvestigated = [idea for idea in ideas if idea.get('idea_id') not in investigated]
        
        if not uninvestigated:
            log("No uninvestigated ideas found, generating new ones...")
            # Generate new ideas from existing
            for idea in ideas[:3]:
                new_ideas = expand_from_research({'idea': idea.get('idea', '')})
                ideas.extend(new_ideas)
                total_expanded += len(new_ideas)
            uninvestigated = [idea for idea in ideas if idea.get('idea_id') not in investigated]
        
        # Investigate top 3 uninvestigated ideas
        for idea in uninvestigated[:3]:
            research = investigate_idea(idea)
            investigated.add(idea.get('idea_id'))
            total_investigated += 1
            
            # Expand from research
            new_ideas = expand_from_research(research)
            ideas.extend(new_ideas)
            total_expanded += len(new_ideas)
            
            log(f"  Investigated: {idea['idea_id']}")
            log(f"  Found: {len(new_ideas)} related ideas")
        
        # Save updated ideas
        save_ideas(ideas)
        
        log(f"  Total ideas: {len(ideas)}")
        log(f"  Total investigated: {total_investigated}")
        log()
    
    log("=== AUTONOMOUS LOOP COMPLETE ===")
    log(f"Total investigated: {total_investigated}")
    log(f"Total expanded: {total_expanded}")
    log(f"Total ideas: {len(ideas)}")


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
