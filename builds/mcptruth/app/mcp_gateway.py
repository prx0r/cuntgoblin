"""MCPTruth's own MCP interface (spec §API / MCP).

Exposes the REST surface as MCP tools so agents can query MCPTruth from within
their own MCP toolchain:

  mcp_search        full-text search over tracked servers
  mcp_health        current health window for one server
  capability_search servers+tools implementing a normalized capability
  tool_get          tool details + schema fingerprint
  healthiest        current-state ranking (optionally deep-tested only)

Run:  python -m app.mcp_gateway        (stdio transport)
"""

from __future__ import annotations

import os
from typing import Any, Optional

from . import db, reducer, capabilities as caps

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover
    FastMCP = None  # type: ignore

SERVER_NAME = "mcptruth"

_FAST_MCP_DOC = """MCPTruth product gateway. Query the MCP-server truth database:
mcp_search (servers), mcp_health (one server's current window), healthiest
(current ranking), capability_search (servers implementing a capability),
tool_get (tool schema fingerprint)."""


def _mcp() -> Optional[Any]:
    if FastMCP is None:
        raise RuntimeError("mcp SDK unavailable; pip install mcp")
    mcp = FastMCP(
        SERVER_NAME,
        instructions=_FAST_MCP_DOC,
    )

    @mcp.tool()
    def mcp_search(query: str, limit: int = 20) -> list[dict]:
        """Search tracked MCP servers by id/name/description."""
        q = query.lower()
        hits = []
        for s in db.list_servers():
            hay = f"{s['server_id']} {s['name']} {s['description']} {s['source_registry']}".lower()
            if q in hay:
                hits.append({
                    "server_id": s["server_id"], "name": s["name"],
                    "transport": s["transport"], "status": s["status"],
                    "deep_test": s["deep_test"], "auth_scheme": s["auth_scheme"],
                    "source_registry": s["source_registry"], "source_url": s["source_url"],
                })
            if len(hits) >= limit:
                break
        return hits

    @mcp.tool()
    def mcp_health(server_id: str) -> dict:
        """Return the current health window for one server (or {} if absent)."""
        srv = db.get_server(server_id)
        if srv is None:
            return {"error": "server not found"}
        windows = db.get_windows_for_server(server_id, limit=20)
        latest = windows[0] if windows else None
        runs = db.get_probe_runs(server_id=server_id, limit=5)
        return {
            "server_id": server_id,
            "name": srv["name"],
            "status": srv["status"],
            "current_window": latest,
            "recent_runs": [
                {"probe_run_id": r["probe_run_id"], "probe_type": r["probe_type"],
                 "status": r["status"], "error_class": r["error_class"],
                 "started_at": r["started_at"]}
                for r in runs
            ],
        }

    @mcp.tool()
    def healthiest(limit: int = 10, require_deep: bool = False) -> list[dict]:
        """Current-state ranking of the healthiest MCP servers."""
        return [
            {
                "rank": h["rank"],
                "server_id": h["server"]["server_id"],
                "name": h["server"]["name"],
                "transport": h["server"]["transport"],
                "freshness_seconds": h["window"].get("freshness_seconds", 0),
                "connection_ms_p50": h["window"].get("connection_ms_p50"),
                "invocation_ms_p50": h["window"].get("invocation_ms_p50"),
                "invocation_success_rate": h["window"].get("invocation_success_rate"),
                "schema_break_count": h["window"].get("schema_break_count", 0),
            }
            for h in reducer.healthiest(limit=limit, require_deep=require_deep)
        ]

    @mcp.tool()
    def capability_search(capability: str) -> list[dict]:
        """Servers+tools implementing a normalized capability (e.g. web.search)."""
        return [
            {
                "server_id": i["server_id"], "server_name": i["server_name"],
                "tool_name": i["tool_name"], "safety_class": i["safety_class"],
                "confidence": i["confidence"], "mapping_method": i["mapping_method"],
            }
            for i in caps.capability_implementations(capability)
        ]

    @mcp.tool()
    def tool_get(server_id: str, tool_name: str) -> dict:
        """Return one tool's details + schema fingerprint for a server."""
        tool_id = db._tool_id(server_id, tool_name)
        t = db.get_tool(tool_id)
        if t is None:
            return {"error": "tool not found"}
        return {
            "tool_id": t["tool_id"], "server_id": t["server_id"], "name": t["name"],
            "description": t["description"], "safety_class": t["safety_class"],
            "schema_sha256": t["schema_sha256"], "schema_token_count": t["schema_token_count"],
            "first_seen": t["first_seen"], "last_seen": t["last_seen"],
            "input_schema": t["input_schema"], "capabilities": t["capabilities"],
        }

    @mcp.tool()
    def schema_changes(limit: int = 20) -> list[dict]:
        """Recent schema fingerprints (proxy for breaking API evolution)."""
        return db.list_schema_changes(limit=limit)

    return mcp


def run_stdio() -> None:
    if FastMCP is None:
        raise RuntimeError("mcp SDK unavailable; pip install mcp")
    mcp = _mcp()
    mcp.run()  # stdio transport by default


if __name__ == "__main__":
    run_stdio()