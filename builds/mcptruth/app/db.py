"""SQLite persistence for MCPTruth.

Layout follows specs/mcptruth/architecture.md:

- servers          (MCPServer identity; SERVER != TOOL != CAPABILITY)
- server_versions  (MCPServerVersion)
- tools            (Tool identity + schema fingerprint; a tool belongs to one server)
- capabilities     (normalized Capability, e.g. web.search)
- tool_capabilities (M:N; a tool may implement multiple capabilities)
- auth_schemes     (AuthScheme)
- probe_runs       (InvocationProbe; one per probe attempt)
- probe_measurements (raw immutable measurements; NEVER overwritten)
- observations     (Oracle-compatible universal envelopes, content-addressed)
- server_windows   (derived projection: window aggregates -> current state)
- schema_changes   (breaking API evolution feed)

Raw probe measurements are append-only. Derived projections (server_windows)
are recomputed by the reducer and may be replaced.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Optional

DB_PATH = os.environ.get(
    "MCPTRUTH_DB",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "mcptruth.db"),
)

_local = threading.local()

STATE_KNOWN = "KNOWN"
STATE_UNKNOWN = "UNKNOWN"
STATE_ABSENT = "ABSENT"
STATE_NOT_OBSERVED = "NOT_OBSERVED"
STATE_NOT_APPLICABLE = "NOT_APPLICABLE"
STATE_STALE = "STALE"
STATE_CONFLICTED = "CONFLICTED"
STATE_UNAVAILABLE = "UNAVAILABLE"

STATES = {
    STATE_KNOWN,
    STATE_UNKNOWN,
    STATE_ABSENT,
    STATE_NOT_OBSERVED,
    STATE_NOT_APPLICABLE,
    STATE_STALE,
    STATE_CONFLICTED,
    STATE_UNAVAILABLE,
}

SAFETY_READ_ONLY = "READ_ONLY"
SAFETY_REVERSIBLE = "REVERSIBLE"
SAFETY_MUTATING = "MUTATING"
SAFETY_UNKNOWN = "UNKNOWN"

SAFETY_CLASSES = {SAFETY_READ_ONLY, SAFETY_REVERSIBLE, SAFETY_MUTATING, SAFETY_UNKNOWN}

SCHEMA = """
CREATE TABLE IF NOT EXISTS servers (
  server_id       TEXT PRIMARY KEY,
  name            TEXT NOT NULL,
  description     TEXT DEFAULT '',
  source_registry TEXT NOT NULL,          -- github | npm | manual | local
  source_url      TEXT DEFAULT '',
  transport       TEXT NOT NULL,          -- stdio | http | sse | mock
  command         TEXT,                   -- stdio: executable
  args_json       TEXT DEFAULT '[]',      -- stdio: args
  env_json        TEXT DEFAULT '{}',      -- stdio: extra env
  url             TEXT,                   -- http/sse: endpoint url
  auth_scheme     TEXT DEFAULT 'none',    -- none | api_key | bearer | oauth | basic
  auth_notes      TEXT DEFAULT '',
  status          TEXT NOT NULL DEFAULT 'REGISTERED',  -- REGISTERED|ACTIVE|RETIRED
  deep_test       INTEGER NOT NULL DEFAULT 0,
  discovered_at   TEXT NOT NULL,
  retired_at      TEXT
);

CREATE TABLE IF NOT EXISTS server_versions (
  server_version_id TEXT PRIMARY KEY,
  server_id       TEXT NOT NULL REFERENCES servers(server_id),
  version         TEXT,
  install_command TEXT DEFAULT '',
  status          TEXT NOT NULL DEFAULT 'CURRENT',
  installed_at    TEXT
);

CREATE TABLE IF NOT EXISTS tools (
  tool_id           TEXT PRIMARY KEY,     -- sha256(server_id|tool_name)
  server_id         TEXT NOT NULL REFERENCES servers(server_id),
  name              TEXT NOT NULL,
  description       TEXT DEFAULT '',
  input_schema      TEXT NOT NULL DEFAULT '{}',   -- canonical JSON
  schema_sha256     TEXT NOT NULL,
  schema_token_count INTEGER NOT NULL DEFAULT 0,
  safety_class      TEXT NOT NULL DEFAULT 'UNKNOWN',
  first_seen        TEXT NOT NULL,
  last_seen         TEXT NOT NULL,
  UNIQUE(server_id, name)
);

