"""VentureLab MCP server — official SDK v2."""

from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

mcp = MCPServer("VentureLab")

_system = None


def _get_system():
    if _system is None:
        from factory.system import VentureLabSystem
        global _system
        _system = VentureLabSystem()
    return _system


@mcp.tool()
def venturelab_get_status() -> dict[str, Any]:
    """Get VentureLab system status."""
    return _get_system().get_status()


@mcp.tool()
def venturelab_route_task(
    task_kind: str,
    quality: float = 0.8,
) -> dict[str, Any]:
    """Route a task through the factory system."""
    return _get_system().route_task(task_kind, {"quality": quality})


@mcp.tool()
def venturelab_list_opportunities() -> dict[str, Any]:
    """List opportunities from the database."""
    import sqlite3
    conn = sqlite3.connect("data/venturelab.db")
    try:
        rows = conn.execute(
            "SELECT id, title, status FROM opportunities ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
        return {"opportunities": [{"id": r[0], "title": r[1], "status": r[2]} for r in rows]}
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        conn.close()
