"""Normalized capability mapping for MCP tools.

SERVER != TOOL != CAPABILITY.  A tool may implement multiple capabilities.

MVP policy (spec): mappings initially curated + heuristic + optionally LLM-reviewed.
Heuristic mapping is keyword-based on tool name/description; curated overrides
carry confidence 1.0.
"""

from __future__ import annotations

import re

# Normalized capability vocabulary (spec: web.search, repository.issue.create,
# browser.navigate, database.query, filesystem.read + a pragmatic superset).
CAPABILITIES = [
    "web.search",
    "web.fetch",
    "web.scrape",
    "browser.navigate",
    "browser.automate",
    "repository.issue.create",
    "repository.issue.read",
    "repository.pull.create",
    "repository.read",
    "database.query",
    "filesystem.read",
    "filesystem.write",
    "memory.store",
    "memory.recall",
    "search.vector",
    "messaging.send",
    "email.send",
    "calendar.read",
    "cloud.provision",
    "code.execute",
    "math.compute",
    "time.now",
    "image.generate",
    "pdf.read",
]

# Curated overrides: (server_id|tool_name) -> [(capability, confidence, method)]
CURATED: dict[str, list[tuple[str, float, str]]] = {
    "mock:echo": [("math.compute", 1.0, "curated")],
    "mock:add": [("math.compute", 1.0, "curated")],
    "mock:read_doc": [("filesystem.read", 1.0, "curated"), ("pdf.read", 0.6, "curated")],
    "mock:list_tree": [("filesystem.read", 1.0, "curated")],
    "mock:web_search": [("web.search", 1.0, "curated")],
    "mock:mutate_state": [("memory.store", 0.8, "curated")],
    "npm:@modelcontextprotocol/server-filesystem:read_file": [("filesystem.read", 1.0, "curated")],
    "npm:@modelcontextprotocol/server-filesystem:read_directory": [("filesystem.read", 1.0, "curated")],
    "npm:@modelcontextprotocol/server-filesystem:write_file": [("filesystem.write", 1.0, "curated")],
    "npm:@modelcontextprotocol/server-github:create_issue": [("repository.issue.create", 1.0, "curated")],
    "npm:@modelcontextprotocol/server-github:search_repositories": [("repository.read", 1.0, "curated"), ("web.search", 0.5, "curated")],
    "npm:@modelcontextprotocol/server-fetch:fetch": [("web.fetch", 1.0, "curated")],
    "npm:@modelcontextprotocol/server-memory:create_entities": [("memory.store", 1.0, "curated")],
    "npm:@modelcontextprotocol/server-memory:search_nodes": [("memory.recall", 1.0, "curated")],
    "npm:@modelcontextprotocol/server-puppeteer:navigate": [("browser.navigate", 1.0, "curated")],
    "npm:@modelcontextprotocol/server-puppeteer:screenshot": [("browser.automate", 0.8, "curated")],
    "git:mcpsqlite:mcp_query": [("database.query", 1.0, "curated")],
}

_KEYWORD_MAP: list[tuple[str, list[str], float]] = [
    ("web.search", ["search", "web_search", "internet search"], 0.75),
    ("web.fetch", ["fetch", "http", "url", "download", "webpage"], 0.7),
    ("web.scrape", ["scrape", "crawl", "extract"], 0.75),
    ("browser.navigate", ["navigate", "browser", "goto", "open page"], 0.7),
    ("browser.automate", ["click", "screenshot", "automate", "dom"], 0.6),
    ("repository.issue.create", ["issue", "create_issue", "open_issue"], 0.8),
    ("repository.issue.read", ["list_issue", "get_issue", "comment"], 0.7),
    ("repository.pull.create", ["pull", "merge request", "pr"], 0.75),
    ("repository.read", ["repo", "repository", "github", "gitlab", "code", "file_content"], 0.6),
    ("database.query", ["query", "sql", "database", "select", "table"], 0.75),
    ("filesystem.read", ["read_file", "read_directory", "readfile", "ls", "list_dir", "open"], 0.7),
    ("filesystem.write", ["write_file", "create_file", "edit", "upload", "save"], 0.7),
    ("memory.store", ["memory", "remember", "store", "create_entit", "save"], 0.6),
    ("memory.recall", ["recall", "search_node", "remembered", "retrieve"], 0.7),
    ("search.vector", ["vector", "embedding", "semantic", "similarity"], 0.8),
    ("messaging.send", ["send_message", "slack", "telegram", "whatsapp", "discord", "post"], 0.7),
    ("email.send", ["send_email", "mail", "gmail"], 0.75),
    ("calendar.read", ["calendar", "event", "schedule"], 0.75),
    ("cloud.provision", ["ec2", "instance", "provision", "deploy", "k8s", "kubernetes", "aws"], 0.6),
    ("code.execute", ["execute", "run_code", "sandbox", "shell", "terminal", "bash"], 0.65),
    ("math.compute", ["add", "subtract", "multiply", "calculate", "math"], 0.7),
    ("time.now", ["time", "date", "now", "clock"], 0.7),
    ("image.generate", ["generate_image", "image", "dalle", "draw"], 0.6),
    ("pdf.read", ["pdf", "document"], 0.6),
]


def map_tool_capabilities(server_id: str, tool_name: str, description: str) -> list[tuple[str, float, str]]:
    """Return [(capability_id, confidence, method)] for one tool."""
    key = f"{server_id}:{tool_name}"
    if key in CURATED:
        return CURATED[key]

    haystack = f"{tool_name} {description}".lower()
    hits: list[tuple[str, float, str]] = []
    for cap, keywords, conf in _KEYWORD_MAP:
        if any(re.search(rf"\b{re.escape(kw)}\b", haystack) for kw in keywords):
            hits.append((cap, conf, "heuristic"))

    # de-duplicate keeping highest confidence
    best: dict[str, tuple[float, str]] = {}
    for cap, conf, method in hits:
        if cap not in best or conf > best[cap][0]:
            best[cap] = (conf, method)
    return [(cap, conf, method) for cap, (conf, method) in sorted(best.items())]


def map_all_tools(server_id: str, tool_name: str, description: str, tool_id: str) -> None:
    """Persist capability mappings for a single tool."""
    from . import db
    mappings = map_tool_capabilities(server_id, tool_name, description)
    db.set_tool_capabilities(tool_id, mappings)


def capability_implementations(capability_id: str) -> list[dict]:
    """Servers + tools implementing a capability, joined with names."""
    from . import db
    conn = db.get_conn()
    rows = conn.execute(
        """SELECT s.server_id, s.name AS server_name, s.transport, t.tool_id, t.name AS tool_name,
                  t.safety_class, t.schema_sha256, tc.confidence, tc.mapping_method
           FROM tool_capabilities tc
           JOIN tools t ON t.tool_id = tc.tool_id
           JOIN servers s ON s.server_id = t.server_id
           WHERE tc.capability_id=?
           ORDER BY tc.confidence DESC, s.server_id""",
        (capability_id,),
    ).fetchall()
    return [dict(r) for r in rows]