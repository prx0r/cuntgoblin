"""Safe MCP test harness.

Probes a server through the real Model Context Protocol SDK:

  connect -> initialize   (connection latency, init success)
  tools/list              (success, tool count, schema fingerprints)
  invocation of READ_ONLY tools with curated safe args (latency, success)

Safety NEVER relaxes: invocation only for READ_ONLY-class tools with a curated
safe-args entry; everything else is recorded as NOT_APPLICABLE / SAFETY_SKIP.

Each probe run writes data/runs/<run-id>/run.json + results.jsonl + artifacts/
and records immutable measurements + Oracle envelopes in the DB.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Optional

from . import db, oracle
from .capabilities import map_all_tools

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamable_http_client
    MCP_AVAILABLE = True
except Exception:  # pragma: no cover - environment guard
    ClientSession = None  # type: ignore
    StdioServerParameters = None  # type: ignore
    stdio_client = None  # type: ignore
    streamable_http_client = None  # type: ignore
    MCP_AVAILABLE = False  # type: ignore


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------

_MUTATING_KW = [
    "write_file", "create", "edit", "delete", "remove", "update", "insert",
    "upsert", "send", "post", "push", "commit", "merge", "deploy", "execute",
    "run", "transform", "upload", "save", "mkdir", "rm", "move", "copy",
    "mutate", "destroy", "clear", "append", "modify", "rename", "chmod",
]
_READ_ONLY_KW = [
    "read", "list", "get_", "get ", "search", "query", "fetch", "describe",
    "show", "ls", "status", "info", "find", "lookup", "view", "stat", "cat",
    "head", "tail", "echo", "add", "sum", "diff", "peek", "inspect", "count",
    "calculate", "print", "exists", "ping", "health",
]


def classify_tool(name: str, description: str) -> str:
    """READ_ONLY | REVERSIBLE | MUTATING | UNKNOWN (spec §Safe testing)."""
    text = f"{name} {description}".lower()
    if any(k in text for k in _MUTATING_KW):
        return db.SAFETY_MUTATING
    if any(k in text for k in _READ_ONLY_KW):
        return db.SAFETY_READ_ONLY
    return db.SAFETY_UNKNOWN


# Curated safe args: only (server_id, tool_name) pairs proven safe to invoke
# repeatedly from a public probe.  MVP: mock/local servers only.
SAFE_ARGS: dict[tuple[str, str], dict] = {
    ("mock:echo", "echo"): {"text": "mcptruth-probe"},
    ("mock:add", "add"): {"a": 2, "b": 3},
    ("mock:read_doc", "read_doc"): {"path": "data/test-doc.txt"},
    ("mock:list_tree", "list_tree"): {},
    ("mock:web_search", "web_search"): {"query": "model context protocol"},
}


# ---------------------------------------------------------------------------
# Probe result
# ---------------------------------------------------------------------------

@dataclass
class ProbeResult:
    status: str = "SUCCESS"                       # SUCCESS|FAILED|TIMEOUT|SKIPPED
    error_class: Optional[str] = None             # CONNECTION_ERROR|INIT_FAILED|TOOLS_LIST_FAILED|INVOCATION_FAILED|RATE_LIMITED|TIMEOUT|SAFETY_SKIP
    error_detail: str = ""
    measurements: list[dict] = field(default_factory=list)   # raw measurements
    envelopes: list[dict] = field(default_factory=list)      # oracle envelopes
    artifacts: list[dict] = field(default_factory=list)      # {name, payload}
    stdout_log: str = ""


# ---------------------------------------------------------------------------
# Error classification
# ---------------------------------------------------------------------------

_RATE_LIMIT_PATTERNS = ["rate limit", "rate-limit", "too many requests", "429", "quota exceeded", "throttl"]


def classify_error(exc: BaseException) -> tuple[str, str]:
    text = f"{type(exc).__name__}: {exc}".lower()
    if any(p in text for p in _RATE_LIMIT_PATTERNS):
        return "RATE_LIMITED", str(exc)[:1000]
    if isinstance(exc, asyncio.TimeoutError):
        return "TIMEOUT", "operation timed out"
    if isinstance(exc, (FileNotFoundError, PermissionError, OSError)):
        return "CONNECTION_ERROR", str(exc)[:1000]
    if "connection" in text or "refused" in text or "spawn" in text or "no such file" in text:
        return "CONNECTION_ERROR", str(exc)[:1000]
    return "INIT_FAILED", str(exc)[:1000]


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

class Harness:
    """Runs a full probe cycle for one server."""

    def __init__(self, run_dir: str, timeout_ms: int = 20000, region: str = "local",
                 method_version: str = "mcptruth-harness-v1"):
        self.run_dir = run_dir
        self.timeout_s = timeout_ms / 1000.0
        self.region = region
        self.method_version = method_version
        self.result = ProbeResult()

    # -- transport ----------------------------------------------------------

    @asynccontextmanager
    async def _open_session(self, server: dict):
        """Yield an initialized ClientSession.  Measures elapsed time through
        initialize() so callers can derive connection latency."""
        transport = server["transport"]
        if transport in ("stdio", "mock", "local"):
            if ClientSession is None or stdio_client is None or StdioServerParameters is None:
                raise RuntimeError("mcp SDK unavailable")
            cmd = server.get("command") or sys.executable
            args = server.get("args") or []
            env = dict(os.environ)
            env.update(server.get("env") or {})
            params = StdioServerParameters(
                command=cmd, args=args, env=env,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            )
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await asyncio.wait_for(session.initialize(), timeout=self.timeout_s)
                    yield session
        elif transport in ("http", "sse"):
            if ClientSession is None or streamable_http_client is None:
                raise RuntimeError("mcp SDK unavailable")
            url = server.get("url")
            if not url:
                raise RuntimeError("http transport requires url")
            import httpx
            headers = {}
            if server.get("auth_scheme") in ("bearer", "api_key"):
                # Token injected at runtime from env; never stored in DB.
                headers["Authorization"] = os.environ.get("MCPTRUTH_TOKEN", "")
            async with streamable_http_client(
                url, http_client=httpx.AsyncClient(headers=headers)
            ) as (read, write, _session_id):
                async with ClientSession(read, write) as session:
                    await asyncio.wait_for(session.initialize(), timeout=self.timeout_s)
                    yield session
        else:
            raise RuntimeError(f"unsupported transport: {transport}")

    # -- one full probe cycle ----------------------------------------------

    def run(self, server: dict) -> ProbeResult:
        try:
            asyncio.run(self._run_async(server))
        except Exception as exc:  # top-level safety net
            ec, ed = classify_error(exc)
            self.result.status = "FAILED"
            self.result.error_class = self.result.error_class or ec
            self.result.error_detail = ed[:1000]
            self.result.measurements.append({
                "metric": "probe.status", "value_numeric": 0, "value_text": "FAILED",
                "unit": "", "state": db.STATE_UNAVAILABLE,
                "observed_at": oracle.now_iso(),
            })
        return self.result

    async def _run_async(self, server: dict) -> None:
        server_id = server["server_id"]
        started = time.perf_counter()
        try:
            async with self._open_session(server) as session:
                init_ms = (time.perf_counter() - started) * 1000.0
                self._measure("init.success", 1, None, "", db.STATE_KNOWN)
                self._measure("connection.ms", round(init_ms, 2), None, "ms", db.STATE_KNOWN)

                # tools/list
                tl_start = time.perf_counter()
                tools = await asyncio.wait_for(session.list_tools(), timeout=self.timeout_s)
                tl_ms = (time.perf_counter() - tl_start) * 1000.0
                self._measure("tools_list.success", 1, None, "", db.STATE_KNOWN)
                self._measure("tools_list.ms", round(tl_ms, 2), None, "ms", db.STATE_KNOWN)
                self._measure("tool.count", float(len(tools.tools)), None, "tools", db.STATE_KNOWN)

                # schema fingerprint + persistence
                total_tokens = 0
                for t in tools.tools:
                    ischema = t.inputSchema or {}
                    safety = classify_tool(t.name, t.description or "")
                    self.artifacts.append({
                        "name": f"tool-{t.name}.json",
                        "payload": {"name": t.name, "description": t.description or "",
                                    "inputSchema": ischema, "safety_class": safety},
                    })
                    canon = db.canonical_tool_schema(t.name, t.description or "", ischema)
                    total_tokens += db.schema_token_count(canon)
                    tool = db.upsert_tool(
                        server_id, t.name, t.description or "", ischema, safety,
                        observed_at=oracle.now_iso(),
                    )
                    map_all_tools(server_id, t.name, t.description or "", tool["tool_id"])
                self._measure("schema.token_count", float(total_tokens), None, "tokens", db.STATE_KNOWN)

                # invocation: READ_ONLY only, curated safe args only
                inv_results = await self._probe_invocations(session, server, tools.tools)

                for inv in inv_results:
                    if inv["measurement"] is not None:
                        self.measurements.append(inv["measurement"])
                    self.result.envelopes.extend(inv["envelopes"])
                    for a in inv.get("artifacts", []):
                        self.artifacts.append(a)

                self.result.status = "SUCCESS"
        except Exception as exc:
            ec, ed = classify_error(exc)
            self.result.status = "FAILED"
            self.result.error_class = ec
            self.result.error_detail = ed[:1000]
            # record the failing stage as unavailable so ranked state drops it
            self._measure("init.success", 0, None, "", db.STATE_UNAVAILABLE)

    async def _probe_invocations(self, session, server: dict, tools) -> list[dict]:
        """Invoke only READ_ONLY tools with curated safe args, one probe each,
        up to MAX_INVOCATIONS overall."""
        MAX_INVOCATIONS = 5
        server_id = server["server_id"]
        results: list[dict] = []
        attempted = 0
        for t in tools:
            tool_key = db._tool_id(server_id, t.name)
            if attempted >= MAX_INVOCATIONS:
                break
            safety = classify_tool(t.name, t.description or "")
            if safety != db.SAFETY_READ_ONLY:
                env = oracle.build_envelope(
                    "tool", tool_key, "tool.invocation",
                    db.STATE_NOT_APPLICABLE,
                    source_id=f"run-{server_id}", method_id=self.method_version,
                    method_version=self.method_version,
                    value_text=f"safety_class={safety} -> not invoked",
                    valid_for=3600,
                )
                results.append({"measurement": None, "envelopes": [env], "artifacts": []})
                continue
            args = SAFE_ARGS.get((server_id, t.name))
            if args is None:
                env = oracle.build_envelope(
                    "tool", tool_key, "tool.invocation",
                    db.STATE_NOT_APPLICABLE,
                    source_id=f"run-{server_id}", method_id=self.method_version,
                    method_version=self.method_version,
                    value_text="no curated safe args -> invocation skipped",
                    valid_for=3600,
                )
                results.append({"measurement": None, "envelopes": [env], "artifacts": []})
                continue
            attempted += 1
            inv_start = time.perf_counter()
            success = 0
            err = ""
            try:
                resp = await asyncio.wait_for(
                    session.call_tool(t.name, args), timeout=self.timeout_s
                )
                inv_ms = (time.perf_counter() - inv_start) * 1000.0
                success = 0 if getattr(resp, "isError", False) else 1
                self.artifacts.append({
                    "name": f"invoke-{t.name}.json",
                    "payload": {
                        "tool": t.name, "args": args, "isError": getattr(resp, "isError", None),
                        "content": [
                            {"type": getattr(c, "type", None), "text": getattr(c, "text", None)}
                            for c in (resp.content or [])
                        ],
                    },
                })
            except Exception as exc:
                inv_ms = (time.perf_counter() - inv_start) * 1000.0
                ec, ed = classify_error(exc)
                # classify_error defaults unknown exceptions to INIT_FAILED;
                # at the invocation stage that means the TOOL call failed.
                if ec == "INIT_FAILED":
                    ec = "INVOCATION_FAILED"
                err = f"{ec}: {ed}"
                if ec == "RATE_LIMITED":
                    self.result.error_class = self.result.error_class or "RATE_LIMITED"
            state = db.STATE_KNOWN if success else (db.STATE_UNAVAILABLE if err else db.STATE_KNOWN)
            self._measure("invocation.ms", round(inv_ms, 2), None, "ms", db.STATE_KNOWN)
            results.append({
                "measurement": {
                    "metric": "invocation.success", "value_numeric": float(success),
                    "value_text": err or ("ok" if success else "failed"),
                    "unit": "", "state": state, "observed_at": oracle.now_iso(),
                },
                "envelopes": [
                    oracle.build_envelope(
                        "tool", tool_key, "tool.invocation",
                        state, source_id=f"run-{server_id}", method_id=self.method_version,
                        method_version=self.method_version,
                        value_number=float(success), value_text=err or None,
                        valid_for=900,
                    )
                ],
                "artifacts": [],
            })
        return results

    # -- helpers -------------------------------------------------------------

    def _measure(self, metric: str, value_numeric: Optional[float],
                 value_text: Optional[str], unit: str, state: str) -> None:
        self.measurements.append({
            "metric": metric, "value_numeric": value_numeric,
            "value_text": value_text, "unit": unit, "state": state,
            "observed_at": oracle.now_iso(),
        })

    @property
    def artifacts(self) -> list[dict]:
        return self.result.artifacts

    @property
    def measurements(self) -> list[dict]:
        return self.result.measurements


# ---------------------------------------------------------------------------
# Orchestration: run probe cycle for a server, persist everything
# ---------------------------------------------------------------------------

def run_probe_cycle(server: dict, run_dir: Optional[str] = None,
                    timeout_ms: int = 20000, region: str = "local") -> dict:
    """Run the full probe cycle for one server and persist observations.

    Returns a summary dict.  Raw measurements are immutable; envelope
    observations are content-addressed in the observations table.
    """
    server_id = server["server_id"]
    now = oracle.now_iso()
    run_dir = run_dir or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "runs",
        f"{server_id.replace('@', '_').replace(':', '_')[:48]}_{now.replace(':', '').replace('+', 'Z')}",
    )
    os.makedirs(os.path.join(run_dir, "artifacts"), exist_ok=True)

    harness = Harness(run_dir=run_dir, timeout_ms=timeout_ms, region=region)
    # Persist run row before probing so partial failures are visible.
    run_id = db.start_probe_run(server_id, "full", harness.method_version, run_dir, region=region)

    result = harness.run(server)
    db.finish_probe_run(run_id, result.status, result.error_class, result.error_detail)

    # Persist measurements (append-only, immutable)
    for m in result.measurements:
        db.record_measurement(
            run_id, m["metric"], m["value_numeric"], m["value_text"], m["unit"],
            m["state"], observed_at=m.get("observed_at"),
        )

    # Persist oracle envelopes
    env_count = 0
    saved_envs = []
    for env in result.envelopes:
        env["source"] = {"type": "probe", "id": f"run-{run_id}"}
        pers = oracle.persist_envelope(env)
        saved_envs.append(pers)
        env_count += 1

    # Write run artifacts (content-addressed evidence)
    run_json = {
        "run_id": run_id,
        "server_id": server_id,
        "server_name": server["name"],
        "probe_type": "full",
        "method_version": harness.method_version,
        "started_at": now,
        "completed_at": oracle.now_iso(),
        "status": result.status,
        "error_class": result.error_class,
        "error_detail": result.error_detail,
        "region": region,
        "measurement_count": len(result.measurements),
        "observation_count": env_count,
        "artifact_count": len(result.artifacts),
    }
    with open(os.path.join(run_dir, "run.json"), "w") as f:
        json.dump(run_json, f, indent=2, sort_keys=True)
    with open(os.path.join(run_dir, "stdout.log"), "w") as f:
        f.write(result.stdout_log or f"harness {harness.method_version} completed\n")
    with open(os.path.join(run_dir, "results.jsonl"), "w") as f:
        for m in result.measurements:
            f.write(json.dumps(m, sort_keys=True) + "\n")
        for env in saved_envs:
            f.write(json.dumps(env, sort_keys=True) + "\n")
    for art in result.artifacts:
        art_path = os.path.join(run_dir, "artifacts", art["name"])
        with open(art_path, "w") as f:
            json.dump(art["payload"], f, indent=2, sort_keys=True)
        art["artifact_sha256"] = oracle.artifact_sha256(art["payload"])

    evidence_index = [
        {"artifact": a["name"], "sha256": a["artifact_sha256"], "selector": f"$.{a['name']}"}
        for a in result.artifacts
    ]
    with open(os.path.join(run_dir, "evidence.json"), "w") as f:
        json.dump(evidence_index, f, indent=2, sort_keys=True)

    # Mark server ACTIVE on success
    if result.status == "SUCCESS":
        db.upsert_server(
            server_id, server["name"], server["transport"],
            status="ACTIVE", deep_test=1,
            command=server.get("command"), args=server.get("args"),
            env=server.get("env"), url=server.get("url"),
            auth_scheme=server.get("auth_scheme", "none"),
            auth_notes=server.get("auth_notes", ""),
            source_registry=server.get("source_registry", "manual"),
            source_url=server.get("source_url", ""),
            description=server.get("description", ""),
        )

    return {
        "run_id": run_id,
        "server_id": server_id,
        "status": result.status,
        "error_class": result.error_class,
        "error_detail": result.error_detail,
        "measurements": len(result.measurements),
        "observations": env_count,
        "run_dir": run_dir,
    }