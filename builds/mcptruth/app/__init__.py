"""MCPTruth — continuously test whether MCP servers actually work.

Track ~50 MCP servers, deeply probe 10-20: existence, transport, reachability,
initialize, tools/list, schema validity, token footprint, auth, latency,
read-only invocation success, and breaking schema changes.

Oracle-compatible evidence envelope throughout (see specs/mcptruth/architecture.md).
"""

__version__ = "0.1.0"