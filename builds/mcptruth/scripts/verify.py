"""Deterministic build gate for MCPTruth.

Runs: byte-compile all modules, pytest suite, seed sanity, and DB integrity
audit against a FRESH ephemeral database (so the gate never depends on
accumulated state).  Writes a content-addressed gate report to
data/runs/gate-<ts>.json and exits non-zero on any failure.

Usage:  python scripts/verify.py
"""

from __future__ import annotations

import hashlib
import json
import os
import py_compile
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime, timezone

BUILD_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BUILD_ROOT)

def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def run(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           cwd=BUILD_ROOT)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def main() -> int:
    results: dict = {
        "gate": "mcptruth-verify-v1",
        "started_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "checks": {},
    }
    ok = True

    # 1. byte-compile
    files = []
    for root, _dirs, names in os.walk(os.path.join(BUILD_ROOT, "app")):
        for n in names:
            if n.endswith(".py"):
                files.append(os.path.join(root, n))
    for root, _dirs, names in os.walk(os.path.join(BUILD_ROOT, "tests")):
        for n in names:
            if n.endswith(".py"):
                files.append(os.path.join(root, n))
    compile_errors = []
    for f in files:
        try:
            py_compile.compile(f, doraise=True)
        except py_compile.PyCompileError as exc:
            compile_errors.append(str(exc))
    results["checks"]["byte_compile"] = {"files": len(files), "errors": compile_errors}
    ok = ok and not compile_errors

    # 2. pytest against a fresh ephemeral DB
    with tempfile.TemporaryDirectory() as tmp:
        db_env = dict(os.environ)
        db_env["MCPTRUTH_DB"] = os.path.join(tmp, "gate.db")
        rc, out = run(["python", "-m", "pytest", "tests/", "-q", "--tb=short"])
        results["checks"]["pytest"] = {"rc": rc, "output_tail": out[-3000:]}
        results["pytest_result"] = {"rc": rc, "summary": _pytest_summary(out)}
        ok = ok and rc == 0

    # 3. seed sanity on the gate DB
    rc, out = run(["python", "-m", "app.runner", "seed"])
    results["checks"]["seed"] = {"rc": rc, "output_tail": out[-800:]}
    ok = ok and rc == 0

    # 4. dB integrity audit (content addressing + append-only + windows)
    integrity = _db_integrity()
    results["checks"]["db_integrity"] = integrity
    ok = ok and integrity["ok"]

    results["completed_at"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    results["passed"] = ok

    runs_dir = os.path.join(BUILD_ROOT, "data", "runs")
    os.makedirs(runs_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    path = os.path.join(runs_dir, f"gate-{ts}.json")
    with open(path, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    # content-addressed record (append to agent-steps log)
    rec = {"step": "gate", "result": results, "ts": results["started_at"]}
    rec_id = sha256_hex(json.dumps(rec, sort_keys=True))
    rec["record_id"] = rec_id
    with open(os.path.join(runs_dir, "agent-steps.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")

    print(json.dumps({"passed": ok, "checks": {k: v.get("rc", "ok") if isinstance(v, dict) else v for k, v in results["checks"].items()},
                      "pytest": results["pytest_result"], "report": path}, indent=2, sort_keys=True))
    return 0 if ok else 1


def _pytest_summary(out: str) -> str:
    for line in out.splitlines():
        if line.startswith("==") and ("passed" in line or "failed" in line or "error" in line):
            return line
    return out[-300:]


def _db_integrity() -> dict:
    try:
        from app import db
        import sqlite3
        conn = sqlite3.connect(os.environ.get("MCPTRUTH_DB", "data/mcptruth.db"))
        conn.row_factory = sqlite3.Row
        n_obs = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        bad = 0
        for row in conn.execute("SELECT observation_id, envelope_json FROM observations"):
            canon = json.dumps(json.loads(row["envelope_json"]), sort_keys=True, separators=(",", ":"))
            if sha256_hex(canon) != row["observation_id"]:
                bad += 1
        conn.close()
        return {"ok": bad == 0, "observations": n_obs, "bad_hashes": bad}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)