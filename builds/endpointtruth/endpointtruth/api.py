"""FastAPI application: the EndpointTruth API (spec section 'API') plus the
shared Oracle substrate endpoints (spec section 0):

    GET /health
    GET /v1/stats
    GET /v1/coverage
    GET /v1/evidence/{id}
    GET /v1/endpoints
    GET /v1/endpoints/{id}
    GET /v1/endpoints/{id}/measurements
    GET /v1/endpoints/{id}/history
    GET /v1/resolve
    GET /v1/models/{model}/endpoints
    GET /v1/providers/{provider}/endpoints
    GET /v1/leaderboard?metric=ttft|tps|tool_success|json_success|success_rate
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from .aggregator import (DEFAULT_STALE_SECONDS, DEFAULT_WINDOW_SECONDS,
                         aggregate_windows, current_windows)
from .db import DB
from .resolve import resolve
from .schema import utcnow
from .state import current_state_map


def create_app(db_path: str = "data/endpointtruth.db",
               stale_after_seconds: int = DEFAULT_STALE_SECONDS,
               window_seconds: int = DEFAULT_WINDOW_SECONDS) -> FastAPI:
    app = FastAPI(title="EndpointTruth", version="0.1.0",
                  description="Continuously determine what an actual LLM serving endpoint can do right now.")
    db = DB(db_path)
    app.state.db = db
    app.state.stale_after_seconds = stale_after_seconds
    app.state.window_seconds = window_seconds

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "endpointtruth", "time": utcnow()}

    @app.get("/v1/stats")
    def stats():
        db_ = app.state.db
        runs = db_.conn.execute("SELECT status, COUNT(*) c FROM probe_runs GROUP BY status").fetchall()
        obs_state = db_.conn.execute(
            "SELECT state, COUNT(*) c FROM probe_measurements GROUP BY state").fetchall()
        return {
            "endpoints": db_.count_endpoints(),
            "probe_runs": db_.count_probe_runs(),
            "observations": db_.count_observations(),
            "windows": db_.conn.execute("SELECT COUNT(*) c FROM endpoint_windows").fetchone()["c"],
            "probe_runs_by_status": {r["status"]: r["c"] for r in runs},
            "observations_by_state": {r["state"]: r["c"] for r in obs_state},
            "time": utcnow(),
        }

    @app.get("/v1/coverage")
    def coverage():
        db_ = app.state.db
        eps = db_.list_endpoints()
        per_provider: dict[str, dict] = {}
        total = [0, 0]
        for ep in eps:
            p = per_provider.setdefault(ep.provider_id, {"endpoints": 0, "with_observations": 0})
            p["endpoints"] += 1
            n = db_.conn.execute(
                "SELECT COUNT(*) c FROM probe_measurements WHERE subject_id=?",
                (ep.endpoint_id,)).fetchone()["c"]
            if n > 0:
                p["with_observations"] += 1
                total[0] += 1
            total[1] += 1
        probe_types = [r["probe_type"] for r in db_.conn.execute(
            "SELECT DISTINCT probe_type FROM probe_runs ORDER BY probe_type").fetchall()]
        return {
            "endpoints_total": total[1],
            "endpoints_with_observations": total[0],
            "probe_types_observed": probe_types,
            "probe_types_total": 7,  # six inference probes + discovery
            "providers": {k: v for k, v in sorted(per_provider.items())},
            "time": utcnow(),
        }

    @app.get("/v1/evidence/{artifact_id}")
    def evidence(artifact_id: str):
        import glob
        from pathlib import Path
        hits = glob.glob(f"data/runs/*/artifacts/{artifact_id}")
        if not hits:
            hits = glob.glob(f"data/runs/*/artifacts/*{artifact_id[:8]}*")
        if not hits:
            raise HTTPException(status_code=404, detail="artifact not found")
        p = Path(hits[0])
        return {"artifact_id": artifact_id, "path": str(p),
                "sha256": p.stem.split("-")[-1],
                "content": p.read_text(errors="replace")[:50000]}

    @app.get("/v1/endpoints")
    def list_eps(provider: Optional[str] = None, model: Optional[str] = None,
                 include_advertised_only: Optional[bool] = Query(default=None, alias="include_advertised_only")):
        db_ = app.state.db
        eps = db_.list_endpoints(provider=provider, model=model)
        states = current_state_map(db_, stale_after_seconds=app.state.stale_after_seconds)
        out = []
        for ep in eps:
            st = states.get(ep.endpoint_id, {})
            d = {
                "endpoint_id": ep.endpoint_id,
                "provider": ep.provider_id,
                "model_id": ep.model_id,
                "region": ep.region,
                "deployment_variant": ep.deployment_variant,
                "advertised": {
                    "context_tokens": ep.advertised_context_tokens,
                    "tools": ep.tools_advertised,
                    "json": ep.json_advertised,
                    "pricing": ep.pricing,
                },
                "state": st.get("state", "UNKNOWN"),
                "freshness_seconds": st.get("freshness_seconds"),
                "observed": st.get("observed", {}),
            }
            out.append(d)
        if include_advertised_only is True:
            out = [d for d in out
                   if d["observed"].get("ttft_ms_p50") is not None
                   or d["observed"].get("output_tps_p50") is not None
                   or d["observed"].get("success_rate") is not None]
        return {"endpoints": out, "count": len(out)}

    def _get_ep(endpoint_id: str):
        ep = app.state.db.get_endpoint(endpoint_id)
        if ep is None:
            raise HTTPException(status_code=404, detail="endpoint not found")
        return ep

    @app.get("/v1/endpoints/{endpoint_id}")
    def get_ep(endpoint_id: str):
        ep = _get_ep(endpoint_id)
        st = current_state_map(app.state.db, stale_after_seconds=app.state.stale_after_seconds).get(endpoint_id, {})
        return {
            "endpoint_id": ep.endpoint_id,
            "provider": ep.provider_id,
            "model_id": ep.model_id,
            "provider_model_name": ep.provider_model_name,
            "base_url": ep.base_url,
            "region": ep.region,
            "deployment_variant": ep.deployment_variant,
            "advertised": {
                "context_tokens": ep.advertised_context_tokens,
                "tools": ep.tools_advertised,
                "json": ep.json_advertised,
                "pricing": ep.pricing,
            },
            "state": st.get("state", "UNKNOWN"),
            "freshness_seconds": st.get("freshness_seconds"),
            "observed": st.get("observed", {}),
        }

    @app.get("/v1/endpoints/{endpoint_id}/measurements")
    def measurements(endpoint_id: str, metric: Optional[str] = None, limit: int = Query(default=200, le=5000)):
        _get_ep(endpoint_id)
        rows = app.state.db.measurements_for_endpoint(endpoint_id, metric=metric, limit=limit)
        return {"endpoint_id": endpoint_id, "measurements": [dict(r) for r in rows], "count": len(rows)}

    @app.get("/v1/endpoints/{endpoint_id}/history")
    def history(endpoint_id: str, metric: Optional[str] = None, limit: int = Query(default=500, le=10000)):
        _get_ep(endpoint_id)
        rows = app.state.db.history_for_endpoint(endpoint_id, metric=metric, limit=limit)
        return {"endpoint_id": endpoint_id, "history": [dict(r) for r in rows], "count": len(rows)}

    @app.get("/v1/resolve")
    def api_resolve(capability: str = "chat", tools: bool = False,
                    min_context: Optional[int] = None, limit: int = 5):
        return resolve(app.state.db, capability=capability, tools=tools,
                       min_context=min_context, limit=limit,
                       stale_after_seconds=app.state.stale_after_seconds)

    @app.get("/v1/models/{model}/endpoints")
    def model_endpoints(model: str):
        eps = app.state.db.list_endpoints(model=model)
        if not eps:
            raise HTTPException(status_code=404, detail="no endpoints for model")
        return {"model": model, "endpoints": [e.endpoint_id for e in eps], "count": len(eps)}

    @app.get("/v1/providers/{provider}/endpoints")
    def provider_endpoints(provider: str):
        eps = app.state.db.list_endpoints(provider=provider)
        return {"provider": provider, "endpoints": [e.endpoint_id for e in eps], "count": len(eps)}

    @app.get("/v1/leaderboard")
    def leaderboard(metric: str = "ttft", limit: int = Query(default=20, le=200)):
        states = current_state_map(app.state.db, stale_after_seconds=app.state.stale_after_seconds)
        col = {"ttft": "ttft_ms_p50", "tps": "output_tps_p50",
               "tool_success": "tool_success_rate", "json_success": "json_success_rate",
               "success_rate": "success_rate"}.get(metric)
        if col is None:
            raise HTTPException(status_code=400,
                                detail=f"unknown metric {metric!r}; choose ttft|tps|tool_success|json_success|success_rate")
        rows = []
        for eid, st in sorted(states.items()):
            v = (st.get("observed") or {}).get(col)
            if v is None or st["state"] == "STALE":
                continue
            rows.append({"endpoint_id": eid, "metric": metric, "value": v,
                         "state": st["state"], "freshness_seconds": st["freshness_seconds"]})
        lower_better = metric == "ttft"
        rows.sort(key=lambda r: r["value"], reverse=not lower_better)
        return {"metric": metric, "leaderboard": rows[:limit], "count": len(rows),
                "total": len(app.state.db.list_endpoints())}

    return app


def app_factory():
    db_path = os.environ.get("ENDPOINTTRUTH_DB", "data/endpointtruth.db")
    stale = int(os.environ.get("ENDPOINTTRUTH_STALE_SECONDS", str(DEFAULT_STALE_SECONDS)))
    win = int(os.environ.get("ENDPOINTTRUTH_WINDOW_SECONDS", str(DEFAULT_WINDOW_SECONDS)))
    return create_app(db_path, stale_after_seconds=stale, window_seconds=win)


app = app_factory()