"""Reference shape using the official MCP Python SDK v2.

Pin the exact SDK in uv.lock and use its documented transport entrypoint.
"""
from __future__ import annotations
from typing import Any
from mcp.server import MCPServer

mcp = MCPServer("VentureLab")
SYSTEM = None

def system():
    if SYSTEM is None:
        raise RuntimeError("VentureLab system not initialized")
    return SYSTEM

@mcp.tool()
def venturelab_get_status() -> dict[str, Any]:
    return system().get_status()

@mcp.tool()
def venturelab_list_factories() -> list[dict[str, Any]]:
    return system().list_factories()

@mcp.tool()
def venturelab_submit_job(
    factory_type: str,
    task_kind: str,
    input: dict[str, Any],
    idempotency_key: str,
    budget_usd: float | None = None,
    quality_floor: float = .70,
) -> dict[str, Any]:
    return system().submit_job({
        "factory_type": factory_type,
        "task_kind": task_kind,
        "input": input,
        "idempotency_key": idempotency_key,
        "budget_usd": budget_usd,
        "quality_floor": quality_floor,
    })

@mcp.tool()
def venturelab_get_job(job_id: str) -> dict[str, Any] | None:
    return system().get_job(job_id)

# Keep transport bootstrapping in a tiny separate entrypoint and use the
# exact run/stdio/Streamable-HTTP API from the pinned v2 release.
