"""app/api.py — FastAPI surface for AgentSLA.

Spec section 0 (shared substrate): GET /health, GET /v1/stats, GET /v1/coverage,
GET /v1/evidence/{id}.
Spec Product 2: POST /v1/profile, GET /v1/architectures,
GET /v1/architectures/{id}, GET /v1/architectures/{id}/sla, GET /v1/compare,
GET /v1/tasks/{class}/frontier.

All read endpoints derive from the SLA database (raw rows retained; summaries
computed on read). POST /v1/profile runs one real cell synchronously.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from .cost import run_totals
from .db import connect, table_names
from .dataset import TASK_CLASSES, task_spec
from .evidence import RunEnvelope
from .metrics import RunRow, knee_from_runs, sla_summary
from .runner import DB_PATH, run_cell
from .client import LLMClient

app = FastAPI(title="AgentSLA", version="0.1.0", description="Measure real cost, duration and success rate of agent tasks.")

_conn = None


def get_conn():
    global _conn
    if _conn is None:
        _conn = connect(DB_PATH)
    return _conn


def _env_credentials() -> tuple[str, str]:
    base_url = os.environ.get("OPENCODE_GO_BASE_URL", "")
    api_key = os.environ.get("OPENCODE_GO_API_KEY", "")
    if not base_url or not api_key:
        raise HTTPException(status_code=503, detail="OPENCODE_GO_BASE_URL / OPENCODE_GO_API_KEY not set")
    return base_url, api_key


def _arch_versions_rows():
    conn = get_conn()
    return conn.execute(
        """SELECT av.architecture_version_id, av.architecture_id, av.version, av.config_json,
                  COUNT(r.run_id) AS runs, COALESCE(SUM(r.success),0) AS successes
           FROM architecture_versions av
           LEFT JOIN runs r ON r.architecture_version_id = av.architecture_version_id
           GROUP BY av.architecture_version_id ORDER BY av.architecture_id""",
    ).fetchall()


@app.get("/health")
def health():
    conn = get_conn()
    tables = table_names(conn)
    return {"status": "ok", "db": str(DB_PATH), "tables": tables}


@app.get("/v1/stats")
def stats():
    conn = get_conn()
    def count(sql):
        return conn.execute(sql).fetchone()[0]
    return {
        "runs": count("SELECT COUNT(*) FROM runs"),
        "successful_runs": count("SELECT COUNT(*) FROM runs WHERE success=1"),
        "model_calls": count("SELECT COUNT(*) FROM model_calls"),
        "tool_calls": count("SELECT COUNT(*) FROM tool_calls"),
        "evaluations": count("SELECT COUNT(*) FROM evaluations"),
        "cost_events": count("SELECT COUNT(*) FROM cost_events"),
        "tasks": count("SELECT COUNT(*) FROM tasks"),
        "architectures": count("SELECT COUNT(*) FROM architectures"),
        "total_cost_usd": round(float(conn.execute("SELECT COALESCE(SUM(amount_usd),0) FROM cost_events").fetchone()[0]), 6),
        "cost_basis_mix": {
            "provider_reported": count("SELECT COUNT(*) FROM cost_events WHERE basis='provider_reported'"),
            "price_table_estimate": count("SELECT COUNT(*) FROM cost_events WHERE basis='price_table_estimate'"),
        },
    }


@app.get("/v1/coverage")
def coverage():
    """Coverage matrix: for every (task class × architecture) cell, n runs and successes."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT t.task_class, a.architecture_id, COUNT(r.run_id) AS n, COALESCE(SUM(r.success),0) AS successes
           FROM tasks t
           JOIN task_versions tv ON tv.task_id = t.task_id
           JOIN runs r ON r.task_version_id = tv.task_version_id
           JOIN architecture_versions av ON av.architecture_version_id = r.architecture_version_id
           JOIN architectures a ON a.architecture_id = av.architecture_id
           GROUP BY t.task_class, a.architecture_id ORDER BY t.task_class, a.architecture_id""",
    ).fetchall()
    classes = sorted(TASK_CLASSES)
    archs = sorted({r["architecture_id"] for r in rows})
    cells = {(r["task_class"], r["architecture_id"]): r for r in rows}
    def _cell(tc, ar):
        row = cells.get((tc, ar))
        return (int(row["n"] or 0), int(row["successes"] or 0)) if row else (0, 0)
    return {
        "task_classes": classes,
        "architectures": archs,
        "matrix": [
            {
                "task_class": tc,
                "architecture_id": ar,
                "runs": _cell(tc, ar)[0],
                "successes": _cell(tc, ar)[1],
            }
            for tc in classes for ar in archs
        ],
    }


@app.get("/v1/evidence/{run_id}")
def evidence(run_id: str):
    env = RunEnvelope(run_id)
    if not (env.dir / "run.json").exists():
        raise HTTPException(status_code=404, detail=f"no run envelope for {run_id}")
    return {
        "run_id": run_id,
        "manifest": env.read_run_json(),
        "events": env.read_events()[-200:],  # bounded; full file on disk
        "stdout_log": (env.dir / "stdout.log").read_text(encoding="utf-8")[-4000:],
    }


@app.get("/v1/runs/{run_id}")
def run_detail(run_id: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"unknown run {run_id}")
    detail = dict(row)
    detail["cost"] = run_totals(conn, run_id)
    return detail


@app.get("/v1/tasks")
def tasks():
    return {"task_classes": sorted(TASK_CLASSES), "specs": {k: task_spec(k) for k in TASK_CLASSES}}


@app.get("/v1/architectures")
def architectures():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM architectures ORDER BY architecture_id").fetchall()
    return {"architectures": [dict(r) for r in rows]}


@app.get("/v1/architectures/{architecture_id}")
def architecture_detail(architecture_id: str):
    conn = get_conn()
    arch = conn.execute("SELECT * FROM architectures WHERE architecture_id=?", (architecture_id,)).fetchone()
    if arch is None:
        raise HTTPException(status_code=404, detail=f"unknown architecture {architecture_id}")
    versions = conn.execute(
        "SELECT * FROM architecture_versions WHERE architecture_id=? ORDER BY version",
        (architecture_id,),
    ).fetchall()
    return {"architecture": dict(arch), "versions": [dict(v) for v in versions]}


def _runs_for_architecture(conn, architecture_id: str, task_class: str | None = None) -> list:
    query = """SELECT r.* FROM runs r
               JOIN architecture_versions av ON av.architecture_version_id = r.architecture_version_id
               JOIN task_versions tv ON tv.task_version_id = r.task_version_id
               JOIN tasks t ON t.task_id = tv.task_id
               WHERE av.architecture_id = ? AND r.status != 'running'"""
    params: list = [architecture_id]
    if task_class:
        query += " AND t.task_class = ?"
        params.append(task_class)
    query += " ORDER BY r.started_at"
    return conn.execute(query, params).fetchall()


def _to_run_rows(db_rows) -> list[RunRow]:
    return [
        RunRow(
            success=bool(r["success"]) if r["success"] is not None else False,
            cost_usd=float(r["cost_usd"] or 0.0),
            duration_seconds=float(r["duration_seconds"] or 0.0),
            input_tokens=int(r["input_tokens"] or 0),
            output_tokens=int(r["output_tokens"] or 0),
            tool_calls=int(r["tool_calls"] or 0),
            retries=int(r["retries"] or 0),
        )
        for r in db_rows
    ]


@app.get("/v1/architectures/{architecture_id}/sla")
def architecture_sla(architecture_id: str, task_class: str | None = Query(default=None)):
    conn = get_conn()
    rows = _runs_for_architecture(conn, architecture_id, task_class)
    summary = sla_summary(_to_run_rows(rows))
    basis_row = conn.execute(
        """SELECT c.basis, COUNT(*) AS n FROM cost_events c
           JOIN runs r ON r.run_id = c.run_id
           JOIN architecture_versions av ON av.architecture_version_id = r.architecture_version_id
           WHERE av.architecture_id = ? GROUP BY c.basis""",
        (architecture_id,),
    ).fetchall()
    if not basis_row:
        basis = "none"
    else:
        basis = "mixed" if len(basis_row) > 1 else basis_row[0]["basis"]
    return {
        "architecture_id": architecture_id,
        "task_class": task_class,
        "n": summary.n,
        "successes": summary.successes,
        "success_rate": summary.success_rate,
        "success_rate_ci": list(summary.success_rate_ci),
        "cost_per_attempt_usd": summary.cost_per_attempt,
        "cost_per_success_usd": summary.cost_per_success,
        "duration_per_success_seconds": summary.duration_per_success,
        "tokens_per_success": summary.tokens_per_success,
        "tool_calls_per_success": summary.tool_calls_per_success,
        "retry_rate": summary.retry_rate,
        "efficiency": summary.efficiency,
        "total_cost_usd": summary.total_cost_usd,
        "cost_basis": basis,
        "insufficient_evidence": summary.insufficient_evidence,
    }


@app.get("/v1/compare")
def compare(task_class: str, architectures: str = Query(default="")):
    ids = [a for a in architectures.split(",") if a] if architectures else None
    conn = get_conn()
    selected = ids or [
        r["architecture_id"] for r in conn.execute("SELECT DISTINCT architecture_id FROM architectures").fetchall()
    ]
    out = {}
    for aid in selected:
        rows = _runs_for_architecture(conn, aid, task_class)
        s = sla_summary(_to_run_rows(rows))
        out[aid] = {
            "n": s.n, "successes": s.successes, "success_rate": s.success_rate,
            "wilson_lb": s.success_rate_ci[0],
            "cost_per_attempt_usd": s.cost_per_attempt,
            "cost_per_success_usd": s.cost_per_success,
            "duration_per_success_seconds": s.duration_per_success,
            "efficiency": s.efficiency,
            "insufficient_evidence": s.insufficient_evidence,
        }
    return {"task_class": task_class, "compare": out}


@app.get("/v1/tasks/{task_class}/frontier")
def frontier(task_class: str, min_success: float = Query(default=0.8, ge=0.0, le=1.0)):
    if task_class not in TASK_CLASSES:
        raise HTTPException(status_code=404, detail=f"unknown task class {task_class}")
    conn = get_conn()
    grouped = []
    for row in conn.execute(
        "SELECT DISTINCT architecture_id FROM architectures ORDER BY architecture_id"
    ).fetchall():
        aid = row["architecture_id"]
        rows = _runs_for_architecture(conn, aid, task_class)
        if not rows:
            continue
        s = sla_summary(_to_run_rows(rows))
        grouped.append((aid, s))
    if not grouped:
        return {"status": "INSUFFICIENT_EVIDENCE", "task_class": task_class, "min_success": min_success,
                "candidates": []}
    return {"task_class": task_class, "min_success": min_success,
            **knee_from_runs(grouped, min_success)}


@app.post("/v1/profile")
def profile(payload: dict):
    """Run one cell synchronously: task_class × architecture_id × 1 attempt.

    Payload: {"task_class": "coding.patch", "architecture_id": "single_agent",
              "model": "..." (optional), "max_steps": 6 (optional)}
    """
    task_class = payload.get("task_class", "")
    architecture_id = payload.get("architecture_id", "")
    if task_class not in TASK_CLASSES:
        raise HTTPException(status_code=400, detail=f"unknown task_class {task_class}")
    if architecture_id not in {"single_agent", "worker_verifier", "planner_worker", "parallel_candidates_judge"}:
        raise HTTPException(status_code=400, detail=f"unknown architecture_id {architecture_id}")

    base_url, api_key = _env_credentials()
    model = payload.get("model") or os.environ.get("AGENTSLA_MODEL", "deepseek-v4-flash")
    client = LLMClient(base_url, api_key, model, timeout=90, max_retries=2)
    arch_config = {
        "components": [
            {"role": "worker", "model": model, "max_steps": int(payload.get("max_steps", 6))}
        ],
        "max_steps": int(payload.get("max_steps", 6)),
    }
    if architecture_id == "worker_verifier":
        arch_config["components"].append({"role": "verifier", "model": model})
        arch_config["max_rounds"] = int(payload.get("max_rounds", 2))
    if architecture_id == "planner_worker":
        arch_config["components"] = [
            {"role": "planner", "model": model},
            {"role": "worker", "model": model, "max_steps": int(payload.get("max_steps", 6))},
        ]
    if architecture_id == "parallel_candidates_judge":
        arch_config["components"] = [
            {"role": "worker", "model": model, "max_steps": int(payload.get("max_steps", 6))},
        ]
        arch_config["n_candidates"] = int(payload.get("n_candidates", 3))

    conn = get_conn()
    manifest = run_cell(
        conn, benchmark_id=f"profile-{os.getpid()}",
        task_class=task_class, architecture_id=architecture_id,
        arch_config=arch_config, client=client, attempt=1,
        base_url=base_url, git_sha="",
    )
    client.close()
    return JSONResponse(status_code=200, content=manifest)


def run() -> None:
    import uvicorn

    port = int(os.environ.get("AGENTSLA_PORT", "8790"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run()