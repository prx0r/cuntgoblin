"""VentureLab MCP server."""

import json
from typing import Any


MCP_TOOLS = [
    {
        "name": "venturelab_list_ideas",
        "description": "List all ideas in the venture database",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Filter by category"},
                "limit": {"type": "integer", "description": "Max results", "default": 10}
            }
        }
    },
    {
        "name": "venturelab_route_task",
        "description": "Route a task through the factory system",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_kind": {"type": "string", "description": "Task type (coding_patch, research_synthesis, etc.)"},
                "quality": {"type": "number", "description": "Minimum quality (0-1)", "default": 0.8}
            },
            "required": ["task_kind"]
        }
    },
    {
        "name": "venturelab_get_status",
        "description": "Get system status",
        "inputSchema": {"type": "object", "properties": {}}
    }
]


def handle_mcp_request(method: str, params: dict) -> dict:
    """Handle MCP tool invocation."""
    if method == "tools/list":
        return {"tools": MCP_TOOLS}
    
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "venturelab_list_ideas":
            return handle_list_ideas(arguments)
        elif tool_name == "venturelab_route_task":
            return handle_route_task(arguments)
        elif tool_name == "venturelab_get_status":
            return handle_get_status()
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    return {"error": f"Unknown method: {method}"}


def handle_list_ideas(args: dict) -> dict:
    """Handle list_ideas tool."""
    import sqlite3
    conn = sqlite3.connect("data/venturelab.db")
    cur = conn.cursor()
    
    category = args.get("category")
    limit = args.get("limit", 10)
    
    if category:
        cur.execute("SELECT idea_id, idea, category FROM ideas WHERE category = ? LIMIT ?", (category, limit))
    else:
        cur.execute("SELECT idea_id, idea, category FROM ideas LIMIT ?", (limit,))
    
    ideas = [{"id": r[0], "idea": r[1], "category": r[2]} for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return {"content": [{"type": "text", "text": json.dumps(ideas, indent=2)}]}


def handle_route_task(args: dict) -> dict:
    """Handle route_task tool."""
    from factory.system import VentureLabSystem
    
    system = VentureLabSystem()
    result = system.route_task(
        args.get("task_kind", "coding"),
        {"quality": args.get("quality", 0.8)}
    )
    
    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


def handle_get_status() -> dict:
    """Handle get_status tool."""
    from factory.system import VentureLabSystem
    
    system = VentureLabSystem()
    status = system.get_status()
    
    return {"content": [{"type": "text", "text": json.dumps(status, indent=2)}]}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        method = sys.argv[1]
        params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        result = handle_mcp_request(method, params)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python server.py <method> [params]")