CREATE TABLE IF NOT EXISTS capabilities (
  capability_id TEXT PRIMARY KEY,
  label         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tool_capabilities (
  tool_id        TEXT NOT NULL REFERENCES tools(tool_id),
  capability_id  TEXT NOT NULL REFERENCES capabilities(capability_id),
  confidence     REAL NOT NULL,
  mapping_method TEXT NOT NULL,           -- curated | heuristic | llm_reviewed
  PRIMARY KEY (tool_id, capability_id)
);

CREATE TABLE IF NOT EXISTS auth_schemes (
  auth_scheme_id TEXT PRIMARY KEY,
  server_id      TEXT NOT NULL REFERENCES servers(server_id),
  scheme_type    TEXT NOT NULL,           -- none | api_key | bearer | oauth | basic
  required_headers TEXT DEFAULT '{}',
  notes          TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS probe_runs (
  probe_run_id  TEXT PRIMARY KEY,
  server_id     TEXT NOT NULL,
  probe_type    TEXT NOT NULL,            -- init | tools_list | invocation | full
  started_at    TEXT NOT NULL,
  completed_at  TEXT,
  probe_region  TEXT DEFAULT 'local',
  method_version TEXT NOT NULL,
  status        TEXT NOT NULL,            -- RUNNING|SUCCESS|FAILED|TIMEOUT|SKIPPED
  run_dir       TEXT,
  artifact_id   TEXT,
  error_class   TEXT,                     -- CONNECTION_ERROR|INIT_FAILED|TOOLS_LIST_FAILED|INVOCATION_FAILED|RATE_LIMITED|TIMEOUT|SAFETY_SKIP
  error_detail  TEXT
);

CREATE TABLE IF NOT EXISTS probe_measurements (
  measurement_id TEXT PRIMARY KEY,
  probe_run_id   TEXT NOT NULL REFERENCES probe_runs(probe_run_id),
  metric         TEXT NOT NULL,
  value_numeric  REAL,
  value_text     TEXT,
  unit           TEXT,
  state          TEXT NOT NULL,
  observed_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS observations (
  observation_id TEXT PRIMARY KEY,        -- sha256(content-addressed)
  envelope_json  TEXT NOT NULL,
  subject_type   TEXT NOT NULL,
  subject_id     TEXT NOT NULL,
  predicate      TEXT NOT NULL,
  state          TEXT NOT NULL,
  observed_at    TEXT NOT NULL,
  valid_until    TEXT,
  source_id      TEXT NOT NULL,
  method_id      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS server_windows (
  server_id                  TEXT NOT NULL,
  window_start               TEXT NOT NULL,
  window_end                 TEXT NOT NULL,
  samples                    INTEGER NOT NULL DEFAULT 0,
  init_success_rate          REAL,
  tools_list_success_rate    REAL,
  connection_ms_p50          REAL,
  connection_ms_p95          REAL,
  invocation_ms_p50          REAL,
  invocation_ms_p95          REAL,
  invocation_success_rate    REAL,
  tool_count                 INTEGER,
  schema_break_count         INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (server_id, window_start)
);

CREATE TABLE IF NOT EXISTS schema_changes (
  change_id         TEXT PRIMARY KEY,
  server_id         TEXT NOT NULL,
  tool_name         TEXT NOT NULL,
  old_schema_sha256 TEXT,
  new_schema_sha256 TEXT,
  change_type       TEXT NOT NULL,        -- ADDED|REMOVED|MODIFIED|BREAKING
  detected_at       TEXT NOT NULL,
  detail            TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_obs_subject ON observations(subject_id, predicate);
CREATE INDEX IF NOT EXISTS idx_meas_run ON probe_measurements(probe_run_id);
CREATE INDEX IF NOT EXISTS idx_meas_metric ON probe_measurements(metric, observed_at);
CREATE INDEX IF NOT EXISTS idx_runs_server ON probe_runs(server_id, started_at);
CREATE INDEX IF NOT EXISTS idx_windows_server ON server_windows(server_id, window_end);
CREATE INDEX IF NOT EXISTS idx_sc_server ON schema_changes(server_id, detected_at);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def get_conn() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript(SCHEMA)
        _local.conn = conn
    return conn


def close_conn() -> None:
    conn = getattr(_local, "conn", None)
    if conn is not None:
        conn.close()
        _local.conn = None


def init_db() -> None:
    get_conn().commit()


# ---------------------------------------------------------------------------
# Servers
# ---------------------------------------------------------------------------

def upsert_server(
    server_id: str,
    name: str,
    transport: str,
    description: str = "",
    source_registry: str = "manual",
    source_url: str = "",
    command: Optional[str] = None,
    args: Optional[list] = None,
    env: Optional[dict] = None,
    url: Optional[str] = None,
    auth_scheme: str = "none",
    auth_notes: str = "",
    deep_test: int = 0,
    status: str = "REGISTERED",
    discovered_at: Optional[str] = None,
    version: Optional[str] = None,
    install_command: str = "",
) -> dict:
    conn = get_conn()
    now = discovered_at or _now()
    conn.execute(
        """INSERT INTO servers
           (server_id, name, description, source_registry, source_url, transport,
            command, args_json, env_json, url, auth_scheme, auth_notes, status,
            deep_test, discovered_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(server_id) DO UPDATE SET
             name=excluded.name, description=excluded.description,
             source_registry=excluded.source_registry, source_url=excluded.source_url,
             transport=excluded.transport, command=excluded.command,
             args_json=excluded.args_json, env_json=excluded.env_json,
             url=excluded.url, auth_scheme=excluded.auth_scheme,
             auth_notes=excluded.auth_notes, status=excluded.status,
             deep_test=excluded.deep_test
        """,
        (
            server_id,
            name,
            description,
            source_registry,
            source_url,
            transport,
            command,
            json.dumps(args or []),
            json.dumps(env or {}),
            url,
            auth_scheme,
            auth_notes,
            status,
            deep_test,
            now,
        ),
    )
    if version:
        vid = f"{server_id}@{version}"
        conn.execute(
            """INSERT OR IGNORE INTO server_versions
               (server_version_id, server_id, version, install_command, installed_at)
               VALUES (?,?,?,?,?)""",
            (vid, server_id, version, install_command, now),
        )
        conn.execute(
            "UPDATE server_versions SET status='CURRENT' WHERE server_version_id=?",
            (vid,),
        )
    conn.commit()
    return get_server(server_id)  # type: ignore


def get_server(server_id: str) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM servers WHERE server_id=?", (server_id,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["args"] = json.loads(d.pop("args_json") or "[]")
    d["env"] = json.loads(d.pop("env_json") or "{}")
    vrow = conn.execute(
        "SELECT version, install_command FROM server_versions WHERE server_id=? AND status='CURRENT'",
        (server_id,),
    ).fetchone()
    d["current_version"] = dict(vrow) if vrow else None
    return d


def list_servers(status: Optional[str] = None, deep_test: Optional[int] = None) -> list[dict]:
    conn = get_conn()
    q = "SELECT * FROM servers"
    clauses, params = [], []
    if status:
        clauses.append("status=?")
        params.append(status)
    if deep_test is not None:
        clauses.append("deep_test=?")
        params.append(deep_test)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY server_id"
    rows = conn.execute(q, params).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["args"] = json.loads(d.pop("args_json") or "[]")
        d["env"] = json.loads(d.pop("env_json") or "{}")
        out.append(d)
    return out


def retire_server(server_id: str) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE servers SET status='RETIRED', retired_at=? WHERE server_id=?",
        (_now(), server_id),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------

def ensure_capabilities(cap_ids: list[str]) -> None:
    conn = get_conn()
    for c in cap_ids:
        conn.execute(
            "INSERT OR IGNORE INTO capabilities (capability_id, label) VALUES (?,?)",
            (c, c),
        )
    conn.commit()


def list_capabilities() -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT c.*, COUNT(tc.tool_id) AS tool_count FROM capabilities c "
        "LEFT JOIN tool_capabilities tc ON tc.capability_id = c.capability_id "
        "GROUP BY c.capability_id ORDER BY c.capability_id"
    ).fetchall()
    return [dict(r) for r in rows]


def set_tool_capabilities(tool_id: str, mappings: list[tuple[str, float, str]]) -> None:
    """mappings: [(capability_id, confidence, method)]"""
    conn = get_conn()
    for cap_id, conf, method in mappings:
        conn.execute(
            """INSERT INTO tool_capabilities (tool_id, capability_id, confidence, mapping_method)
               VALUES (?,?,?,?)
               ON CONFLICT(tool_id, capability_id) DO UPDATE SET
                 confidence=excluded.confidence, mapping_method=excluded.mapping_method""",
            (tool_id, cap_id, conf, method),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# Tools + schema fingerprint
# ---------------------------------------------------------------------------

def canonical_tool_schema(name: str, description: str, input_schema: dict) -> str:
    """Canonical fingerprint payload: {name, description, inputSchema}."""
    canon = {"name": name, "description": description or "", "inputSchema": input_schema or {}}
    return json.dumps(canon, sort_keys=True, separators=(",", ":"))


def schema_token_count(schema_json: str) -> int:
    """Rough token footprint of a canonical schema JSON (chars/4)."""
    return max(1, len(schema_json) // 4)


def upsert_tool(
    server_id: str, name: str, description: str, input_schema: dict,
    safety_class: str, observed_at: Optional[str] = None,
) -> dict:
    """Insert/update a tool; detect schema fingerprints and log changes."""
    conn = get_conn()
    now = observed_at or _now()
    tool_id = _tool_id(server_id, name)
    canon = canonical_tool_schema(name, description, input_schema)
    new_hash = _sha256(canon)
    tokens = schema_token_count(canon)

    row = conn.execute("SELECT * FROM tools WHERE tool_id=?", (tool_id,)).fetchone()
    if row is None:
        conn.execute(
            """INSERT INTO tools
               (tool_id, server_id, name, description, input_schema, schema_sha256,
                schema_token_count, safety_class, first_seen, last_seen)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (tool_id, server_id, name, description, canon, new_hash, tokens, safety_class, now, now),
        )
        conn.execute(
            """INSERT INTO schema_changes
               (change_id, server_id, tool_name, new_schema_sha256, change_type, detected_at, detail)
               VALUES (?,?,?,?,?,?,?)""",
            (_sha256(f"ADDED|{server_id}|{name}|{now}"), server_id, name, new_hash, "ADDED", now, "tool first seen"),
        )
    else:
        old_hash = row["schema_sha256"]
        conn.execute(
            """UPDATE tools SET description=?, input_schema=?, schema_sha256=?,
               schema_token_count=?, safety_class=?, last_seen=? WHERE tool_id=?""",
            (description, canon, new_hash, tokens, safety_class, now, tool_id),
        )
        if old_hash != new_hash:
            change_type = classify_schema_change(
                json.loads(row["input_schema"]) if row["input_schema"] else {},
                input_schema,
            )
            conn.execute(
                """INSERT INTO schema_changes
                   (change_id, server_id, tool_name, old_schema_sha256, new_schema_sha256,
                    change_type, detected_at, detail)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    _sha256(f"CHG|{server_id}|{name}|{now}"),
                    server_id, name, old_hash, new_hash, change_type, now,
                    f"schema fingerprint changed: {old_hash[:12]} -> {new_hash[:12]}",
                ),
            )
    conn.commit()
    return get_tool(tool_id)  # type: ignore


def classify_schema_change(old_schema: dict, new_schema: dict) -> str:
    """Heuristic: required-property removal or property type change = BREAKING."""
    def _props(s: dict) -> dict:
        return s.get("properties") or {}

    def _required(s: dict) -> set:
        return set(s.get("required") or [])

    old_props, new_props = _props(old_schema), _props(new_schema)
    old_required = _required(old_schema)
    new_required = _required(new_schema)

    for prop in old_required:
        if prop not in new_required:
            return "BREAKING"
    for prop, spec in old_props.items():
        if prop in new_props and _type_of(spec) != _type_of(new_props[prop]) and _type_of(new_props[prop]) != "any":
            return "BREAKING"
    if json.dumps(old_schema, sort_keys=True) != json.dumps(new_schema, sort_keys=True):
        return "MODIFIED"
    return "MODIFIED"


def _type_of(spec: Any) -> str:
    if isinstance(spec, dict):
        return str(spec.get("type", "any"))
    return "any"


def get_tool(tool_id: str) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM tools WHERE tool_id=?", (tool_id,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["input_schema"] = json.loads(d["input_schema"] or "{}") if d.get("input_schema") else {}
    caps = conn.execute(
        """SELECT c.capability_id, c.label, tc.confidence, tc.mapping_method
           FROM tool_capabilities tc JOIN capabilities c ON c.capability_id=tc.capability_id
           WHERE tc.tool_id=?""",
        (tool_id,),
    ).fetchall()
    d["capabilities"] = [dict(r) for r in caps]
    return d


def list_tools(server_id: Optional[str] = None, capability: Optional[str] = None,
               safety: Optional[str] = None) -> list[dict]:
    conn = get_conn()
    q = "SELECT * FROM tools"
    clauses, params = [], []
    if server_id:
        clauses.append("server_id=?")
        params.append(server_id)
    if safety:
        clauses.append("safety_class=?")
        params.append(safety)
    if capability:
        q = (
            "SELECT t.* FROM tools t JOIN tool_capabilities tc ON tc.tool_id=t.tool_id "
            "WHERE tc.capability_id=?"
        )
        params = [capability]
        clauses = []
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY server_id, name"
    rows = conn.execute(q, params).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["input_schema"] = json.loads(d["input_schema"] or "{}") if d.get("input_schema") else {}
        out.append(d)
    return out


def _tool_id(server_id: str, name: str) -> str:
    return _sha256(f"{server_id}|{name}")


# ---------------------------------------------------------------------------
# Probe runs + measurements (append-only)
# ---------------------------------------------------------------------------

def start_probe_run(
    server_id: str, probe_type: str, method_version: str, run_dir: str, region: str = "local",
) -> str:
    conn = get_conn()
    run_id = f"run_{server_id.replace('@', '_').replace(':', '_')[:48]}_{_now().replace(':', '').replace('.', '')}"
    conn.execute(
        """INSERT INTO probe_runs
           (probe_run_id, server_id, probe_type, started_at, probe_region, method_version, status, run_dir)
           VALUES (?,?,?,?,?,?,?,?)""",
        (run_id, server_id, probe_type, _now(), region, method_version, "RUNNING", run_dir),
    )
    conn.commit()
    return run_id


def finish_probe_run(
    run_id: str, status: str, error_class: Optional[str] = None, error_detail: str = "",
) -> None:
    conn = get_conn()
    conn.execute(
        """UPDATE probe_runs SET status=?, completed_at=?, error_class=?, error_detail=?
           WHERE probe_run_id=?""",
        (status, _now(), error_class, error_detail[:2000], run_id),
    )
    conn.commit()


def record_measurement(
    run_id: str, metric: str, value_numeric: Optional[float], value_text: Optional[str],
    unit: str = "", state: str = STATE_KNOWN, observed_at: Optional[str] = None,
) -> str:
    conn = get_conn()
    now = observed_at or _now()
    mid = _sha256(f"{run_id}|{metric}|{now}|{value_numeric}|{value_text}")
    conn.execute(
        """INSERT INTO probe_measurements
           (measurement_id, probe_run_id, metric, value_numeric, value_text, unit, state, observed_at)
           VALUES (?,?,?,?,?,?,?,?)""",
        (mid, run_id, metric, value_numeric, value_text, unit, state, now),
    )
    conn.commit()
    return mid


def record_observation(envelope: dict) -> str:
    """Store one Oracle-compatible universal envelope, content-addressed."""
    conn = get_conn()
    payload = _without(envelope, "observation_id")
    oid = _sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    conn.execute(
        """INSERT OR IGNORE INTO observations
           (observation_id, envelope_json, subject_type, subject_id, predicate, state,
            observed_at, valid_until, source_id, method_id)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            oid,
            json.dumps(payload, sort_keys=True),
            payload["subject"]["type"],
            payload["subject"]["id"],
            payload["predicate"],
            payload["state"],
            payload["observed_at"],
            payload.get("valid_until"),
            payload["source"]["id"],
            payload["method"]["id"],
        ),
    )
    conn.commit()
    return oid


def get_observation(observation_id: str) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM observations WHERE observation_id=?", (observation_id,)
    ).fetchone()
    if row is None:
        return None
    env = json.loads(row["envelope_json"])
    env["observation_id"] = row["observation_id"]
    return env


def list_observations(subject_id: Optional[str] = None, predicate: Optional[str] = None,
                      limit: int = 100) -> list[dict]:
    conn = get_conn()
    q = "SELECT * FROM observations"
    clauses, params = [], []
    if subject_id:
        clauses.append("subject_id=?")
        params.append(subject_id)
    if predicate:
        clauses.append("predicate=?")
        params.append(predicate)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY observed_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(q, params).fetchall()
    out = []
    for r in rows:
        env = json.loads(r["envelope_json"])
        env["observation_id"] = r["observation_id"]
        out.append(env)
    return out


def get_measurements(server_id: Optional[str] = None, metric: Optional[str] = None,
                     limit: int = 500) -> list[dict]:
    conn = get_conn()
    q = (
        "SELECT m.*, r.server_id, r.status AS run_status, r.error_class "
        "FROM probe_measurements m JOIN probe_runs r ON r.probe_run_id=m.probe_run_id"
    )
    clauses, params = [], []
    if server_id:
        clauses.append("r.server_id=?")
        params.append(server_id)
    if metric:
        clauses.append("m.metric=?")
        params.append(metric)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY m.observed_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(q, params).fetchall()
    return [dict(r) for r in rows]


def get_probe_runs(server_id: Optional[str] = None, limit: int = 200) -> list[dict]:
    conn = get_conn()
    q = "SELECT * FROM probe_runs"
    params: list = []
    if server_id:
        q += " WHERE server_id=?"
        params.append(server_id)
    q += " ORDER BY started_at DESC LIMIT ?"
    params.append(limit)
    return [dict(r) for r in conn.execute(q, params).fetchall()]


def list_schema_changes(limit: int = 100, change_type: Optional[str] = None) -> list[dict]:
    conn = get_conn()
    q = "SELECT * FROM schema_changes"
    params: list = []
    if change_type:
        q += " WHERE change_type=?"
        params.append(change_type)
    q += " ORDER BY detected_at DESC LIMIT ?"
    params.append(limit)
    return [dict(r) for r in conn.execute(q, params).fetchall()]


# ---------------------------------------------------------------------------
# Server windows (derived projection; reducer-owned)
# ---------------------------------------------------------------------------

def upsert_window(window: dict) -> None:
    conn = get_conn()
    conn.execute(
        """INSERT INTO server_windows
           (server_id, window_start, window_end, samples, init_success_rate,
            tools_list_success_rate, connection_ms_p50, connection_ms_p95,
            invocation_ms_p50, invocation_ms_p95, invocation_success_rate,
            tool_count, schema_break_count)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(server_id, window_start) DO UPDATE SET
             window_end=excluded.window_end, samples=excluded.samples,
             init_success_rate=excluded.init_success_rate,
             tools_list_success_rate=excluded.tools_list_success_rate,
             connection_ms_p50=excluded.connection_ms_p50,
             connection_ms_p95=excluded.connection_ms_p95,
             invocation_ms_p50=excluded.invocation_ms_p50,
             invocation_ms_p95=excluded.invocation_ms_p95,
             invocation_success_rate=excluded.invocation_success_rate,
             tool_count=excluded.tool_count,
             schema_break_count=excluded.schema_break_count
        """,
        (
            window["server_id"], window["window_start"], window["window_end"],
            window["samples"], window.get("init_success_rate"),
            window.get("tools_list_success_rate"), window.get("connection_ms_p50"),
            window.get("connection_ms_p95"), window.get("invocation_ms_p50"),
            window.get("invocation_ms_p95"), window.get("invocation_success_rate"),
            window.get("tool_count"), window.get("schema_break_count", 0),
        ),
    )
    conn.commit()


def get_latest_windows(fresh_after: Optional[str] = None, limit: int = 500) -> list[dict]:
    """Latest window per server; optional freshness cut on window_end."""
    conn = get_conn()
    q = (
        "SELECT w.* FROM server_windows w "
        "JOIN (SELECT server_id, MAX(window_start) AS ws FROM server_windows "
        "      GROUP BY server_id) m ON m.server_id=w.server_id AND m.ws=w.window_start"
    )
    params: list = []
    if fresh_after:
        q = (
            "SELECT w.* FROM server_windows w "
            "JOIN (SELECT server_id, MAX(window_start) AS ws FROM server_windows "
            "      WHERE window_end>=? GROUP BY server_id) m "
            "ON m.server_id=w.server_id AND m.ws=w.window_start"
        )
        params = [fresh_after]
    q += " ORDER BY w.server_id LIMIT ?"
    params.append(limit)
    return [dict(r) for r in conn.execute(q, params).fetchall()]


def get_windows_for_server(server_id: str, limit: int = 200) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM server_windows WHERE server_id=? ORDER BY window_start DESC LIMIT ?",
        (server_id, limit),
    ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Stats / coverage
# ---------------------------------------------------------------------------

def stats() -> dict:
    conn = get_conn()
    def one(q: str, p: tuple = ()) -> int:
        return conn.execute(q, p).fetchone()[0]  # type: ignore

    return {
        "servers_tracked": one("SELECT COUNT(*) FROM servers WHERE status!='RETIRED'"),
        "servers_deep_tested": one("SELECT COUNT(*) FROM servers WHERE deep_test=1 AND status!='RETIRED'"),
        "servers_active": one("SELECT COUNT(*) FROM servers WHERE status='ACTIVE'"),
        "tools": one("SELECT COUNT(*) FROM tools"),
        "tools_by_safety": {
            s: one("SELECT COUNT(*) FROM tools WHERE safety_class=?", (s,))
            for s in ["READ_ONLY", "REVERSIBLE", "MUTATING", "UNKNOWN"]
        },
        "capabilities": one("SELECT COUNT(*) FROM capabilities"),
        "tool_capability_mappings": one("SELECT COUNT(*) FROM tool_capabilities"),
        "observations": one("SELECT COUNT(*) FROM observations"),
        "probe_runs": one("SELECT COUNT(*) FROM probe_runs"),
        "schema_changes": one("SELECT COUNT(*) FROM schema_changes"),
        "breaking_schema_changes": one("SELECT COUNT(*) FROM schema_changes WHERE change_type='BREAKING'"),
        "measurements": one("SELECT COUNT(*) FROM probe_measurements"),
    }


def coverage() -> dict:
    conn = get_conn()
    servers = list_servers()
    by_registry: dict[str, int] = {}
    for s in servers:
        by_registry[s["source_registry"]] = by_registry.get(s["source_registry"], 0) + 1
    by_transport: dict[str, int] = {}
    for s in servers:
        by_transport[s["transport"]] = by_transport.get(s["transport"], 0) + 1
    probe_types = [
        dict(r)
        for r in conn.execute(
            "SELECT probe_type, COUNT(*) AS runs, "
            "SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) AS succeeded "
            "FROM probe_runs GROUP BY probe_type"
        ).fetchall()
    ]
    return {
        "servers_total": len(servers),
        "servers_deep_test": len([s for s in servers if s["deep_test"]]),
        "by_registry": by_registry,
        "by_transport": by_transport,
        "by_auth": {
            s: len([x for x in servers if x["auth_scheme"] == s])
            for s in sorted({x["auth_scheme"] for x in servers})
        },
        "probe_types": probe_types,
        "deep_tested_endpoints": [
            {"server_id": s["server_id"], "name": s["name"], "transport": s["transport"]}
            for s in servers if s["deep_test"]
        ],
    }


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _sha256(data: str) -> str:
    import hashlib
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _without(d: dict, key: str) -> dict:
    out = dict(d)
    out.pop(key, None)
    return out