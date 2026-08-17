"""Discovery: seed the tracked-server registry and resolve deep-test targets.

MVP policy (spec): track ~50 MCP servers; deeply test ~10-20.

The seed set is curated from the modelcontextprotocol GitHub org, the npm
@modelcontextprotocol scope, and notable community servers.  Each entry carries
its source registry + install/launch details so the harness can attempt a real
probe.  Servers that need auth or destructive rights are tracked but marked
deep_test=0 until a controlled test account exists.
"""

from __future__ import annotations

from typing import Optional

from . import db

NPX = "npx"
PY = "python3"
DOCKER = "docker"

# Each entry: (server_id, name, transport, command, args, registry, url, auth,
#              deep_test, description, version, install_command)
SEED: list[dict] = [
    # --- local/mock (always deep-testable, deterministic) -------------------
    dict(server_id="mock:mock-mcp", name="Mock MCP (local)", transport="stdio",
         command=None, args=["-m", "tests.mock_mcp_server"], registry="local",
         url="", auth="none", deep=1, version=None,
         desc="Local FastMCP mock used for deterministic harness tests."),
    # --- official modelcontextprotocol org (npm) ----------------------------
    dict(server_id="npm:@modelcontextprotocol/server-filesystem", name="Filesystem", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=1,
         version="0.6.2", desc="Filesystem access: read, write, search, directory ops."),
    dict(server_id="npm:@modelcontextprotocol/server-github", name="GitHub", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-github"], registry="npm",
         url="https://github.com/github/github-mcp-server", auth="token", deep=0,
         version="0.8.3", desc="GitHub API: issues, PRs, repos, search."),
    dict(server_id="npm:@modelcontextprotocol/server-memory", name="Memory (knowledge graph)", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-memory"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=1,
         version="0.6.2", desc="Persistent knowledge graph memory (entities, relations)."),
    dict(server_id="npm:@modelcontextprotocol/server-fetch", name="Fetch", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-fetch"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=1,
         version="0.6.2", desc="Fetch web pages and convert to markdown."),
    dict(server_id="npm:@modelcontextprotocol/server-puppeteer", name="Puppeteer (browser)", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-puppeteer"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=0,
         version="0.6.2", desc="Browser automation via headless Chrome."),
    dict(server_id="npm:@modelcontextprotocol/server-everything", name="Everything", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-everything"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=1,
         version="0.6.2", desc="Reference server exercising every MCP feature (echo, tools, prompts)."),
    dict(server_id="npm:@modelcontextprotocol/server-sequential-thinking", name="Sequential Thinking", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-sequential-thinking"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=1,
         version="0.6.2", desc="Structured reasoning tool."),
    dict(server_id="npm:@modelcontextprotocol/server-time", name="Time", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-time"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=1,
         version="0.6.2", desc="Time and timezone utilities."),
    dict(server_id="npm:@modelcontextprotocol/server-brave-search", name="Brave Search", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-brave-search"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="api_key", deep=0,
         version="0.6.2", desc="Web search via Brave Search API."),
    dict(server_id="npm:@modelcontextprotocol/server-slack", name="Slack", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-slack"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="oauth", deep=0,
         version="0.6.2", desc="Slack workspace: messages, channels."),
    dict(server_id="npm:@modelcontextprotocol/server-postgres", name="Postgres", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-postgres"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=0,
         version="0.6.2", desc="Read-only Postgres schema + query tools."),
    dict(server_id="npm:@modelcontextprotocol/server-sqlite", name="SQLite", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-sqlite"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=0,
         version="0.6.2", desc="SQLite database exploration + queries."),
    dict(server_id="npm:@modelcontextprotocol/server-git", name="Git", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-git"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=0,
         version="0.6.2", desc="Git repository operations."),
    dict(server_id="npm:@modelcontextprotocol/server-google-maps", name="Google Maps", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-google-maps"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="api_key", deep=0,
         version="0.6.2", desc="Maps, places, directions, elevation."),
    dict(server_id="npm:@modelcontextprotocol/server-websearch", name="WebSearch (MCP org)", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-websearch"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="api_key", deep=0,
         version="0.6.2", desc="Web search (requires API key)."),
    dict(server_id="npm:@modelcontextprotocol/server-sentry", name="Sentry", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-sentry"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="token", deep=0,
         version="0.6.2", desc="Sentry issues and releases."),
    dict(server_id="npm:@modelcontextprotocol/server-google-drive", name="Google Drive", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-google-drive"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="oauth", deep=0,
         version="0.6.2", desc="Google Drive files and search."),
    dict(server_id="npm:@modelcontextprotocol/server-linear", name="Linear", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-linear"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="api_key", deep=0,
         version="0.6.2", desc="Linear issue tracking."),
    dict(server_id="npm:@modelcontextprotocol/server-firecrawl", name="Firecrawl", transport="stdio",
         command=NPX, args=["-y", "firecrawl-mcp"], registry="npm",
         url="https://github.com/mendableai/firecrawl-mcp-server", auth="api_key", deep=0,
         version="1.16.0", desc="Web scraping and crawling (Firecrawl API)."),
    # --- community / notable servers ----------------------------------------
    dict(server_id="npm:@upstash/redis-mcp", name="Upstash Redis", transport="stdio",
         command=NPX, args=["-y", "@upstash/redis-mcp"], registry="npm",
         url="https://github.com/upstash/redis-mcp", auth="api_key", deep=0,
         version="0.4.0", desc="Redis operations via Upstash."),
    dict(server_id="npm:@modelcontextprotocol/server-aws-kb-retrieval", name="AWS KB Retrieval", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-aws-kb-retrieval"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="iam", deep=0,
         version="0.6.2", desc="AWS Knowledge Bases retrieval."),
    dict(server_id="npm:@executeautomation/playwright-mcp-server", name="Playwright Automation", transport="stdio",
         command=NPX, args=["-y", "@executeautomation/playwright-mcp-server"], registry="npm",
         url="https://github.com/executeautomation/mcp-playwright", auth="none", deep=0,
         version="2.0.1", desc="Playwright browser automation."),
    dict(server_id="npm:@modelcontextprotocol/server-servers-registry", name="Servers Registry", transport="stdio",
         command=NPX, args=["-y", "@modelcontextprotocol/server-servers-registry"], registry="npm",
         url="https://github.com/modelcontextprotocol/servers", auth="none", deep=0,
         version="0.6.2", desc="DNS-style registry of MCP servers."),
    dict(server_id="npm:mcp-server-mysql", name="MySQL", transport="stdio",
         command=NPX, args=["-y", "mcp-server-mysql"], registry="npm",
         url="https://github.com/benborla29/mcp-server-mysql", auth="none", deep=0,
         version="1.1.0", desc="MySQL read/write operations."),
    dict(server_id="npm:mcp-server-sqlite", name="SQLite (mcp-server-sqlite)", transport="stdio",
         command=NPX, args=["-y", "mcp-server-sqlite"], registry="npm",
         url="https://github.com/mcp-sqlite/server-sqlite", auth="none", deep=0,
         version="0.6.4", desc="SQLite interactive queries."),
    dict(server_id="npm:@aws-sdk/mcp-server", name="AWS SDK Resources", transport="stdio",
         command=NPX, args=["-y", "@aws-sdk/mcp-server"], registry="npm",
         url="https://github.com/awslabs/mcp", auth="iam", deep=0,
         version="1.5.0", desc="AWS service resources and tools."),
    dict(server_id="npm:obsidian-mcp", name="Obsidian", transport="stdio",
         command=NPX, args=["-y", "obsidian-mcp"], registry="npm",
         url="https://github.com/StevenStavrakis/obsidian-mcp", auth="none", deep=0,
         version="2.2.1", desc="Read/write vault notes."),
    dict(server_id="npm:github-mcp-server", name="GitHub MCP Server (community)", transport="stdio",
         command=NPX, args=["-y", "github-mcp-server"], registry="npm",
         url="https://github.com/github/github-mcp-server", auth="token", deep=0,
         version="0.8.3", desc="GitHub API server."),
    dict(server_id="npm:blender-mcp", name="Blender", transport="stdio",
         command=NPX, args=["-y", "blender-mcp"], registry="npm",
         url="https://github.com/ahujasid/blender-mcp", auth="none", deep=0,
         version="1.1.0", desc="Blender 3D scene control."),
    dict(server_id="npm:mcp-pandoc", name="Pandoc", transport="stdio",
         command=NPX, args=["-y", "mcp-pandoc"], registry="npm",
         url="https://github.com/vivekVells/mcp-pandoc", auth="none", deep=1,
         version="1.6.0", desc="Document format conversion via pandoc."),
    dict(server_id="npm:@elsoul/solc-mcp-server", name="Solc (Solidity)", transport="stdio",
         command=NPX, args=["-y", "@elsoul/solc-mcp-server"], registry="npm",
         url="https://github.com/elsoul/solc-mcp-server", auth="none", deep=0,
         version="1.0.1", desc="Solidity compiler interactions."),
    dict(server_id="npm:@zereight/mcp-server-azure-devops", name="Azure DevOps", transport="stdio",
         command=NPX, args=["-y", "@zereight/mcp-server-azure-devops"], registry="npm",
         url="https://github.com/todo-labs/mcp-server-azure-devops", auth="token", deep=0,
         version="0.4.0", desc="Azure DevOps work items and pipelines."),
    dict(server_id="npm:qbit-mcp", name="qBittorrent", transport="stdio",
         command=NPX, args=["-y", "qbit-mcp"], registry="npm",
         url="https://github.com/reefwoo/qbit-mcp", auth="none", deep=0,
         version="0.4.0", desc="qBittorrent torrent management."),
    dict(server_id="npm:mongodb-mcp-server", name="MongoDB", transport="stdio",
         command=NPX, args=["-y", "mongodb-mcp-server"], registry="npm",
         url="https://github.com/kiliczsh/mcp-mongo-server", auth="none", deep=0,
         version="0.7.0", desc="MongoDB collections and queries."),
    dict(server_id="npm:@hackmd/mcp-server", name="HackMD", transport="stdio",
         command=NPX, args=["-y", "@hackmd/mcp-server"], registry="npm",
         url="https://github.com/hackmdio/mcp-server", auth="token", deep=0,
         version="1.0.0", desc="HackMD notes and teams."),
    dict(server_id="npm:webkit-mcp", name="WebKit / Safari", transport="stdio",
         command=NPX, args=["-y", "webkit-mcp"], registry="npm",
         url="https://github.com/webfansplz/webkit-mcp", auth="none", deep=0,
         version="1.0.3", desc="WebKit browser driving."),
    dict(server_id="npm:aws-s3-mcp", name="AWS S3", transport="stdio",
         command=NPX, args=["-y", "aws-s3-mcp"], registry="npm",
         url="https://github.com/aws-samples/mcp-s3-server", auth="iam", deep=0,
         version="0.1.0", desc="S3 bucket operations."),
    dict(server_id="npm:@pab1it0/adb-mcp-server", name="ADB (Android)", transport="stdio",
         command=NPX, args=["-y", "@pab1it0/adb-mcp-server"], registry="npm",
         url="https://github.com/pab1it0/adb-mcp-server", auth="none", deep=0,
         version="0.1.0", desc="Android device automation via adb."),
    dict(server_id="npm:supabase-mcp-server", name="Supabase", transport="stdio",
         command=NPX, args=["-y", "supabase-mcp-server"], registry="npm",
         url="https://github.com/supabase-community/supabase-mcp", auth="token", deep=0,
         version="0.6.0", desc="Supabase project management."),
    dict(server_id="npm:@anthropic/mcp-server-nightly", name="Anthropic MCP", transport="stdio",
         command=NPX, args=["-y", "@anthropic/mcp-server-nightly"], registry="npm",
         url="https://github.com/anthropics/anthropic-quickstarts", auth="api_key", deep=0,
         version="0.1.0", desc="Anthropic API server (alpha)."),
    dict(server_id="npm:huggingface-mcp-server", name="Hugging Face", transport="stdio",
         command=NPX, args=["-y", "huggingface-mcp-server"], registry="npm",
         url="https://github.com/huggingface/mcp-huggingface", auth="token", deep=0,
         version="0.1.0", desc="Hugging Face inference and datasets."),
    dict(server_id="npm:@chenzhe0712/mcp-server-bilibili", name="Bilibili", transport="stdio",
         command=NPX, args=["-y", "@chenzhe0712/mcp-server-bilibili"], registry="npm",
         url="https://github.com/chenzhe0712/mcp-server-bilibili", auth="none", deep=0,
         version="0.1.0", desc="Bilibili video search and info."),
    dict(server_id="npm:@multiwoven/mcp-server", name="Multiwoven", transport="stdio",
         command=NPX, args=["-y", "@multiwoven/mcp-server"], registry="npm",
         url="https://github.com/Multiwoven/mcp-server", auth="none", deep=0,
         version="0.1.0", desc="Marketing/analytics data connectors."),
    dict(server_id="npm:@tavily-ai/tavily-mcp", name="Tavily Search", transport="stdio",
         command=NPX, args=["-y", "@tavily-ai/tavily-mcp"], registry="npm",
         url="https://github.com/tavily-ai/tavily-mcp", auth="api_key", deep=0,
         version="0.1.0", desc="AI-optimized web search."),
    dict(server_id="npm:@vscode/mcp-server", name="VS Code", transport="stdio",
         command=NPX, args=["-y", "@vscode/mcp-server"], registry="npm",
         url="https://github.com/microsoft/vscode-mcp-server", auth="none", deep=0,
         version="0.1.0", desc="VS Code extension and workspace control."),
    dict(server_id="npm:octo-mcp", name="Octo (GitHub CLI)", transport="stdio",
         command=NPX, args=["-y", "octo-mcp"], registry="npm",
         url="https://github.com/octomapper/octo-mcp", auth="token", deep=0,
         version="0.1.0", desc="GitHub workflows via gh CLI."),
    dict(server_id="npm:@docker/mcp-server", name="Docker", transport="stdio",
         command=DOCKER, args=["run", "-i", "--rm", "mcp/docker"], registry="npm",
         url="https://github.com/docker/mcp-servers", auth="none", deep=0,
         version="1.0.0", desc="Docker containers, images, compose."),
    dict(server_id="npm:@kubernetes-mcp-server/core", name="Kubernetes", transport="stdio",
         command=NPX, args=["-y", "@kubernetes-mcp-server/core"], registry="npm",
         url="https://github.com/kubernetes-mcp-server/core", auth="kubeconfig", deep=0,
         version="0.1.0", desc="Kubernetes cluster operations."),
    dict(server_id="npm:mcp-proxmox", name="Proxmox", transport="stdio",
         command=NPX, args=["-y", "mcp-proxmox"], registry="npm",
         url="https://github.com/shdq/mcp-proxmox", auth="token", deep=0,
         version="0.3.0", desc="Proxmox VE virtualization."),
    dict(server_id="npm:@recteurl/vmcp-server", name="vMCP", transport="stdio",
         command=NPX, args=["-y", "@recteurl/vmcp-server"], registry="npm",
         url="https://github.com/recteurl/vmcp-server", auth="none", deep=0,
         version="0.1.0", desc="Virtual machine management."),
    dict(server_id="npm:exa-mcp-server", name="Exa Search", transport="stdio",
         command=NPX, args=["-y", "exa-mcp-server"], registry="npm",
         url="https://github.com/exa-labs/exa-mcp-server", auth="api_key", deep=0,
         version="3.0.0", desc="Exa neural search."),
    dict(server_id="npm:matplotlib-mcp-server", name="Matplotlib MCP", transport="stdio",
         command=NPX, args=["-y", "matplotlib-mcp-server"], registry="npm",
         url="https://github.com/Sunwood-ai-labs/matplotlib-mcp-server", auth="none", deep=1,
         version="0.2.0", desc="Python data visualization."),
    dict(server_id="npm:desktop-automation-mcp", name="Desktop Automation", transport="stdio",
         command=NPX, args=["-y", "desktop-automation-mcp"], registry="npm",
         url="https://github.com/nicepkg/desktop-automation-mcp", auth="none", deep=0,
         version="0.1.0", desc="Cross-platform desktop control."),
    dict(server_id="npm:@hexagonai/mcp_server", name="Hexagon AI", transport="stdio",
         command=NPX, args=["-y", "@hexagonai/mcp_server"], registry="npm",
         url="https://github.com/hexagon-ai/mcp-server", auth="none", deep=0,
         version="0.1.0", desc="Multi-purpose productivity tools."),
    dict(server_id="npm:kalosm-mcp-server", name="Kalosm", transport="stdio",
         command=NPX, args=["-y", "kalosm-mcp-server"], registry="npm",
         url="https://github.com/floneum/floneum", auth="none", deep=0,
         version="0.4.0", desc="Rust embedding/RAG tools."),
    dict(server_id="npm:gdrive-mcp-server", name="Google Drive (community)", transport="stdio",
         command=NPX, args=["-y", "gdrive-mcp-server"], registry="npm",
         url="https://github.com/aeharding/mcp-server-gdrive", auth="oauth", deep=0,
         version="0.1.0", desc="Google Drive community server."),
    dict(server_id="npm:@automatalabs/mcp-server-automata", name="Automata", transport="stdio",
         command=NPX, args=["-y", "@automatalabs/mcp-server-automata"], registry="npm",
         url="https://github.com/AutomataLabs/MCP-Server", auth="none", deep=0,
         version="0.3.0", desc="Browser automation with Automata."),
    dict(server_id="npm:mcp-server-mcpviewer", name="MCP Viewer", transport="stdio",
         command=NPX, args=["-y", "mcp-server-mcpviewer"], registry="npm",
         url="https://github.com/terilku/mcp-viewer", auth="none", deep=0,
         version="0.1.0", desc="MCP server diagnostics."),
    dict(server_id="npm:@xmcp/mcp-server-stripe", name="Stripe", transport="stdio",
         command=NPX, args=["-y", "@xmcp/mcp-server-stripe"], registry="npm",
         url="https://github.com/xmcp/mcp-stripe", auth="api_key", deep=0,
         version="0.9.0", desc="Stripe payments data."),
    dict(server_id="npm:server-vmagenticsearch", name="VMagentic Search", transport="stdio",
         command=NPX, args=["-y", "server-vmagenticsearch"], registry="npm",
         url="https://github.com/VMagentic/search-mcp-server", auth="api_key", deep=0,
         version="0.1.0", desc="Search provider MCP."),
    dict(server_id="npm:quickchart-mcp-server", name="QuickChart", transport="stdio",
         command=NPX, args=["-y", "quickchart-mcp-server"], registry="npm",
         url="https://github.com/tywenk/quickchart-mcp-server", auth="none", deep=0,
         version="0.1.0", desc="Chart generation."),
    dict(server_id="npm:youtube-mcp-server", name="YouTube", transport="stdio",
         command=NPX, args=["-y", "youtube-mcp-server"], registry="npm",
         url="https://github.com/jupiverse/doppio-mcp", auth="none", deep=0,
         version="0.1.0", desc="YouTube transcripts and metadata."),
    dict(server_id="npm:mcp-server-typescript-starter", name="TypeScript Starter", transport="stdio",
         command=NPX, args=["-y", "mcp-server-typescript-starter"], registry="npm",
         url="https://github.com/modelcontextprotocol/typescript-sdk", auth="none", deep=0,
         version="0.6.2", desc="Empty TS server skeleton."),
]

