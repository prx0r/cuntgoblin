#!/usr/bin/env python3
"""Scoring determinism A/B test.

Tests if scoring is deterministic across multiple runs.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))

import json
from datetime import datetime, timezone

from factory.scoring.engine import ScoringEngine


def run_determinism_test(idea_text: str, num_runs: int = 3):
    """Run scoring multiple times and check variance."""
    engine = ScoringEngine()
    results = []
    
    for i in range(num_runs):
        scorecard = engine.score_idea(f"test_{i}", idea_text)
        results.append({
            "run": i + 1,
            "overall": scorecard.overall_score,
            "dimensions": {d.name: d.score for d in scorecard.dimensions},
        })
    
    # Analyze variance
    overall_scores = [r["overall"] for r in results]
    mean = sum(overall_scores) / len(overall_scores)
    std = (sum((x - mean) ** 2 for x in overall_scores) / len(overall_scores)) ** 0.5
    
    # Determinism assessment
    if std < 0.01:
        determinism = "DETERMINISTIC"
    elif std < 0.05:
        determinism = "NEAR-DETERMINISTIC"
    else:
        determinism = "NON-DETERMINISTIC"
    
    return {
        "idea": idea_text,
        "runs": results,
        "analysis": {
            "mean": mean,
            "std": std,
            "determinism": determinism,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    # Test with different ideas
    ideas = [
        "MCP Truth runtime reliability intelligence",
        "Endpoint Truth model endpoint measurements",
        "Knee cost-quality cliff finder",
    ]
    
    print("=== SCORING DETERMINISM A/B TEST ===")
    print()
    
    for idea in ideas:
        result = run_determinism_test(idea)
        print(f"Idea: {idea[:40]}...")
        print(f"  Overall: {result['analysis']['mean']:.2f} (std: {result['analysis']['std']:.4f})")
        print(f"  Determinism: {result['analysis']['determinism']}")
        print()
        
        # Save result
        results_file = Path("data/runs") / f"scoring_det_{idea[:20].replace(' ', '_')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, "w") as f:
            json.dump(result, f, indent=2)
    
    print("All tests complete")
