"""Local mock MCP server (FastMCP) used for deterministic harness + API tests.

Tools deliberately span the safety spectrum:

  echo(text)      READ_ONLY  (pure echo)
  add(a, b)       READ_ONLY  (pure math)
  read_doc(path)  READ_ONLY  (returns canned content; name triggers filesystem.read)
  list_tree()     READ_ONLY  (canned directory listing)
  web_search(q)   READ_ONLY  (canned fake result)
  mutate_state()  MUTATING   (harness must NEVER invoke this)

Run:  python -m tests.mock_mcp_server   (stdio transport)
"""

from __future__ import annotations

import json
import os

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover
    raise SystemExit("mcp SDK unavailable; pip install mcp")

_STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mock_state.json"
)

mcp = FastMCP("mock-mcp", instructions="Deterministic mock for MCPTruth harness tests.")


@mcp.tool()
def echo(text: str) -> dict:
    """Echo back the provided text (read-only, deterministic)."""
    return {"echo": text}


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers (read-only, deterministic)."""
    return a + b


@mcp.tool()
def read_doc(path: str) -> str:
    """Read a document (read-only mock; returns canned content)."""
    return "MCPTruth mock document content."


@mcp.tool()
def list_tree() -> list[str]:
    """List a directory tree (read-only mock)."""
    return ["data/test-doc.txt", "data/notes/"]


@mcp.tool()
def web_search(query: str) -> dict:
    """Fake web search (read-only mock; no network)."""
    return {"query": query, "results": [{"title": "Model Context Protocol", "url": "https://modelcontextprotocol.io"}]}


@mcp.tool()
def mutate_state(key: str, value: str) -> dict:
    """Persist a key/value to local state (MUTATING — never invoked by probes)."""
    state = {}
    if os.path.exists(_STATE_FILE):
        with open(_STATE_FILE) as f:
            state = json.load(f)
    state[key] = value
    with open(_STATE_FILE, "w") as f:
        json.dump(state, f)
    return {"stored": key, "value": value}


if __name__ == "__main__":
    mcp.run()  # stdio