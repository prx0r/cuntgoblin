#!/usr/bin/env python3
"""hermes_loop.py — Hermes-driven autonomous venture research loop.

This script uses hermes kanban to orchestrate parallel research agents.

Usage:
  python3 hermes_loop.py --iterations 5
  python3 hermes_loop.py --continuous
"""
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

BOARD = "venturelab"


def log(msg=""):
    """Print with timestamp."""
    if msg:
        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}")
    else:
        print()


def hermes(*args):
    """Run hermes command."""
    try:
        result = subprocess.run(
            ["hermes"] + list(args),
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "__TIMEOUT__"
    except Exception as e:
        return f"__ERROR__ {e}"


def create_board():
    """Create kanban board if not exists."""
    log("Creating kanban board...")
    output = hermes("kanban", "boards", "create", BOARD, "--description", "VentureLab autonomous research")
    log(f"  Board: {output[:100]}")
    return output


def create_swarm(goal, workers):
    """Create a kanban swarm with parallel workers."""
    log(f"Creating swarm: {goal[:60]}...")
    
    # Build worker args
    args = ["kanban", "swim", goal, "--board", BOARD]
    for worker in workers:
        args.extend(["--worker", worker])
    
    output = hermes(*args)
    log(f"  Swarm: {output[:100]}")
    return output


def dispatch_workers():
    """Dispatch workers to execute tasks."""
    log("Dispatching workers...")
    output = hermes("kanban", "dispatch", "--board", BOARD, "--max", "5")
    log(f"  Dispatch: {output[:100]}")
    return output


def list_tasks():
    """List all tasks."""
    output = hermes("kanban", "list", "--board", BOARD)
    return output


def complete_task(task_id):
    """Complete a task."""
    output = hermes("kanban", "complete", task_id, "--board", BOARD)
    return output


def comment_task(task_id, comment):
    """Add comment to task."""
    output = hermes("kanban", "comment", task_id, "--board", BOARD, "--comment", comment)
    return output


def research_venture(venture_id, idea):
    """Research a venture idea using hermes."""
    log(f"Researching: {idea[:60]}...")
    
    # Create swarm for this venture
    workers = [
        f"researcher:Research arxiv for {idea[:30]}:research",
        f"researcher:Research github for {idea[:30]}:research",
        f"analyst:Analyze competitors for {idea[:30]}:research",
    ]
    
    create_swarm(f"Research {venture_id}: {idea[:50]}", workers)
    
    # Dispatch
    dispatch_workers()
    
    # Wait for completion
    time.sleep(10)
    
    # Check status
    tasks = list_tasks()
    log(f"  Tasks: {tasks[:200]}")
    
    return tasks


def generate_report():
    """Generate venture brief report."""
    log("Generating report...")
    
    # Load all research
    research = []
    research_file = ROOT / "data" / "research.jsonl"
    if research_file.exists():
        with open(research_file, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    research.append(json.loads(line))
    
    # Load evaluations
    evaluations = []
    eval_file = ROOT / "data" / "evaluations.jsonl"
    if eval_file.exists():
        with open(eval_file, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    evaluations.append(json.loads(line))
    
    # Generate report
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_research": len(research),
        "total_evaluations": len(evaluations),
        "top_ideas": [],
    }
    
    # Sort evaluations by score
    evaluations.sort(key=lambda x: x.get('scores', {}).get('overall', 0), reverse=True)
    
    for e in evaluations[:10]:
        report["top_ideas"].append({
            "idea_id": e.get("idea_id"),
            "idea": e.get("idea"),
            "score": e.get("scores", {}).get("overall", 0),
            "verdict": e.get("verdict"),
        })
    
    # Save report
    report_file = ROOT / "data" / "reports" / f"venture-brief-{int(time.time())}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    log(f"  Report saved: {report_file}")
    return report


def run_loop(iterations=5):
    """Run the hermes-driven loop."""
    log("=== HERMES-DRIVEN LOOP STARTED ===")
    log(f"Iterations: {iterations}")
    log()
    
    # Create board
    create_board()
    log()
    
    # Load ideas
    ideas = []
    ideas_file = ROOT / "data" / "ideas.jsonl"
    if ideas_file.exists():
        with open(ideas_file, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    ideas.append(json.loads(line))
    
    log(f"Loaded {len(ideas)} ideas")
    log()
    
    for i in range(iterations):
        log(f"--- Iteration {i+1}/{iterations} ---")
        
        # Pick top ideas to research
        top_ideas = ideas[:3]
        
        for idea in top_ideas:
            # Create task
            task_id = f"VENT_{idea.get('idea_id', int(time.time()))}"
            log(f"Creating task: {task_id}")
            
            # Research using hermes swarm
            research_venture(task_id, idea.get('idea', ''))
        
        # Generate report
        generate_report()
        
        log()
    
    log("=== HERMES-DRIVEN LOOP COMPLETE ===")


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
