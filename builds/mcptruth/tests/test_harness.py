"""End-to-end harness tests against the real local mock MCP server.

These run actual stdio JSON-RPC traffic through the mcp SDK client, so they
exercise transport, initialize, tools/list, schema fingerprinting, invocation,
and safety classification for real.
"""

from __future__ import annotations

import json
import os

from app import db, oracle
from app.harness import Harness, SAFE_ARGS, classify_error, classify_tool, run_probe_cycle

MOCK = "mock:mock-mcp"


def test_mock_probe_succeeds(mock_probe_summary):
    assert mock_probe_summary["status"] == "SUCCESS"
    assert mock_probe_summary["measurements"] >= 6
    assert mock_probe_summary["observations"] >= 3
    assert os.path.isdir(mock_probe_summary["run_dir"])


def test_run_artifacts_written(mock_probe_summary):
    run_dir = mock_probe_summary["run_dir"]
    assert os.path.exists(os.path.join(run_dir, "run.json"))
    assert os.path.exists(os.path.join(run_dir, "results.jsonl"))
    assert os.path.exists(os.path.join(run_dir, "evidence.json"))
    arts = os.path.join(run_dir, "artifacts")
    assert os.path.isdir(arts)
    names = set(os.listdir(arts))
    assert "tool-echo.json" in names
    assert "invoke-echo.json" in names
    run = json.load(open(os.path.join(run_dir, "run.json")))
    assert run["run_id"] == mock_probe_summary["run_id"]
    # evidence index hashes must match artifact payloads
    ev = json.load(open(os.path.join(run_dir, "evidence.json")))
    for e in ev:
        payload = json.load(open(os.path.join(run_dir, "artifacts", e["artifact"])))
        assert e["sha256"] == oracle.artifact_sha256(payload)


def test_measurements_recorded(mock_probe_summary, seeded_db):
    ms = db.get_measurements(server_id=MOCK)
    metrics = {m["metric"] for m in ms}
    assert "init.success" in metrics
    assert "tools_list.success" in metrics
    assert "connection.ms" in metrics
    assert "tool.count" in metrics
    init = [m for m in ms if m["metric"] == "init.success"]
    assert all(m["value_numeric"] == 1 for m in init)
    conn = [m["value_numeric"] for m in ms if m["metric"] == "connection.ms"]
    assert all(c > 0 for c in conn)


def test_tools_discovered_with_safety_classes(seeded_db):
    tools = db.list_tools(server_id=MOCK)
    by_name = {t["name"]: t for t in tools}
    assert set(by_name) == {"echo", "add", "read_doc", "list_tree", "web_search", "mutate_state"}
    assert by_name["echo"]["safety_class"] == "READ_ONLY"
    assert by_name["add"]["safety_class"] == "READ_ONLY"
    assert by_name["read_doc"]["safety_class"] == "READ_ONLY"
    assert by_name["mutate_state"]["safety_class"] == "MUTATING"
    # every tool must carry a schema fingerprint
    for t in tools:
        assert len(t["schema_sha256"]) == 64
        assert t["schema_token_count"] > 0


def test_schema_fingerprint_stable_across_probes(seeded_db, mock_server):
    """Re-probing must NOT create spurious schema changes."""
    before = {
        t["name"]: t["schema_sha256"] for t in db.list_tools(server_id=MOCK)
    }
    changes_before = len(db.list_schema_changes())
    summary = run_probe_cycle(mock_server)
    assert summary["status"] == "SUCCESS"
    changes_after = len(db.list_schema_changes())
    after = {t["name"]: t["schema_sha256"] for t in db.list_tools(server_id=MOCK)}
    assert before == after, "identical server must not change fingerprints"
    assert changes_after == changes_before, "no spurious schema changes allowed"


def test_safe_args_only_read_only_invoked(seeded_db, mock_probe_summary):
    """MUTATING tool must never be invoked; its observation is NOT_APPLICABLE."""
    inv_obs = db.list_observations(predicate="tool.invocation")
    mut = [o for o in inv_obs if "mutate_state" in o["subject"]["id"]]
    assert mut, "mutate_state should have an invocation observation"
    assert all(o["state"] == "NOT_APPLICABLE" for o in mut)
    ok = [o for o in inv_obs if o["state"] == "KNOWN"]
    assert any("echo" in o["subject"]["id"] for o in ok)
    # and no invocation artifact may exist for mutate_state
    run_dir = mock_probe_summary["run_dir"]
    names = set(os.listdir(os.path.join(run_dir, "artifacts")))
    assert not any("mutate_state" in n for n in names)


