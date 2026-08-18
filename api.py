"""VentureLab API server."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import sqlite3

from fastapi import FastAPI

from factory.db.migrate import migrate

_DB = "data/venturelab.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    migrate(_DB)
    yield


app = FastAPI(title="VentureLab API", lifespan=lifespan)


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
    conn = sqlite3.connect(_DB)
    try:
        count = conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
    except sqlite3.OperationalError:
        count = 0
    finally:
        conn.close()
    return {"count": count}


@app.post("/route")
def route_task(task: dict):
    from factory.system import VentureLabSystem
    system = VentureLabSystem()
    result = system.route_task(task.get("task_kind", "coding"), task.get("requirements", {}))
    return result
