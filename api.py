"""VentureLab API server."""

from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(title="VentureLab API")


@app.get("/")
def root():
    return {
        "service": "VentureLab",
        "version": "1.0.0",
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ideas")
def list_ideas():
    import sqlite3
    conn = sqlite3.connect("data/venturelab.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ideas")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"count": count}


@app.post("/route")
def route_task(task: dict):
    from factory.system import VentureLabSystem
    system = VentureLabSystem()
    result = system.route_task(task.get("task_kind", "coding"), task.get("requirements", {}))
    return result
