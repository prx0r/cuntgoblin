"""End-to-end runner tests with scripted stub clients (no network).

These verify the full pipeline: task workspace -> model calls -> deterministic
grading -> cost events -> evidence envelope -> DB finalize.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import connect  # noqa: E402
from app.fake import MATHLIB_FIX, PARSE_LOG_FIX, RESEARCH_PERFECT, FakeClient, make_scripted_client  # noqa: E402
from app.runner import run_cell  # noqa: E402

SCHEMA_REQUIRED = {"tasks", "task_versions", "architectures", "architecture_versions",
                   "runs", "run_components", "model_calls", "tool_calls",
                   "evaluations", "cost_events"}


def _arch(name, model="fake-model"):
    if name == "single_agent":
        return {"components": [{"role": "worker", "model": model, "max_steps": 6}], "max_steps": 6}
    if name == "worker_verifier":
        return {"components": [{"role": "worker", "model": model, "max_steps": 6},
                               {"role": "verifier", "model": model}], "max_steps": 6, "max_rounds": 1}
    if name == "planner_worker":
        return {"components": [{"role": "planner", "model": model},
                               {"role": "worker", "model": model, "max_steps": 6}], "max_steps": 6}
    if name == "parallel_candidates_judge":
        return {"components": [{"role": "worker", "model": model, "max_steps": 6}],
                "max_steps": 6, "n_candidates": 2}
    raise ValueError(name)


@pytest.fixture()
def conn(db_path):
    return connect(db_path)


def _count(conn, table, run_id=None):
    if run_id:
        return conn.execute(f"SELECT COUNT(*) AS c FROM {table} WHERE run_id=?", (run_id,)).fetchone()["c"]
    return conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]


def test_single_agent_coding_patch_success(conn):
    client = FakeClient("fake-model", responder=lambda msgs: __import__("app.fake", fromlist=["ChatResult"]).ChatResult(
        content="Submitting fix.",
        status="ok",
        tool_calls=[{"id": "c1", "type": "function",
                     "function": {"name": "submit_patch", "arguments": json.dumps({"diff": MATHLIB_FIX})}}],
        prompt_tokens=100, completion_tokens=50, total_tokens=150,
    ))
    manifest = run_cell(conn, benchmark_id="test", task_class="coding.patch",
                        architecture_id="single_agent", arch_config=_arch("single_agent"),
                        client=client, attempt=1, base_url="stub://", git_sha="abc123")
    assert manifest["success"] is True
    assert manifest["status"] == "success"
    assert manifest["git_sha"] == "abc123"
    assert manifest["model_calls"] >= 1
    assert manifest["cost_usd"] > 0
    assert _count(conn, "evaluations", manifest["run_id"]) >= 3
    assert _count(conn, "model_calls", manifest["run_id"]) >= 1
    assert _count(conn, "cost_events", manifest["run_id"]) >= 1


def test_single_agent_wrong_patch_failure(conn):
    wrong = "--- a/src/mathlib.py\n+++ b/src/mathlib.py\n@@ -17,7 +17,7 @@\n-    return ordered[mid - 1] + ordered[mid] / 2.0\n+    return 0.0\n"
    client = FakeClient("fake-model", responder=lambda msgs: __import__("app.fake", fromlist=["ChatResult"]).ChatResult(
        content="done",
        status="ok",
        tool_calls=[{"id": "c1", "type": "function",
                     "function": {"name": "submit_patch", "arguments": json.dumps({"diff": wrong})}}],
        prompt_tokens=100, completion_tokens=50, total_tokens=150,
    ))
    manifest = run_cell(conn, benchmark_id="test", task_class="coding.patch",
                        architecture_id="single_agent", arch_config=_arch("single_agent"),
                        client=client, attempt=1, base_url="stub://", git_sha="")
    assert manifest["success"] is False
    assert manifest["status"] == "failure"


def test_single_agent_no_patch_failure_reason(conn):
    client = FakeClient("fake-model", responder=lambda msgs: __import__("app.fake", fromlist=["ChatResult"]).ChatResult(
        content="I give up.", status="ok", prompt_tokens=10, completion_tokens=5, total_tokens=15,
    ))
    manifest = run_cell(conn, benchmark_id="test", task_class="coding.patch",
                        architecture_id="single_agent", arch_config=_arch("single_agent"),
                        client=client, attempt=1, base_url="stub://", git_sha="")
    assert manifest["success"] is False
    assert "no_patch" in (manifest.get("failure_reason") or "")


def test_research_answer_success(conn):
    client = FakeClient("fake-model", responder=lambda msgs: __import__("app.fake", fromlist=["ChatResult"]).ChatResult(
        content=RESEARCH_PERFECT, status="ok",
        prompt_tokens=200, completion_tokens=60, total_tokens=260,
    ))
    manifest = run_cell(conn, benchmark_id="test", task_class="research.answer",
                        architecture_id="single_agent", arch_config=_arch("single_agent"),
                        client=client, attempt=1, base_url="stub://", git_sha="")
    assert manifest["success"] is True


def test_worker_verifier_rounds(conn):
    """Verifier says REVISIONS once, then APPROVED; two worker calls expected."""
    calls = {"n": 0, "verifier_calls": 0}

    def responder(messages):
        from app.fake import ChatResult

        system = messages[0]["content"] if messages else ""
        if "verif" in system.lower() or "You verify" in system or "verify a" in system.lower():
            calls["verifier_calls"] += 1
            verdict = "APPROVED" if calls["verifier_calls"] > 1 else "REVISIONS: add edge case handling"
            return ChatResult(content=verdict, status="ok", prompt_tokens=50, completion_tokens=10, total_tokens=60)
        calls["n"] += 1
        return ChatResult(
            content="Submitting fix.",
            status="ok",
            tool_calls=[{"id": "c1", "type": "function",
                         "function": {"name": "submit_patch", "arguments": json.dumps({"diff": MATHLIB_FIX})}}],
            prompt_tokens=100, completion_tokens=50, total_tokens=150,
        )

    client = FakeClient("fake-model", responder=responder)
    manifest = run_cell(conn, benchmark_id="test", task_class="coding.patch",
                        architecture_id="worker_verifier", arch_config=_arch("worker_verifier"),
                        client=client, attempt=1, base_url="stub://", git_sha="")
    assert manifest["success"] is True
    assert calls["n"] >= 2  # revision round happened
    assert calls["verifier_calls"] == 2


def test_parallel_candidates_judge_picks_best(conn):
    """Candidate 0 submits a wrong patch; candidate 1 submits the correct one.
    The deterministic judge must pick candidate 1."""
    cand = {"n": 0}

    def responder(messages):
        from app.fake import ChatResult

        cand["n"] += 1
        patch = MATHLIB_FIX if cand["n"] >= 2 else "--- a/src/mathlib.py\n+++ b/src/mathlib.py\n@@ -17,7 +17,7 @@\n-    return ordered[mid - 1] + ordered[mid] / 2.0\n+    return 0.0\n"
        return ChatResult(
            content="Submitting.",
            status="ok",
            tool_calls=[{"id": "c1", "type": "function",
                         "function": {"name": "submit_patch", "arguments": json.dumps({"diff": patch})}}],
            prompt_tokens=100, completion_tokens=50, total_tokens=150,
        )

    client = FakeClient("fake-model", responder=responder)
    manifest = run_cell(conn, benchmark_id="test", task_class="coding.patch",
                        architecture_id="parallel_candidates_judge",
                        arch_config=_arch("parallel_candidates_judge"),
                        client=client, attempt=1, base_url="stub://", git_sha="")
    assert manifest["success"] is True
    assert cand["n"] == 2  # both candidates ran


def test_envelope_written(conn):
    client = make_scripted_client("fake-model", MATHLIB_FIX)[0]
    manifest = run_cell(conn, benchmark_id="test", task_class="coding.patch",
                        architecture_id="single_agent", arch_config=_arch("single_agent"),
                        client=client, attempt=1, base_url="stub://", git_sha="")
    from app.evidence import RUNS_ROOT

    env_dir = RUNS_ROOT / manifest["run_id"]
    assert (env_dir / "run.json").exists()
    assert (env_dir / "stdout.log").exists()
    assert (env_dir / "results.jsonl").exists()
    assert (env_dir / "artifacts" / "final.patch").exists()
    run_json = json.loads((env_dir / "run.json").read_text(encoding="utf-8"))
    assert run_json["run_id"] == manifest["run_id"]
    assert run_json["sha256"]
    events = [json.loads(l) for l in (env_dir / "results.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    kinds = {e["kind"] for e in events}
    assert "model_call" in kinds
    assert "evaluation" in kinds
    assert "cost_event" in kinds or any("cost" in k for k in kinds)


def test_all_architectures_leave_consistent_rows(conn):
    for arch in ("single_agent", "worker_verifier", "planner_worker", "parallel_candidates_judge"):
        client = make_scripted_client("fake-model", MATHLIB_FIX)[0]
        manifest = run_cell(conn, benchmark_id="test2", task_class="coding.patch",
                            architecture_id=arch, arch_config=_arch(arch),
                            client=client, attempt=1, base_url="stub://", git_sha="")
        assert manifest["model_calls"] > 0
        assert manifest["evaluations"]
        assert _count(conn, "run_components", manifest["run_id"]) >= 1