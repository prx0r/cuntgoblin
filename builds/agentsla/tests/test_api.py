"""API surface tests (testclient, no real network; DB from stub runs)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from app.api import app  # noqa: E402
from app.db import connect  # noqa: E402
from app.fake import MATHLIB_FIX, RESEARCH_PERFECT, FakeClient  # noqa: E402
from app.runner import run_cell  # noqa: E402


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def seeded(conn):
    """Create runs for each architecture on coding.patch (success) plus one
    research.answer run, so SLA/compare/frontier have data to serve."""
    archs = ["single_agent", "worker_verifier", "planner_worker", "parallel_candidates_judge"]
    cfg = {
        "single_agent": {"components": [{"role": "worker", "model": "fake", "max_steps": 6}], "max_steps": 6},
        "worker_verifier": {"components": [{"role": "worker", "model": "fake", "max_steps": 6},
                                           {"role": "verifier", "model": "fake"}], "max_steps": 6, "max_rounds": 1},
        "planner_worker": {"components": [{"role": "planner", "model": "fake"},
                                          {"role": "worker", "model": "fake", "max_steps": 6}], "max_steps": 6},
        "parallel_candidates_judge": {"components": [{"role": "worker", "model": "fake", "max_steps": 6}],
                                      "max_steps": 6, "n_candidates": 2},
    }
    for arch in archs:
        for attempt in (1, 2):
            client = FakeClient("fake", responder=lambda msgs: __import__("app.fake", fromlist=["ChatResult"]).ChatResult(
                content="Submitting.",
                status="ok",
                tool_calls=[{"id": "c1", "type": "function",
                             "function": {"name": "submit_patch", "arguments": json.dumps({"diff": MATHLIB_FIX})}}],
                prompt_tokens=100, completion_tokens=50, total_tokens=150,
            ))
            run_cell(conn, benchmark_id="apiTest", task_class="coding.patch",
                     architecture_id=arch, arch_config=cfg[arch], client=client,
                     attempt=attempt, base_url="stub://", git_sha="")
    rc = FakeClient("fake", responder=lambda msgs: __import__("app.fake", fromlist=["ChatResult"]).ChatResult(
        content=RESEARCH_PERFECT, status="ok", prompt_tokens=100, completion_tokens=50, total_tokens=150,
    ))
    run_cell(conn, benchmark_id="apiTest", task_class="research.answer",
             architecture_id="single_agent",
             arch_config=cfg["single_agent"], client=rc, attempt=1, base_url="stub://", git_sha="")
    yield


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "runs" in data["tables"]


def test_stats(client, seeded):
    r = client.get("/v1/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["runs"] >= 9
    assert data["tasks"] >= 2
    assert data["cost_events"] > 0


def test_coverage(client, seeded):
    r = client.get("/v1/coverage")
    assert r.status_code == 200
    data = r.json()
    assert "coding.patch" in data["task_classes"]
    cells = {c["task_class"] for c in data["matrix"]}
    assert "research.answer" in cells
    patch_cells = [c for c in data["matrix"] if c["task_class"] == "coding.patch"]
    assert all(c["runs"] >= 2 for c in patch_cells)


def test_evidence_unknown_404(client):
    r = client.get("/v1/evidence/does-not-exist")
    assert r.status_code == 404


def test_evidence_exists(client, seeded):
    from app.evidence import RUNS_ROOT

    runs = [d for d in RUNS_ROOT.iterdir() if d.is_dir() and (d / "run.json").exists()]
    assert runs
    rid = runs[0].name
    r = client.get(f"/v1/evidence/{rid}")
    assert r.status_code == 200
    data = r.json()
    assert data["manifest"]["success"] is True
    assert data["manifest"]["sha256"]


def test_architectures(client, seeded):
    r = client.get("/v1/architectures")
    assert r.status_code == 200
    ids = {a["architecture_id"] for a in r.json()["architectures"]}
    assert "single_agent" in ids


def test_sla(client, seeded):
    r = client.get("/v1/architectures/single_agent/sla")
    assert r.status_code == 200
    data = r.json()
    assert data["n"] >= 2
    assert data["success_rate"] == 1.0
    assert 0.0 < data["cost_per_attempt_usd"] <= 10.0


def test_compare(client, seeded):
    r = client.get("/v1/compare", params={"task_class": "coding.patch"})
    assert r.status_code == 200
    data = r.json()
    assert len(data["compare"]) >= 3
    assert all(v["n"] >= 2 for v in data["compare"].values())


def test_frontier(client, seeded):
    r = client.get("/v1/tasks/coding.patch/frontier", params={"min_success": 0.5})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("OK", "NO_QUALIFYING")
    assert data["candidates"]


def test_frontier_unknown_class(client):
    r = client.get("/v1/tasks/nope/frontier")
    assert r.status_code == 404


def test_run_detail(client, seeded):
    from app.evidence import RUNS_ROOT

    rid = [d.name for d in RUNS_ROOT.iterdir() if d.is_dir() and (d / "run.json").exists()][0]
    r = client.get(f"/v1/runs/{rid}")
    assert r.status_code == 200
    assert r.json()["cost"]["cost_usd"] >= 0