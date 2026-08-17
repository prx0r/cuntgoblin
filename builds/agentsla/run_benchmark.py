#!/usr/bin/env python3
"""run_benchmark.py — AgentSLA benchmark driver (spec: TASK DATASET -> RUN MANIFEST -> RUNNER).

Modes:
  --bench benchmarks/bench_v1.json           run the full live benchmark (real model calls)
  --cell TASK_CLASS ARCHITECTURE [--attempt N] [--model M]   run one live cell
  --demo TASK_CLASS ARCHITECTURE             run one cell with a SCRIPTED stub (no network;
                                             pipeline self-check only, not an observation)
  --summary [--task TASK_CLASS]              print SLA summary from the database
  --demo-everything                          run all cells with stubs (offline pipeline test)

Real observations = runs produced by --bench/--cell. Anything from --demo is a
harness check and is marked `stub=true` in the run.json manifest.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.client import LLMClient  # noqa: E402
from app.db import connect  # noqa: E402
from app.dataset import TASK_CLASSES  # noqa: E402
from app.fake import (  # noqa: E402
    MATHLIB_FIX,
    PARSE_LOG_FIX,
    RESEARCH_PERFECT,
    FakeClient,
)
from app.metrics import RunRow, sla_summary  # noqa: E402
from app.runner import DB_PATH, _git_sha, run_cell  # noqa: E402

STUB_PATCHES = {
    "coding.patch": MATHLIB_FIX,
    "coding.debug": PARSE_LOG_FIX,
    "research.answer": RESEARCH_PERFECT,
}


def _env_credentials() -> tuple[str, str]:
    base_url = os.environ.get("OPENCODE_GO_BASE_URL", "")
    api_key = os.environ.get("OPENCODE_GO_API_KEY", "")
    if not base_url or not api_key:
        raise SystemExit("OPENCODE_GO_BASE_URL and OPENCODE_GO_API_KEY must be set for live runs")
    return base_url, api_key


def make_stub_client(model: str, task_class: str):
    """A FakeClient whose script answers perfectly for the task class."""
    patch = STUB_PATCHES.get(task_class, "")

    def responder(messages):
        from app.client import ChatResult

        system = messages[0]["content"] if messages else ""
        if "verif" in system.lower() or "verify a" in system.lower() or "You verify" in system:
            return ChatResult(content="APPROVED", status="ok",
                              prompt_tokens=50, completion_tokens=10, total_tokens=60)
        if "produce a short numbered" in system or "step-by-step plan" in system:
            return ChatResult(content="1. inspect\n2. fix\n3. submit\nPLAN COMPLETE", status="ok",
                              prompt_tokens=40, completion_tokens=15, total_tokens=55)
        if task_class in ("coding.patch", "coding.debug"):
            return ChatResult(
                content="Submitting the fix.",
                status="ok",
                tool_calls=[{
                    "id": "call_stub_1", "type": "function",
                    "function": {"name": "submit_patch", "arguments": json.dumps({"diff": patch})},
                }],
                prompt_tokens=120, completion_tokens=40, total_tokens=160,
            )
        return ChatResult(content=patch, status="ok",
                          prompt_tokens=100, completion_tokens=30, total_tokens=130)

    return FakeClient(model=model, responder=responder)


def make_client(model: str, stub: bool, task_class: str | None = None):
    if stub:
        return make_stub_client(model, task_class or "coding.patch")
    base_url, api_key = _env_credentials()
    return LLMClient(base_url, api_key, model, timeout=90, max_retries=2)


def _point_at(db_path_: str, runs_dir: str) -> None:
    """Point the DB + run-envelope dirs at demo paths when running stubs, so the
    real observation store (data/agentsla.db, data/runs/) is never polluted."""
    os.environ["AGENTSLA_DB"] = db_path_
    os.environ["AGENTSLA_RUNS_DIR"] = runs_dir
    import app.evidence
    import app.runner

    app.runner.DB_PATH = Path(db_path_)
    app.evidence.RUNS_ROOT = Path(runs_dir)


def run_cell_cli(
    conn, *, task_class: str, architecture_id: str, arch_config: dict,
    model: str, attempt: int, stub: bool, benchmark_id: str, base_url: str = "",
) -> dict:
    client = make_client(model, stub, task_class)
    manifest = run_cell(
        conn, benchmark_id=benchmark_id, task_class=task_class,
        architecture_id=architecture_id, arch_config=arch_config,
        client=client, attempt=attempt, base_url=base_url or ("stub://" if stub else _env_credentials()[0]),
        git_sha=_git_sha(),
    )
    client.close()
    if stub:
        manifest["stub"] = True
        # write manifest with stub flag back into the envelope
        from app.evidence import RunEnvelope
        RunEnvelope(manifest["run_id"]).write_run_json(manifest)
    return manifest


def run_benchmark(bench: dict, stub: bool = False, limit_classes: list[str] | None = None):
    db_file = Path(DB_PATH)
    if stub:
        _point_at("/tmp/agentsla-demo/agentsla-demo.db", "/tmp/agentsla-demo/runs")
        db_file = Path("/tmp/agentsla-demo/agentsla-demo.db")
    conn = connect(db_file)
    benchmark_id = bench["benchmark_id"]
    model = bench.get("model", "deepseek-v4-flash")
    archs = bench["architectures"]
    classes = bench["task_classes"] if not limit_classes else limit_classes
    total = len(classes) * len(archs) * int(bench.get("attempts", 1))
    done = 0
    results = []
    base_url = "" if stub else _env_credentials()[0]
    started = time.time()
    for task_class in classes:
        for arch_id, arch_config in archs.items():
            for attempt in range(1, int(bench.get("attempts", 1)) + 1):
                done += 1
                print(f"[{done}/{total}] {task_class} × {arch_id} attempt={attempt} "
                      f"({'stub' if stub else 'live'})", flush=True)
                t0 = time.time()
                try:
                    manifest = run_cell_cli(
                        conn, task_class=task_class, architecture_id=arch_id,
                        arch_config=arch_config, model=model, attempt=attempt,
                        stub=stub, benchmark_id=benchmark_id, base_url=base_url,
                    )
                    results.append(manifest)
                    print(f"    -> status={manifest['status']} success={manifest.get('success')} "
                          f"cost=${manifest.get('cost_usd', 0):.4f} "
                          f"dur={manifest.get('duration_seconds', 0):.1f}s "
                          f"({time.time()-t0:.1f}s wall, {len(manifest.get('evaluations', []))} evals)", flush=True)
                except Exception as exc:  # noqa: BLE001
                    print(f"    !! cell error: {exc!r}", flush=True)
    print(f"\nBENCHMARK {benchmark_id} DONE in {time.time()-started:.0f}s "
          f"({len(results)}/{total} cells completed)", flush=True)
    return results


def print_summary(task_class: str | None = None, conn=None):
    if conn is None:
        conn = connect(Path(DB_PATH))
    classes = [task_class] if task_class else sorted(TASK_CLASSES)
    for tc in classes:
        print(f"\n=== task class: {tc} ===")
        rows = conn.execute(
            """SELECT a.architecture_id, r.* FROM runs r
               JOIN architecture_versions av ON av.architecture_version_id = r.architecture_version_id
               JOIN architectures a ON a.architecture_id = av.architecture_id
               JOIN task_versions tv ON tv.task_version_id = r.task_version_id
               JOIN tasks t ON t.task_id = tv.task_id
               WHERE t.task_class = ? AND r.status != 'running'
               ORDER BY a.architecture_id, r.started_at""",
            (tc,),
        ).fetchall()
        per_arch: dict[str, list[RunRow]] = {}
        for r in rows:
            per_arch.setdefault(r["architecture_id"], []).append(
                RunRow(
                    success=bool(r["success"]) if r["success"] is not None else False,
                    cost_usd=float(r["cost_usd"] or 0.0),
                    duration_seconds=float(r["duration_seconds"] or 0.0),
                    input_tokens=int(r["input_tokens"] or 0),
                    output_tokens=int(r["output_tokens"] or 0),
                    tool_calls=int(r["tool_calls"] or 0),
                    retries=int(r["retries"] or 0),
                )
            )
        if not rows:
            print("  (no runs yet)")
            continue
        print(f"  {'arch':<28} {'n':>3} {'ok':>3} {'succ%':>6} {'wilsonLB':>8} {'$/att':>8} {'$/succ':>8} {'sec/succ':>9} {'insuff':>7}")
        for aid, runs in sorted(per_arch.items(), key=lambda kv: sum(r.cost_usd for r in kv[1]) / len(kv[1])):
            s = sla_summary(runs)
            print(f"  {aid:<28} {s.n:>3} {s.successes:>3} {s.success_rate*100:>5.1f}% {s.success_rate_ci[0]:>8.3f} "
                  f"{s.cost_per_attempt:>8.4f} {s.cost_per_success:>8.4f} {s.duration_per_success:>9.1f} "
                  f"{'YES' if s.insufficient_evidence else ''}")


def main() -> int:
    ap = argparse.ArgumentParser(description="AgentSLA benchmark driver")
    ap.add_argument("--bench", type=str, help="path to benchmark JSON")
    ap.add_argument("--live", action="store_true", help="bench runs real model calls (default off unless --bench)")
    ap.add_argument("--cell", nargs=2, metavar=("TASK_CLASS", "ARCH"), help="run one cell")
    ap.add_argument("--demo", nargs=2, metavar=("TASK_CLASS", "ARCH"), help="run one cell with stub client")
    ap.add_argument("--demo-everything", action="store_true", help="run cells for all classes x archs with stubs")
    ap.add_argument("--model", default="deepseek-v4-flash")
    ap.add_argument("--attempt", type=int, default=1)
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--task", type=str, default=None, help="filter for --summary")
    ap.add_argument("--bench-id", default="agentsla-bench-v1")
    args = ap.parse_args()

    db_file = Path(DB_PATH)
    if args.demo or args.demo_everything or (args.bench and not args.live):
        db_file = Path("/tmp/agentsla-demo/agentsla-demo.db")
        _point_at(str(db_file), "/tmp/agentsla-demo/runs")
    conn = connect(db_file)

    if args.summary:
        print_summary(args.task, conn)
        return 0

    if args.demo:
        task_class, arch = args.demo
        arch_config = _arch_config_for(arch, args.model)
        manifest = run_cell_cli(
            conn, task_class=task_class, architecture_id=arch, arch_config=arch_config,
            model=args.model, attempt=args.attempt, stub=True, benchmark_id="stub-demo",
        )
        print(json.dumps(manifest, indent=2, default=str))
        return 0

    if args.demo_everything:
        bench = {
            "benchmark_id": "stub-demo-all",
            "model": args.model,
            "architectures": {
                "single_agent": {"components": [{"role": "worker", "model": args.model, "max_steps": 6}], "max_steps": 6},
                "worker_verifier": {"components": [{"role": "worker", "model": args.model, "max_steps": 6},
                                                    {"role": "verifier", "model": args.model}], "max_steps": 6, "max_rounds": 1},
                "planner_worker": {"components": [{"role": "planner", "model": args.model},
                                                   {"role": "worker", "model": args.model, "max_steps": 6}], "max_steps": 6},
                "parallel_candidates_judge": {"components": [{"role": "worker", "model": args.model, "max_steps": 6}],
                                              "max_steps": 6, "n_candidates": 2},
            },
            "task_classes": sorted(TASK_CLASSES),
            "attempts": 1,
        }
        run_benchmark(bench, stub=True)
        print_summary(None, conn)
        return 0

    if args.cell:
        task_class, arch = args.cell
        arch_config = _arch_config_for(arch, args.model)
        manifest = run_cell_cli(
            conn, task_class=task_class, architecture_id=arch, arch_config=arch_config,
            model=args.model, attempt=args.attempt, stub=False, benchmark_id=args.bench_id,
        )
        print(json.dumps(manifest, indent=2, default=str))
        return 0

    if args.bench:
        bench = json.loads(Path(args.bench).read_text(encoding="utf-8"))
        stub = not args.live
        if not args.live:
            print("WARNING: --bench without --live runs STUB cells (pipeline check only, "
                  "not observations). Pass --live for real model calls.", file=sys.stderr)
        run_benchmark(bench, stub=stub)
        print_summary(None, conn)
        return 0

    ap.print_help()
    return 1


def _arch_config_for(arch: str, model: str) -> dict:
    if arch == "single_agent":
        return {"components": [{"role": "worker", "model": model, "max_steps": 6}], "max_steps": 6}
    if arch == "worker_verifier":
        return {"components": [{"role": "worker", "model": model, "max_steps": 6},
                               {"role": "verifier", "model": model}], "max_steps": 6, "max_rounds": 2}
    if arch == "planner_worker":
        return {"components": [{"role": "planner", "model": model},
                               {"role": "worker", "model": model, "max_steps": 6}], "max_steps": 6}
    if arch == "parallel_candidates_judge":
        return {"components": [{"role": "worker", "model": model, "max_steps": 6}],
                "max_steps": 6, "n_candidates": 3}
    raise SystemExit(f"unknown architecture {arch}")


if __name__ == "__main__":
    raise SystemExit(main())