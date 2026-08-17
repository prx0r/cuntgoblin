#!/usr/bin/env python3
"""build_mvp.py — Build MVPs using hermes kanban.

This script uses hermes to actually build MVPs based on our ideas.
"""
import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "venturelab.db"


def log(msg=""):
    if msg:
        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}")
    else:
        print()


def hermes_query(prompt):
    """Run hermes query."""
    try:
        result = subprocess.run(
            ["hermes", "chat", "-q", prompt],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(ROOT)
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def clone_template(template_name, target_name):
    """Clone a template repo."""
    template_dir = Path(f"/root/{template_name}")
    target_dir = ROOT / "builds" / target_name
    
    if not template_dir.exists():
        log(f"Template {template_name} not found")
        return None
    
    # Copy template
    import shutil
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(template_dir, target_dir)
    
    log(f"Cloned {template_name} -> {target_name}")
    return target_dir


def build_mvp(idea_id, idea_text, template="dell-new"):
    """Build an MVP for an idea."""
    log(f"Building MVP for: {idea_text[:60]}...")
    
    # Clone template
    target_name = f"mvp_{idea_id[:20]}"
    build_dir = clone_template(template, target_name)
    
    if not build_dir:
        return None
    
    # Use hermes to customize
    prompt = f"""I'm building an MVP for: {idea_text}

The template is cloned at {build_dir}.

What files should I modify to make this work for this specific idea?
Give me the key changes needed. Be specific."""
    
    result = hermes_query(prompt)
    log(f"  Hermes advice: {result[:200]}")
    
    return build_dir


def main():
    log("=== BUILD MVP SYSTEM ===")
    log()
    
    # Get top ideas
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT idea_id, idea, scores
        FROM ideas
        WHERE category = 'Oracle'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    ideas = cur.fetchall()
    
    for idea in ideas:
        scores = json.loads(idea['scores']) if idea['scores'] else {}
        log(f"Building: {idea['idea_id']}")
        build_dir = build_mvp(idea['idea_id'], idea['idea'])
        if build_dir:
            log(f"  Built at: {build_dir}")
        log()
    
    cur.close()
    conn.close()
    
    log("=== BUILD COMPLETE ===")


if __name__ == "__main__":
    main()
