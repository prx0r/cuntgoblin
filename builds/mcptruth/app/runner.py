"""MCPTruth runner CLI.

  python -m app.runner seed                 seed the tracked-server registry
  python -m app.runner probe --server ID    probe one server (full cycle)
  python -m app.runner probe --all          probe all discovery targets
  python -m app.runner probe --deep --limit N
  python -m app.runner reduce [--minutes 15]
  python -m app.runner demo                 seed + probe mock + reduce + summary
  python -m app.runner show                 current tracked/healthiest state

Every run logs a content-addressed, timestamped agent-step record to
data/runs/agent-steps.jsonl (repo convention) and writes raw probe artifacts to
data/runs/<run-id>/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import traceback
from datetime import datetime, timezone

from . import db, oracle
from .discovery import discovery_targets, seed_registry
from .harness import run_probe_cycle
from . import reducer

BUILD_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS_DIR = os.path.join(BUILD_ROOT, "data", "runs")


def content_address(data: dict) -> str:
    canon = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def log_step(step: str, result: dict) -> str:
    os.makedirs(RUNS_DIR, exist_ok=True)
    record = {
        "step": step,
        "result": result,
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "env": {"db": db.DB_PATH},
    }
    rec_id = content_address(record)
    with open(os.path.join(RUNS_DIR, "agent-steps.jsonl"), "a") as f:
        f.write(json.dumps(record) + "\n")
    # repo-level tracking (venturelab/AGENTS.md)
    try:
        root_runs = os.path.join(os.path.dirname(BUILD_ROOT), "data", "runs")
        os.makedirs(root_runs, exist_ok=True)
        with open(os.path.join(root_runs, "agent-steps.jsonl"), "a") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass
    return rec_id


def cmd_seed(args) -> dict:
    db.init_db()
    res = seed_registry(force=True)
    log_step("seed", res)
    return res


def cmd_probe(args) -> dict:
    db.init_db()
    servers: list[dict]
    if args.server:
        s = db.get_server(args.server)
        if s is None:
            print(f"unknown server: {args.server}", file=sys.stderr)
            sys.exit(2)
        servers = [s]
    else:
        servers = discovery_targets(
            limit=args.limit, only_deep=args.deep
        )
    out = {"probed": [], "failed": 0}
    for s in servers:
        summary = run_probe_cycle(
            s, timeout_ms=args.timeout_ms, region=args.region
        )
        out["probed"].append(summary)
        out["failed"] += 1 if summary["status"] != "SUCCESS" else 0
        print(f"[{summary['status']}] {s['server_id']} :: {summary.get('error_class') or ''} {summary.get('error_detail') or ''}".strip())
    # refresh window projections after probing
    res = reducer.reduce_windows(window_minutes=args.reduce_minutes)
    out["reduce"] = res
    log_step("probe", {"probed": len(out["probed"]), "failed": out["failed"], "reduce": res})
    return out


def cmd_reduce(args) -> dict:
    db.init_db()
    res = reducer.reduce_windows(window_minutes=args.minutes)
    log_step("reduce", res)
    return res


def cmd_demo(args) -> dict:
    db.init_db()
    seed = cmd_seed(args)
    print(f"seeded: {seed}")
    # deterministic local mock first, then up to N real deep targets
    targets = discovery_targets(limit=None, only_deep=True)
    mock = [t for t in targets if t["server_id"] == "mock:mock-mcp"]
    real = [t for t in targets if t["server_id"] != "mock:mock-mcp"]
    order = mock + real
    if args.only_mock:
        order = mock
    results = []
    for s in order[: args.max_servers]:
        summary = run_probe_cycle(s, timeout_ms=args.timeout_ms, region=args.region)
        results.append(summary)
        print(f"[{summary['status']}] {s['server_id']} :: {summary.get('error_class') or ''}")
    red = reducer.reduce_windows(window_minutes=15)
    top = reducer.healthiest(limit=10)
    summary_out = {
        "seed": seed,
        "probed": results,
        "reduce": red,
        "healthiest": [
            {"rank": h["rank"], "server_id": h["server"]["server_id"],
             "name": h["server"]["name"],
             "connection_ms_p50": h["window"].get("connection_ms_p50"),
             "invocation_success_rate": h["window"].get("invocation_success_rate")}
            for h in top
        ],
        "stats": db.stats(),
    }
    log_step("demo", summary_out)
    return summary_out


def cmd_show(args) -> dict:
    db.init_db()
    out = {
        "stats": db.stats(),
        "coverage": db.coverage(),
        "healthiest": [
            {"rank": h["rank"], "server_id": h["server"]["server_id"],
             "name": h["server"]["name"], "transport": h["server"]["transport"],
             "freshness_seconds": h["window"].get("freshness_seconds", 0),
             "connection_ms_p50": h["window"].get("connection_ms_p50"),
             "invocation_ms_p50": h["window"].get("invocation_ms_p50"),
             "invocation_success_rate": h["window"].get("invocation_success_rate"),
             "schema_break_count": h["window"].get("schema_break_count", 0)}
            for h in reducer.healthiest(limit=20)
        ],
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(prog="mcptruth", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("seed", help="seed tracked-server registry")
    p.set_defaults(fn=cmd_seed)

    p = sub.add_parser("probe", help="probe one or many servers")
    p.add_argument("--server", default=None)
    p.add_argument("--all", dest="all", action="store_true")
    p.add_argument("--deep", action="store_true", help="only deep-test targets")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--timeout-ms", type=int, default=25000)
    p.add_argument("--region", default="local")
    p.add_argument("--reduce-minutes", type=int, default=15)
    p.set_defaults(fn=cmd_probe)

    p = sub.add_parser("reduce", help="recompute derived windows")
    p.add_argument("--minutes", type=int, default=15)
    p.set_defaults(fn=cmd_reduce)

    p = sub.add_parser("demo", help="seed + probe (mock first) + reduce + summary")
    p.add_argument("--max-servers", type=int, default=3)
    p.add_argument("--only-mock", action="store_true")
    p.add_argument("--timeout-ms", type=int, default=25000)
    p.add_argument("--region", default="local")
    p.set_defaults(fn=cmd_demo)

    p = sub.add_parser("show", help="print current tracked/healthiest state")
    p.set_defaults(fn=cmd_show)

    args = parser.parse_args()
    try:
        result = args.fn(args)
        if args.cmd != "show":
            print(json.dumps(result, indent=2, sort_keys=True))
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        log_step("error", {"cmd": args.cmd, "exc": traceback.format_exc()[-2000:]})
        sys.exit(1)


if __name__ == "__main__":
    main()