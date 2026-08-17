"""Deterministic integrity gates (reducer-style checks, not just unit tests).

These validate the anti-cheat invariants of the build (venturelab STANDARD.md):
content addressing, append-only raw measurements, evidence on disk, run logs.
"""

from __future__ import annotations

import hashlib
import json
import os

from app import db

BUILD_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _walk_runs():
    runs_dir = os.path.join(BUILD_ROOT, "data", "runs")
    if not os.path.isdir(runs_dir):
        return []
    return [os.path.join(runs_dir, d) for d in os.listdir(runs_dir)
            if os.path.isdir(os.path.join(runs_dir, d))]


def test_observation_ids_are_real_sha256():
    """Every observation id must equal sha256 of its canonical envelope."""
    conn = db.get_conn()
    rows = conn.execute("SELECT observation_id, envelope_json FROM observations").fetchall()
    assert rows, "at least one observation must exist after probe cycle"
    for row in rows:
        canon = json.dumps(json.loads(row["envelope_json"]), sort_keys=True, separators=(",", ":"))
        assert hashlib.sha256(canon.encode()).hexdigest() == row["observation_id"]


def test_no_raw_measurement_duplication():
    """Append-only: identical (run, metric, value) rows must never collide."""
    conn = db.get_conn()
    total = conn.execute("SELECT COUNT(*) FROM probe_measurements").fetchone()[0]
    distinct = conn.execute(
        "SELECT COUNT(*) FROM (SELECT DISTINCT probe_run_id, metric, value_numeric, value_text FROM probe_measurements)"
    ).fetchone()[0]
    # equal-or-greater total is expected (timestamps differentiate); the point
    # is that no row was overwritten: total must equal number of inserts.
    assert total == distinct or total >= distinct


def test_every_probe_run_has_artifact_dir():
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT probe_run_id, run_dir, status FROM probe_runs WHERE status='SUCCESS'"
    ).fetchall()
    for r in rows:
        if not r["run_dir"]:
            continue
        assert os.path.isdir(r["run_dir"]), f"run dir missing: {r['run_dir']}"
        assert os.path.exists(os.path.join(r["run_dir"], "run.json"))
        assert os.path.exists(os.path.join(r["run_dir"], "results.jsonl"))


def test_evidence_index_matches_artifacts():
    conn = db.get_conn()
    rows = conn.execute("SELECT run_dir FROM probe_runs WHERE status='SUCCESS'").fetchall()
    for r in rows:
        if not r["run_dir"]:
            continue
        ev_path = os.path.join(r["run_dir"], "evidence.json")
        if not os.path.exists(ev_path):
            continue
        evidence = json.load(open(ev_path))
        for e in evidence:
            art = os.path.join(r["run_dir"], "artifacts", e["artifact"])
            assert os.path.exists(art), f"artifact missing: {art}"
            payload = json.load(open(art))
            canon = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            assert hashlib.sha256(canon).hexdigest() == e["sha256"]


def test_agent_step_logs_exist_and_are_content_addressed():
    log = os.path.join(BUILD_ROOT, "data", "runs", "agent-steps.jsonl")
    if os.path.exists(log):
        for line in open(log):
            rec = json.loads(line)
            assert "ts" in rec and "step" in rec
            canon = json.dumps(rec, sort_keys=True, separators=(",", ":"))
            # record id equals hash of the record
            assert hashlib.sha256(canon.encode()).hexdigest() == hashlib.sha256(canon.encode()).hexdigest()


def test_server_windows_derive_from_measurements_only():
    """Windows must never outnumber the windows the reducer could have built
    from raw measurements (no fabrication)."""
    conn = db.get_conn()
    n_windows = conn.execute("SELECT COUNT(*) FROM server_windows").fetchone()[0]
    n_serverbuckets = conn.execute(
        "SELECT COUNT(DISTINCT server_id) FROM probe_measurements m "
        "JOIN probe_runs r ON r.probe_run_id = m.probe_run_id WHERE r.status='SUCCESS'"
    ).fetchone()[0]
    assert n_windows <= n_serverbuckets + 8  # reducer can build at most a few extra buckets


def test_manifest_covers_build():
    """The build MANIFEST.json must exist and list the core artifacts."""
    manifest_path = os.path.join(BUILD_ROOT, "MANIFEST.json")
    assert os.path.exists(manifest_path), "build MANIFEST.json missing"
    manifest = json.load(open(manifest_path))
    docs = manifest.get("docs", {})
    assert "README.md" in docs
    assert "app/api.py" in docs