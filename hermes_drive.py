#!/usr/bin/env python3
"""hermes_drive.py — Hermes-driven venture research.

This script uses hermes to actually research ideas intelligently.
"""
import subprocess
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def hermes_chat(prompt):
    """Run hermes chat with a prompt."""
    try:
        result = subprocess.run(
            ["hermes", "chat", "-z", prompt],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(ROOT)
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"


def research_idea(idea_id, idea_text):
    """Use hermes to research an idea."""
    prompt = f"""Research this venture idea and give me:
1. What GitHub repos exist for this?
2. What's the competitive landscape?
3. What's the monetization path?
4. Score it 1-10 for novelty, feasibility, market timing

Idea: {idea_text}

Be concise. Give me facts, not fluff."""
    
    return hermes_chat(prompt)


def main():
    print("=== HERMES-DRIVEN RESEARCH ===")
    print()
    
    # Get ideas from database
    import sqlite3
    db_path = ROOT / "data" / "venturelab.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT i.idea_id, i.idea 
        FROM ideas i 
        LEFT JOIN research r ON i.idea_id = r.idea_id 
        WHERE r.id IS NULL 
        LIMIT 5
    """)
    ideas = cur.fetchall()
    
    for idea in ideas:
        print(f"Researching: {idea['idea'][:60]}...")
        result = research_idea(idea['idea_id'], idea['idea'])
        print(f"Result: {result[:200]}")
        print()
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