# Deep-test default selection: local/mock + official org servers that need no
# auth and cost nothing to invoke.  This lands in the 10-20 band.
DEEP_TEST_IDS = [
    "mock:mock-mcp",
    "npm:@modelcontextprotocol/server-everything",
    "npm:@modelcontextprotocol/server-sequential-thinking",
    "npm:@modelcontextprotocol/server-time",
    "npm:@modelcontextprotocol/server-filesystem",
    "npm:@modelcontextprotocol/server-memory",
    "npm:@modelcontextprotocol/server-fetch",
    "npm:mcp-pandoc",
]


def seed_registry(force: bool = False, deep_ids: Optional[list[str]] = None) -> dict:
    """Idempotent seed.  force=True re-upserts values but never deletes rows."""
    db.init_db()
    db.ensure_capabilities([
        "web.search", "web.fetch", "web.scrape", "browser.navigate",
        "browser.automate", "repository.issue.create", "repository.issue.read",
        "repository.pull.create", "repository.read", "database.query",
        "filesystem.read", "filesystem.write", "memory.store", "memory.recall",
        "search.vector", "messaging.send", "email.send", "calendar.read",
        "cloud.provision", "code.execute", "math.compute", "time.now",
        "image.generate", "pdf.read",
    ])
    deep_ids = deep_ids or DEEP_TEST_IDS
    added = updated = 0
    for entry in SEED:
        sid = entry["server_id"]
        deep = 1 if sid in deep_ids else 0
        existing = db.get_server(sid)
        db.upsert_server(
            server_id=sid,
            name=entry["name"],
            transport=entry["transport"],
            description=entry["desc"],
            source_registry=entry["registry"],
            source_url=entry["url"],
            command=entry["command"],
            args=entry["args"],
            url=entry.get("url"),
            auth_scheme=entry["auth"],
            deep_test=deep,
            status="ACTIVE" if existing and existing.get("status") == "ACTIVE" else "REGISTERED",
            version=entry.get("version"),
            install_command=f"{entry['command']} {' '.join(entry['args'])}" if entry.get("args") else "",
        )
        # auth scheme rows
        db.get_conn().execute(
            """INSERT OR IGNORE INTO auth_schemes
               (auth_scheme_id, server_id, scheme_type, required_headers, notes)
               VALUES (?,?,?,?,?)""",
            (f"{sid}:auth", sid, entry["auth"], "{}",
             f"required credential scheme for {entry['name']}"),
        )
        if existing is None:
            added += 1
        else:
            updated += 1
    db.get_conn().commit()
    return {"added": added, "updated": updated, "total": len(SEED),
            "deep_test": len(deep_ids)}


def discovery_targets(limit: Optional[int] = None, only_deep: bool = False) -> list[dict]:
    """Servers the runner should attempt to probe right now."""
    servers = db.list_servers()
    targets = [s for s in servers if s["status"] != "RETIRED"]
    if only_deep:
        targets = [s for s in targets if s["deep_test"]]
    # prefer deterministic local/mock first, then deep-test targets
    def key(s: dict) -> tuple:
        order = {"local": 0, "npm": 1, "github": 1, "manual": 2}
        return (order.get(s["source_registry"], 3), s["server_id"])
    targets.sort(key=key)
    if limit:
        targets = targets[:limit]
    return targets