"""MCPTruth REST API (spec §API).

GET /health
GET /v1/stats
GET /v1/coverage
GET /v1/evidence/{id}
GET /v1/servers
GET /v1/servers/{id}
GET /v1/servers/{id}/tools
GET /v1/servers/{id}/history
GET /v1/tools
GET /v1/capabilities/{capability}/implementations
GET /v1/healthiest
GET /v1/schema-changes
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from . import __version__, db, reducer, capabilities as caps
from .oracle import now_iso
from .schemas import (
    CapabilityImplementationOut, CoverageOut, HealthOut, HealthiestOut,
    MeasurementOut, OracleEnvelope, ProbeRunOut, SchemaChangeOut, ServerOut,
    StatsOut, ToolOut, WindowOut,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield
    db.close_conn()


app = FastAPI(
    title="MCPTruth",
    description="Continuously test whether MCP servers actually work.",
    version=__version__,
    lifespan=lifespan,
)


def _wrapped_server(server: dict, window: Optional[dict] = None) -> dict:
    out = dict(server)
    out["window"] = window
    return out


def _latest_window_map() -> dict[str, dict]:
    windows = db.get_latest_windows()
    return {w["server_id"]: w for w in windows}


# ---------------------------------------------------------------------------
# universal endpoints (spec §0)
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthOut)
def health():
    return HealthOut(
        status="ok",
        ts=now_iso(),
        db_observations=db.stats()["observations"],
        db_servers=db.stats()["servers_tracked"],
    )


@app.get("/v1/stats", response_model=StatsOut)
def v1_stats():
    return db.stats()


@app.get("/v1/coverage", response_model=CoverageOut)
def v1_coverage():
    return db.coverage()


@app.get("/v1/evidence/{observation_id}", response_model=OracleEnvelope)
def v1_evidence(observation_id: str):
    env = db.get_observation(observation_id)
    if env is None:
        raise HTTPException(status_code=404, detail="observation not found")
    return env


# ---------------------------------------------------------------------------
# servers
# ---------------------------------------------------------------------------

@app.get("/v1/servers", response_model=list[ServerOut])
def v1_servers(status: Optional[str] = None, deep: Optional[int] = None):
    windows = _latest_window_map()
    servers = db.list_servers(status=status, deep_test=deep)
    return [_wrapped_server(s, windows.get(s["server_id"])) for s in servers]


@app.get("/v1/servers/{server_id}", response_model=ServerOut)
def v1_server(server_id: str):
    server = db.get_server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="server not found")
    windows = _latest_window_map()
    return _wrapped_server(server, windows.get(server_id))


@app.get("/v1/servers/{server_id}/tools", response_model=list[ToolOut])
def v1_server_tools(server_id: str):
    if db.get_server(server_id) is None:
        raise HTTPException(status_code=404, detail="server not found")
    return db.list_tools(server_id=server_id)


@app.get("/v1/servers/{server_id}/history", response_model=dict)
def v1_server_history(server_id: str, limit: int = Query(50, le=500)):
    if db.get_server(server_id) is None:
        raise HTTPException(status_code=404, detail="server not found")
    runs = db.get_probe_runs(server_id=server_id, limit=limit)
    measurements = db.get_measurements(server_id=server_id, limit=limit * 20)
    windows = db.get_windows_for_server(server_id, limit=100)
    observations = db.list_observations(subject_id=server_id, limit=limit * 10)
    return {
        "server_id": server_id,
        "probe_runs": [ProbeRunOut(**r).model_dump() for r in runs],
        "measurements": [MeasurementOut(**m).model_dump() for m in measurements],
        "windows": [WindowOut(**w).model_dump() for w in windows],
        "observations": observations,
    }


# ---------------------------------------------------------------------------
# tools + capabilities
# ---------------------------------------------------------------------------

@app.get("/v1/tools", response_model=list[ToolOut])
def v1_tools(server_id: Optional[str] = None, capability: Optional[str] = None,
             safety: Optional[str] = None):
    return db.list_tools(server_id=server_id, capability=capability, safety=safety)


@app.get("/v1/capabilities", response_model=list[dict])
def v1_capabilities_list():
    return db.list_capabilities()


@app.get("/v1/capabilities/{capability}/implementations", response_model=list[CapabilityImplementationOut])
def v1_capability_implementations(capability: str):
    impls = caps.capability_implementations(capability)
    if not impls:
        # 200 with empty list — a capability with zero implementations is a
        # valuable truth (coverage gap), not an error.
        pass
    return impls


# ---------------------------------------------------------------------------
# current state
# ---------------------------------------------------------------------------

@app.get("/v1/healthiest", response_model=list[HealthiestOut])
def v1_healthiest(limit: int = Query(20, le=100),
                  fresh_seconds: int = Query(900, le=86400),
                  require_deep: bool = False):
    return [
        HealthiestOut(
            rank=h["rank"],
            server_id=h["server"]["server_id"],
            name=h["server"]["name"],
            transport=h["server"]["transport"],
            deep_test=h["server"]["deep_test"],
            observed=WindowOut(**h["window"]),
            freshness_seconds=h["window"].get("freshness_seconds", 0),
        )
        for h in reducer.healthiest(limit=limit, fresh_seconds=fresh_seconds,
                                    require_deep=require_deep)
    ]


@app.get("/v1/schema-changes", response_model=list[SchemaChangeOut])
def v1_schema_changes(change_type: Optional[str] = None, limit: int = Query(100, le=500)):
    return db.list_schema_changes(limit=limit, change_type=change_type)


# ---------------------------------------------------------------------------
# errors as JSON
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("MCPTRUTH_PORT", "8000"))
    uvicorn.run("app.api:app", host="0.0.0.0", port=port, reload=False)