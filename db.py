#!/usr/bin/env python3
"""db.py — VentureLab database interface (SQLite).

Hermes can use this to write directly to the database.
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "venturelab.db"


def get_conn():
    """Get database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with schema."""
    conn = get_conn()
    cur = conn.cursor()
    
    # Ideas table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT UNIQUE NOT NULL,
            idea TEXT NOT NULL,
            thesis TEXT,
            category TEXT,
            status TEXT DEFAULT 'seeded',
            scores TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Research table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT,
            arxiv_results TEXT DEFAULT '[]',
            github_results TEXT DEFAULT '[]',
            competitors TEXT DEFAULT '[]',
            evidence TEXT DEFAULT '[]',
            researched_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (idea_id) REFERENCES ideas(idea_id)
        )
    """)
    
    # Evaluations table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT,
            novelty_score REAL,
            research_score REAL,
            feasibility_score REAL,
            overall_score REAL,
            verdict TEXT,
            evaluated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (idea_id) REFERENCES ideas(idea_id)
        )
    """)
    
    # Hypotheses table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hypotheses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hypothesis TEXT NOT NULL,
            based_on TEXT,
            confidence REAL,
            test_plan TEXT,
            status TEXT DEFAULT 'proposed',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Reports table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type TEXT,
            title TEXT,
            content TEXT,
            generated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Competitors table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venture TEXT,
            player TEXT,
            relation TEXT,
            what_it_does TEXT,
            capability TEXT,
            business_model TEXT,
            strength TEXT,
            gap TEXT,
            source_url TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Evidence table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theme TEXT,
            finding TEXT,
            applies_to TEXT,
            source_url TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Research papers table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS research_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            authors TEXT,
            published TEXT,
            relevant_venture TEXT,
            key_finding TEXT,
            product_implication TEXT,
            source_url TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # OSS projects table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS oss_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository TEXT,
            theme TEXT,
            what_it_provides TEXT,
            why_useful TEXT,
            url TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Roadmap table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS roadmap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phase TEXT,
            focus TEXT,
            build_plan TEXT,
            exit_criterion TEXT,
            monetization TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized")


def insert_idea(idea_id, idea, thesis=None, category=None, status='seeded', scores=None):
    """Insert a new idea."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT OR REPLACE INTO ideas (idea_id, idea, thesis, category, status, scores, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, (idea_id, idea, thesis, category, status, json.dumps(scores or {})))
    
    conn.commit()
    cur.close()
    conn.close()
    return idea_id


def insert_research(idea_id, arxiv_results=None, github_results=None, competitors=None, evidence=None):
    """Insert research results."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO research (idea_id, arxiv_results, github_results, competitors, evidence)
        VALUES (?, ?, ?, ?, ?)
    """, (idea_id, json.dumps(arxiv_results or []), json.dumps(github_results or []),
          json.dumps(competitors or []), json.dumps(evidence or [])))
    
    conn.commit()
    cur.close()
    conn.close()


def insert_evaluation(idea_id, novelty_score, research_score, feasibility_score, overall_score, verdict):
    """Insert evaluation."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO evaluations (idea_id, novelty_score, research_score, feasibility_score, overall_score, verdict)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (idea_id, novelty_score, research_score, feasibility_score, overall_score, verdict))
    
    conn.commit()
    cur.close()
    conn.close()


def insert_hypothesis(hypothesis, based_on=None, confidence=None, test_plan=None):
    """Insert hypothesis."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO hypotheses (hypothesis, based_on, confidence, test_plan)
        VALUES (?, ?, ?, ?)
    """, (hypothesis, based_on, confidence, test_plan))
    
    conn.commit()
    cur.close()
    conn.close()


def insert_competitor(venture, player, relation, what_it_does, capability=None, business_model=None, strength=None, gap=None, source_url=None):
    """Insert competitor."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO competitors (venture, player, relation, what_it_does, capability, business_model, strength, gap, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (venture, player, relation, what_it_does, capability, business_model, strength, gap, source_url))
    
    conn.commit()
    cur.close()
    conn.close()


def insert_evidence(theme, finding, applies_to, source_url=None):
    """Insert evidence."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO evidence (theme, finding, applies_to, source_url)
        VALUES (?, ?, ?, ?)
    """, (theme, finding, applies_to, source_url))
    
    conn.commit()
    cur.close()
    conn.close()


def get_ideas(status=None, category=None, limit=100):
    """Get ideas with optional filters."""
    conn = get_conn()
    cur = conn.cursor()
    
    query = "SELECT * FROM ideas"
    params = []
    conditions = []
    
    if status:
        conditions.append("status = ?")
        params.append(status)
    if category:
        conditions.append("category = ?")
        params.append(category)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cur.execute(query, params)
    columns = [desc[0] for desc in cur.description]
    results = [dict(zip(columns, row)) for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    return results


def get_top_ideas(limit=10):
    """Get top ideas by overall score."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT i.idea_id, i.idea, e.overall_score, e.verdict
        FROM ideas i
        JOIN evaluations e ON i.idea_id = e.idea_id
        ORDER BY e.overall_score DESC
        LIMIT ?
    """, (limit,))
    
    results = [{"idea_id": r[0], "idea": r[1], "score": r[2], "verdict": r[3]} for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    return results


def generate_report():
    """Generate venture brief report."""
    conn = get_conn()
    cur = conn.cursor()
    
    # Get stats
    cur.execute("SELECT COUNT(*) FROM ideas")
    total_ideas = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM evaluations")
    total_evaluations = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM hypotheses")
    total_hypotheses = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM competitors")
    total_competitors = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM evidence")
    total_evidence = cur.fetchone()[0]
    
    # Get top ideas
    cur.execute("""
        SELECT i.idea_id, i.idea, e.overall_score, e.verdict
        FROM ideas i
        JOIN evaluations e ON i.idea_id = e.idea_id
        ORDER BY e.overall_score DESC
        LIMIT 10
    """)
    top_ideas = [{"idea_id": r[0], "idea": r[1], "score": r[2], "verdict": r[3]} for r in cur.fetchall()]
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "total_ideas": total_ideas,
            "total_evaluations": total_evaluations,
            "total_hypotheses": total_hypotheses,
            "total_competitors": total_competitors,
            "total_evidence": total_evidence,
        },
        "top_ideas": top_ideas,
    }
    
    # Save report
    cur.execute("""
        INSERT INTO reports (report_type, title, content)
        VALUES (?, ?, ?)
    """, ('venture_brief', 'Venture Brief Report', json.dumps(report)))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return report


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_db()
    elif len(sys.argv) > 1 and sys.argv[1] == "report":
        report = generate_report()
        print(json.dumps(report, indent=2))
    else:
        print("Usage: python3 db.py init|report")