def test_invocation_success_and_latency(seeded_db):
    runs = db.get_probe_runs(server_id=MOCK)
    succ = [m for m in db.get_measurements(server_id=MOCK) if m["metric"] == "invocation.success"]
    assert succ and all(m["value_numeric"] == 1.0 for m in succ if m["state"] == "KNOWN")
    lat = [m["value_numeric"] for m in db.get_measurements(server_id=MOCK)
           if m["metric"] == "invocation.ms" and m["value_numeric"] is not None]
    assert lat and all(v > 0 for v in lat)


def test_failed_invocation_recorded(seeded_db, mock_server):
    """Tool advertised and callable but fails with bad args -> invocation FALSE."""
    old = dict(SAFE_ARGS)
    try:
        SAFE_ARGS[("mock:echo", "echo")] = {"text": 12345}  # wrong type -> error
        summary = run_probe_cycle(mock_server)
        assert summary["status"] == "SUCCESS"  # server itself is fine
    finally:
        SAFE_ARGS.clear()
        SAFE_ARGS.update(old)
    ms = db.get_measurements(server_id=MOCK)
    inv_succ = [m for m in ms if m["metric"] == "invocation.success" and m["value_text"]]
    assert any(m["value_numeric"] == 0 for m in inv_succ), (
        "a failing invocation must be recorded as 0"
    )


def test_unreachable_server_classified_connection_error(seeded_db):
    from app.harness import run_probe_cycle
    bogus = {
        "server_id": "ghost:does-not-exist",
        "name": "Ghost", "transport": "stdio",
        "command": "/nonexistent/binary-xyz", "args": [], "env": {},
        "source_registry": "manual", "source_url": "", "auth_scheme": "none",
        "auth_notes": "", "status": "REGISTERED", "deep_test": 1,
        "description": "advertised but unreachable",
    }
    summary = run_probe_cycle(bogus, timeout_ms=8000)
    assert summary["status"] == "FAILED"
    assert summary["error_class"] == "CONNECTION_ERROR"
    runs = [r for r in db.get_probe_runs(server_id="ghost:does-not-exist")]
    assert runs and runs[0]["error_class"] == "CONNECTION_ERROR"


def test_garbage_stdio_server_recorded_failed(seeded_db):
    """A server that speaks garbage on the wire must fail initialize, not hang."""
    garbage = {
        "server_id": "ghost:garbage-stdio",
        "name": "Garbage", "transport": "stdio",
        "command": "python3", "args": ["-c", "import sys; print('not-json'); sys.exit(0)"],
        "env": {}, "source_registry": "manual", "source_url": "",
        "auth_scheme": "none", "auth_notes": "", "status": "REGISTERED", "deep_test": 1,
        "description": "responds with non-JSON-RPC",
    }
    summary = run_probe_cycle(garbage, timeout_ms=8000)
    assert summary["status"] == "FAILED"
    assert summary["error_class"] in ("INIT_FAILED", "TIMEOUT", "CONNECTION_ERROR")


def test_rate_limit_distinguished_from_outage():
    ec, _ = classify_error(RuntimeError("HTTP 429: too many requests. quota exceeded"))
    assert ec == "RATE_LIMITED"
    ec2, _ = classify_error(ConnectionRefusedError("connection refused"))
    assert ec2 == "CONNECTION_ERROR"
    ec3, _ = classify_error(TimeoutError("timed out"))
    assert ec3 == "TIMEOUT"


def test_classify_tool_safety():
    assert classify_tool("read_file", "read a file") == "READ_ONLY"
    assert classify_tool("write_file", "write to a file") == "MUTATING"
    assert classify_tool("create_issue", "open a new issue") == "MUTATING"
    assert classify_tool("delete_entity", "remove an entity") == "MUTATING"
    assert classify_tool("get_issue", "query an issue") == "READ_ONLY"
    assert classify_tool("xyzzy_plugh", "mystery operation") == "UNKNOWN"


def test_observations_content_addressed(mock_probe_summary):
    obs = db.list_observations(subject_id=db._tool_id(MOCK, "echo"))
    assert obs
    for o in obs:
        assert len(o["observation_id"]) == 64
        # deterministic: re-hash the envelope minus id == stored id
        payload = {k: v for k, v in o.items() if k != "observation_id"}
        import hashlib, json as _json
        canon = _json.dumps(payload, sort_keys=True, separators=(",", ":"))
        assert hashlib.sha256(canon.encode()).hexdigest() == o["observation_id"]


def test_evidence_lookup(mock_probe_summary):
    obs = db.list_observations(limit=1)
    assert obs
    env = db.get_observation(obs[0]["observation_id"])
    assert env is not None
    assert env["observation_id"] == obs[0]["observation_id"]
    assert env["subject"]["type"] in ("tool", "mcpserver")
    assert env["method"]["id"]  # method id present
    assert env["state"] in db.STATES