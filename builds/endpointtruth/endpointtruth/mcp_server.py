"""MCP server: endpoint_search / endpoint_compare / endpoint_resolve /
endpoint_history (spec section 'MCP'). Runs over stdio using the `mcp` SDK
(FastMCP). Fallback to a hand-rolled JSON-RPC stdio server when the SDK is
unavailable is provided by cli.py (--no-sdk).
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Optional

from .db import DB
from .resolve import resolve


def _default_db() -> DB:
    path = os.environ.get("ENDPOINTTRUTH_DB", "data/endpointtruth.db")
    return DB(path)


def build_tools(db: DB) -> dict[str, dict[str, Any]]:
    """Tool implementations as plain callables returning JSON-serializable
    dicts; used by both the FastMCP registration and the JSON-RPC fallback."""

    async def endpoint_search(query: str = "", provider: str = "", model: str = "",
                              limit: int = 20) -> dict:
        eps = db.list_endpoints(provider=provider or None, model=model or None)
        hits = []
        for ep in eps:
            hay = f"{ep.endpoint_id} {ep.model_id} {ep.provider_id}"
            if query and query.lower() not in hay.lower():
                continue
            hits.append({"endpoint_id": ep.endpoint_id, "provider": ep.provider_id,
                         "model_id": ep.model_id, "deployment_variant": ep.deployment_variant,
                         "advertised_context": ep.advertised_context_tokens,
                         "tools_advertised": ep.tools_advertised,
                         "json_advertised": ep.json_advertised,
                         "pricing": ep.pricing})
        return {"query": query, "results": hits[:limit], "count": len(hits[:limit])}

    async def endpoint_compare(a: str, b: str) -> dict:
        from .state import current_state_map
        out = {}
        states = current_state_map(db)
        for eid in (a, b):
            ep = db.get_endpoint(eid)
            if ep is None:
                out[eid] = {"error": "unknown endpoint"}
                continue
            out[eid] = {"endpoint_id": eid, "provider": ep.provider_id,
                        "model_id": ep.model_id,
                        "advertised": {"context": ep.advertised_context_tokens,
                                       "tools": ep.tools_advertised,
                                       "json": ep.json_advertised,
                                       "pricing": ep.pricing},
                        "state": states.get(eid, {}).get("state", "UNKNOWN"),
                        "observed": states.get(eid, {}).get("observed", {})}
        return {"compare": out}

    async def endpoint_resolve(capability: str = "chat", tools: bool = False,
                               min_context: Optional[int] = None, limit: int = 5) -> dict:
        return resolve(db, capability=capability, tools=tools,
                       min_context=min_context, limit=limit)

    async def endpoint_history(endpoint_id: str, metric: str = "", limit: int = 100) -> dict:
        ep = db.get_endpoint(endpoint_id)
        if ep is None:
            return {"error": "unknown endpoint", "endpoint_id": endpoint_id}
        rows = db.history_for_endpoint(endpoint_id, metric=metric or None, limit=limit)
        return {"endpoint_id": endpoint_id, "metric": metric or None,
                "history": [{k: r[k] for k in ("predicate", "value_numeric", "value_text",
                                               "state", "observed_at", "method_id")}
                            for r in rows], "count": len(rows)}

    return {
        "endpoint_search": endpoint_search,
        "endpoint_compare": endpoint_compare,
        "endpoint_resolve": endpoint_resolve,
        "endpoint_history": endpoint_history,
    }


def run_fastmcp(db: Optional[DB] = None) -> None:
    """Register tools with the mcp SDK FastMCP server and run stdio."""
    from mcp.server.fastmcp import FastMCP
    db = db or _default_db()
    mcp = FastMCP("endpointtruth")
    tools = build_tools(db)

    @mcp.tool()
    async def endpoint_search(query: str = "", provider: str = "", model: str = "", limit: int = 20) -> dict:
        return await tools["endpoint_search"](query=query, provider=provider,
                                              model=model, limit=limit)

    @mcp.tool()
    async def endpoint_compare(a: str, b: str) -> dict:
        return await tools["endpoint_compare"](a=a, b=b)

    @mcp.tool()
    async def endpoint_resolve(capability: str = "chat", tools: bool = False,
                               min_context: Optional[int] = None, limit: int = 5) -> dict:
        return await tools["endpoint_resolve"](capability=capability, tools=tools,
                                               min_context=min_context, limit=limit)

    @mcp.tool()
    async def endpoint_history(endpoint_id: str, metric: str = "", limit: int = 100) -> dict:
        return await tools["endpoint_history"](endpoint_id=endpoint_id,
                                               metric=metric, limit=limit)

    mcp.run(transport="stdio")


def run_jsonrpc_stdio(db: Optional[DB] = None) -> None:
    """Minimal MCP stdio server (JSON-RPC 2.0) with no external SDK dependency.
    Implements initialize / tools/list / tools/call / notifications.ping."""
    db = db or _default_db()
    tools = build_tools(db)
    tool_names = list(tools.keys())
    import asyncio

    async def dispatch(msg: dict) -> Optional[dict]:
        method = msg.get("method", "")
        params = msg.get("params", {}) or {}
        rid = msg.get("id")
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": rid,
                    "result": {"protocolVersion": "2024-11-05",
                               "capabilities": {"tools": {}},
                               "serverInfo": {"name": "endpointtruth", "version": "0.1.0"}}}
        if method == "notifications/initialized":
            return None
        if method == "ping":
            return {"jsonrpc": "2.0", "id": rid, "result": {}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": rid,
                    "result": {"tools": [
                        {"name": n, "description": f"EndpointTruth MCP tool {n}",
                         "inputSchema": {"type": "object", "properties": {}}}
                        for n in tool_names]}}
        if method == "tools/call":
            name = params.get("name", "")
            args = params.get("arguments", {}) or {}
            if name not in tools:
                return {"jsonrpc": "2.0", "id": rid,
                        "error": {"code": -32602, "message": f"unknown tool {name}"}}
            try:
                result = await tools[name](**args)
            except Exception as e:  # noqa: BLE001
                result = {"error": str(e)}
            return {"jsonrpc": "2.0", "id": rid,
                    "result": {"content": [{"type": "text",
                                            "text": json.dumps(result, default=str)}],
                               "isError": False}}
        if rid is not None:
            return {"jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32601, "message": f"method not found: {method}"}}
        return None

    async def main():
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        writer = sys.stdout
        while True:
            line = await reader.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except Exception:
                continue
            resp = await dispatch(msg)
            if resp is not None:
                writer.write(json.dumps(resp) + "\n")
                writer.flush()

    asyncio.run(main())


def run(transport: str = "stdio", force_jsonrpc: bool = False) -> None:
    if force_jsonrpc:
        run_jsonrpc_stdio()
        return
    try:
        import mcp  # noqa: F401  (probe availability)
        run_fastmcp()
    except Exception:
        run_jsonrpc_stdio()