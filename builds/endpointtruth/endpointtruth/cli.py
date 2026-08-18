"""CLI: init-db / register / catalog / probe / cycle / schedule / aggregate /
resolve / serve / mcp / status.

Examples:
    endpointtruth init-db --db data/endpointtruth.db
    endpointtruth register --config config/endpoints.yaml
    endpointtruth catalog --provider openrouter --db ...
    endpointtruth cycle --endpoint opencode-go:deepseek-v4-flash
    endpointtruth schedule --cycles 3 --interval 0 --endpoints config/endpoints.yaml --probes all
    endpointtruth aggregate --window-min 5
    endpointtruth resolve --capability coding --tools --min-context 64000
    endpointtruth serve --port 8777
    endpointtruth mcp [--jsonrpc]
    endpointtruth status
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Optional

import yaml

from . import __version__
from .aggregator import aggregate_windows
from .db import DB
from .probes import DiscoveryProbe, probe_instances
from .resolve import resolve
from .runner import Runner
from .scheduler import Scheduler
from .schema import Endpoint, utcnow

DEFAULT_DB = "data/endpointtruth.db"
DEFAULT_RUNS = "data/runs"


def _db(args) -> DB:
    return DB(getattr(args, "db", None) or DEFAULT_DB)


def _endpoints_from_config(path: str) -> list[Endpoint]:
    with open(path) as fh:
        cfg = yaml.safe_load(fh)
    eps: list[Endpoint] = []
    for entry in cfg.get("endpoints", []):
        ep = Endpoint(
            endpoint_id=entry["endpoint_id"],
            provider_id=entry["provider_id"],
            model_id=entry["model_id"],
            provider_model_name=entry.get("provider_model_name", entry["model_id"]),
            base_url=entry.get("base_url", ""),
            region=entry.get("region", ""),
            deployment_variant=entry.get("deployment_variant", ""),
            quantization_state=entry.get("quantization_state", "unknown"),
            advertised_context_tokens=entry.get("advertised_context_tokens"),
            tools_advertised=bool(entry.get("tools_advertised", False)),
            json_advertised=bool(entry.get("json_advertised", False)),
            pricing=entry.get("pricing", {}),
            api_key_env=entry.get("api_key_env"),
            base_url_env=entry.get("base_url_env"),
            discovered_at=utcnow(),
        )
        eps.append(ep)
    return eps


def cmd_init_db(args):
    db = _db(args)
    print(f"db initialized: {db.path} (endpoints={db.count_endpoints()})")
    db.close()


def cmd_register(args):
    db = _db(args)
    eps = _endpoints_from_config(args.config)
    for ep in eps:
        db.upsert_endpoint(ep)
    print(f"registered {len(eps)} endpoints -> {db.count_endpoints()} total")
    db.close()


def cmd_catalog(args):
    """Run discovery-v1 against a provider's public catalog and register the
    discovered endpoints + advertised observations."""
    db = _db(args)
    provider = args.provider
    if provider == "openrouter":
        probe = DiscoveryProbe()
        pseudo = Endpoint(endpoint_id="openrouter:catalog",
                          provider_id="openrouter", model_id="catalog",
                          provider_model_name="catalog",
                          base_url="https://openrouter.ai/api/v1",
                          api_key_env="OPENROUTER_API_KEY")
    else:
        raise SystemExit(f"unknown catalog provider: {provider}")
    runner = Runner(db, runs_root=args.runs)
    run_id, result = runner.run_sync(pseudo, probe)
    n_eps = 0
    for meta_ep in result.meta.get("endpoints", []):
        ep = Endpoint(**{k: v for k, v in meta_ep.items()})
        db.upsert_endpoint(ep)
        n_eps += 1
    print(json.dumps({
        "run_id": run_id,
        "status": result.status,
        "catalog_models": n_eps,
        "observations": len(result.measurements),
        "errors": result.errors,
    }, indent=2))
    db.close()


def cmd_probe(args):
    db = _db(args)
    ep = db.get_endpoint(args.endpoint)
    if ep is None:
        raise SystemExit(f"unknown endpoint {args.endpoint}")
    probe = probe_instances([args.probe],
                            max_output_tokens=args.max_tokens,
                            max_context_bucket=args.max_context)[args.probe]
    runner = Runner(db, runs_root=args.runs)
    run_id, result = runner.run_sync(ep, probe)
    print(json.dumps({
        "run_id": run_id, "endpoint": args.endpoint, "probe": args.probe,
        "status": result.status, "errors": result.errors,
        "measurements": [m.envelope() for m in result.measurements],
    }, indent=2, default=str))
    db.close()


def cmd_cycle(args):
    db = _db(args)
    ep = db.get_endpoint(args.endpoint)
    if ep is None:
        raise SystemExit(f"unknown endpoint {args.endpoint}")
    probes = probe_instances(probe_ids=args.probes or None,
                             max_output_tokens=args.max_tokens,
                             max_context_bucket=args.max_context)
    runner = Runner(db, runs_root=args.runs)
    counts = {}
    for pid, probe in probes.items():
        run_id, result = runner.run_sync(ep, probe)
        counts[pid] = {"run_id": run_id, "status": result.status, "errors": result.errors}
    print(json.dumps({"endpoint": args.endpoint, "runs": counts}, indent=2, default=str))
    db.close()


def cmd_schedule(args):
    db = _db(args)
    ep_ids = args.endpoints or []
    if not ep_ids and args.config:
        eps = _endpoints_from_config(args.config)
    else:
        eps = []
        for eid in ep_ids:
            ep = db.get_endpoint(eid)
            if ep is None:
                raise SystemExit(f"unknown endpoint {eid}")
            eps.append(ep)
    if not eps:
        raise SystemExit("no endpoints to schedule (pass --endpoints or --config)")
    runner = Runner(db, runs_root=args.runs)
    sched = Scheduler(db, runner, endpoints=eps,
                      probe_ids=args.probes or None,
                      cycles=args.cycles, interval_seconds=args.interval,
                      concurrency=args.concurrency,
                      max_output_tokens=args.max_tokens,
                      max_context_bucket=args.max_context,
                      runs_root=args.runs)
    result = asyncio.run(sched.run())
    fp = sched.write_summary(result)
    print(json.dumps({
        "summary_file": fp,
        "cycles": result.cycles_completed,
        "probe_runs": result.probe_runs,
        "observations": result.observations,
        "failures": result.failures,
        "skipped": result.skipped,
    }, indent=2))
    db.close()


def cmd_aggregate(args):
    db = _db(args)
    n = aggregate_windows(db, window_seconds=args.window_min * 60)
    print(f"upserted {n} window rows")
    db.close()


def cmd_resolve(args):
    db = _db(args)
    out = resolve(db, capability=args.capability, tools=args.tools,
                  min_context=args.min_context, limit=args.limit)
    print(json.dumps(out, indent=2, default=str))
    db.close()


def cmd_status(args):
    db = _db(args)
    runs = db.conn.execute("SELECT status, COUNT(*) c FROM probe_runs GROUP BY status").fetchall()
    obs = db.conn.execute("SELECT state, COUNT(*) c FROM probe_measurements GROUP BY state").fetchall()
    provs = [r["provider_id"] for r in db.conn.execute(
        "SELECT DISTINCT provider_id FROM endpoints ORDER BY provider_id").fetchall()]
    probe_types = [r["probe_type"] for r in db.conn.execute(
        "SELECT DISTINCT probe_type FROM probe_runs ORDER BY probe_type").fetchall()]
    print(json.dumps({
        "version": __version__,
        "db": db.path,
        "endpoints": db.count_endpoints(),
        "probe_runs": db.count_probe_runs(),
        "observations": db.count_observations(),
        "windows": db.conn.execute("SELECT COUNT(*) c FROM endpoint_windows").fetchone()["c"],
        "providers": provs,
        "probe_types": probe_types,
        "runs_by_status": {r["status"]: r["c"] for r in runs},
        "observations_by_state": {r["state"]: r["c"] for r in obs},
    }, indent=2))
    db.close()


def cmd_serve(args):
    import uvicorn
    os.environ.setdefault("ENDPOINTTRUTH_DB", args.db or DEFAULT_DB)
    os.environ.setdefault("ENDPOINTTRUTH_STALE_SECONDS", str(args.stale))
    os.environ.setdefault("ENDPOINTTRUTH_WINDOW_SECONDS", str(args.window_min * 60))
    uvicorn.run("endpointtruth.api:app", host=args.host, port=args.port, log_level="info")


def cmd_mcp(args):
    from . import mcp_server
    mcp_server.run(transport="stdio", force_jsonrpc=args.jsonrpc)


def main(argv: Optional[list[str]] = None):
    p = argparse.ArgumentParser(prog="endpointtruth", description="EndpointTruth MVP")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--db", default=DEFAULT_DB)
        sp.add_argument("--runs", default=DEFAULT_RUNS)

    sp = sub.add_parser("init-db", help="create schema"); common(sp)
    sp = sub.add_parser("register", help="register endpoints from yaml")
    common(sp); sp.add_argument("--config", required=True)
    sp = sub.add_parser("catalog", help="discover provider catalog")
    common(sp); sp.add_argument("--provider", default="openrouter")
    sp = sub.add_parser("probe", help="run one probe on one endpoint")
    common(sp); sp.add_argument("--endpoint", required=True); sp.add_argument("--probe", required=True)
    sp.add_argument("--max-tokens", type=int, default=160); sp.add_argument("--max-context", type=int, default=8192)
    sp = sub.add_parser("cycle", help="run all probes on one endpoint")
    common(sp); sp.add_argument("--endpoint", required=True)
    sp.add_argument("--probes", nargs="*")
    sp.add_argument("--max-tokens", type=int, default=160); sp.add_argument("--max-context", type=int, default=8192)
    sp = sub.add_parser("schedule", help="probe loop across endpoints")
    common(sp); sp.add_argument("--endpoints", nargs="*")
    sp.add_argument("--config"); sp.add_argument("--probes", nargs="*")
    sp.add_argument("--cycles", type=int, default=1); sp.add_argument("--interval", type=float, default=0.0)
    sp.add_argument("--concurrency", type=int, default=4)
    sp.add_argument("--max-tokens", type=int, default=160); sp.add_argument("--max-context", type=int, default=8192)
    sp = sub.add_parser("aggregate", help="build endpoint_windows")
    common(sp); sp.add_argument("--window-min", type=int, default=15)
    sp = sub.add_parser("resolve", help="resolution scoring")
    common(sp); sp.add_argument("--capability", default="chat")
    sp.add_argument("--tools", action="store_true"); sp.add_argument("--min-context", type=int)
    sp.add_argument("--limit", type=int, default=5)
    sp = sub.add_parser("serve", help="run FastAPI")
    sp.add_argument("--db", default=DEFAULT_DB); sp.add_argument("--host", default="127.0.0.1")
    sp.add_argument("--port", type=int, default=8777)
    sp.add_argument("--stale", type=int, default=3600); sp.add_argument("--window-min", type=int, default=15)
    sp = sub.add_parser("mcp", help="run MCP stdio server")
    sp.add_argument("--jsonrpc", action="store_true", help="hand-rolled JSON-RPC (no SDK)")
    sp = sub.add_parser("status", help="counts and state"); common(sp)

    args = p.parse_args(argv)
    handlers = {
        "init-db": cmd_init_db, "register": cmd_register, "catalog": cmd_catalog,
        "probe": cmd_probe, "cycle": cmd_cycle, "schedule": cmd_schedule,
        "aggregate": cmd_aggregate, "resolve": cmd_resolve, "serve": cmd_serve,
        "mcp": cmd_mcp, "status": cmd_status,
    }
    handlers[args.cmd](args)


if __name__ == "__main__":
    main()