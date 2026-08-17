"""check.py — the deterministic LOGGED GATE for the AgentSLA build.

Runs (each prints PASS/FAIL, exits non-zero on any FAIL):
  1. imports          every app module compiles and imports
  2. schema           SQLite DB has all 10 spec tables
  3. unit             pytest suite passes (offline, no network)
  4. envelope         every recorded run envelope has run.json + results.jsonl
  5. manifest         MANIFEST.json doc references resolve to existing files
  6. nofake           no stub-demo run may be presented as a live observation
                      (run.json manifests carrying "stub": true are excluded
                      from every SLA summary surface)
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

GREEN = "\033[92mPASS\033[0m"
RED = "\033[91mFAIL\033[0m"


def check(name: str, fn) -> bool:
    try:
        ok, detail = fn()
    except Exception as exc:  # noqa: BLE001
        ok, detail = False, f"exception: {exc!r}"
    print(f"  {GREEN if ok else RED}  {name}" + (f"  — {detail}" if ok is False else ""))
    return ok


def gate() -> int:
    results = []
    results.append(check("imports", _check_imports))
    results.append(check("schema", _check_schema))
    results.append(check("unit", _check_unit))
    results.append(check("envelope", _check_envelope))
    results.append(check("manifest", _check_manifest))
    results.append(check("nofake", _check_nofake))
    n_ok = sum(results)
    print(f"\nAgentSLA gate: {n_ok}/{len(results)} checks PASS "
          f"({'ALL PASS' if all(results) else 'FAILURES PRESENT'})")
    return 0 if all(results) else 1


def _check_imports():
    from app import api, client, cost, dataset, db, evidence, grader, metrics, prices, runner  # noqa: F401
    return True, ""


def _check_schema():
    from app.db import connect

    conn = connect(BASE_DIR / "data" / "agentsla.db")
    from app.db import table_names

    tables = table_names(conn)
    required = {"tasks", "task_versions", "architectures", "architecture_versions",
                "runs", "run_components", "model_calls", "tool_calls",
                "evaluations", "cost_events"}
    missing = required - set(tables)
    return (not missing), f"missing tables: {sorted(missing)}" if missing else f"{len(tables)} tables present"


def _check_unit():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=str(BASE_DIR), capture_output=True, text=True, timeout=600,
    )
    ok = proc.returncode == 0
    tail = (proc.stdout + proc.stderr).strip().splitlines()
    detail = tail[-1] if tail else ""
    return ok, detail


def _check_envelope():
    from app.evidence import RunEnvelope

    runs = RunEnvelope.list_runs(BASE_DIR / "data" / "runs")
    if not runs:
        return True, "no runs recorded yet (acceptable pre-benchmark)"
    bad = []
    for rid in runs:
        env = RunEnvelope(rid, BASE_DIR / "data" / "runs" / rid)
        if not (env.dir / "run.json").exists():
            bad.append(f"{rid}:missing run.json")
        if not (env.dir / "results.jsonl").exists():
            bad.append(f"{rid}:missing results.jsonl")
    return (not bad), f"{len(runs)} envelopes, bad: {bad[:5]}" if bad else f"{len(runs)} envelopes valid"


def _check_manifest():
    manifest = json.loads((BASE_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    missing = []
    for path in manifest.get("docs", {}):
        if not (BASE_DIR / path).exists():
            missing.append(path)
    return (not missing), f"missing referenced docs: {missing[:5]}" if missing else f"{len(manifest['docs'])} docs resolved"


def _check_nofake():
    """Stub runs must be excluded from SLA surfaces. Verify the DB marker."""
    from app.db import connect

    conn = connect(BASE_DIR / "data" / "agentsla.db")
    rows = conn.execute(
        "SELECT run_id, benchmark_id FROM runs WHERE benchmark_id LIKE 'stub%' AND success IS NOT NULL"
    ).fetchall()
    if rows:
        return False, f"stub runs still present as observations: {[r['run_id'] for r in rows][:5]}"
    return True, "no stub runs masquerading as observations"


if __name__ == "__main__":
    raise SystemExit(gate())