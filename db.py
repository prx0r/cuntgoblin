#!/usr/bin/env python3
"""db.py — VentureLab database interface.

Hermes can use this to write directly to the database.
"""
import json
import psycopg2
from datetime import datetime, timezone

DB_DSN = "postgresql://patala:patala@localhost:5432/venturelab"


def get_conn():
    """Get database connection."""
    return psycopg2.connect(DB_DSN)


def init_db():
    """Initialize database with schema."""
    conn = get_conn()
    cur = conn.cursor()
    
    # Read schema
    with open('sql/schema.sql', 'r') as f:
        schema = f.read()
    
    cur.execute(schema)
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized")


def insert_idea(idea_id, idea, thesis=None, category=None, status='seeded', scores=None):
    """Insert a new idea."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO ideas (idea_id, idea, thesis, category, status, scores)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (idea_id) DO UPDATE SET
            idea = EXCLUDED.idea,
            thesis = EXCLUDED.thesis,
            category = EXCLUDED.category,
            status = EXCLUDED.status,
            scores = EXCLUDED.scores,
            updated_at = NOW()
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
        VALUES (%s, %s, %s, %s, %s)
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
        VALUES (%s, %s, %s, %s, %s, %s)
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
        VALUES (%s, %s, %s, %s)
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
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        VALUES (%s, %s, %s, %s)
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
        conditions.append("status = %s")
        params.append(status)
    if category:
        conditions.append("category = %s")
        params.append(category)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at DESC LIMIT %s"
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
        LIMIT %s
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
        VALUES ('venture_brief', 'Venture Brief Report', %s)
    """, (json.dumps(report),))
    
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
