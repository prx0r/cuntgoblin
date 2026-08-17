"""Shared fixtures: ephemeral DB + real probe of the local mock MCP server."""

from __future__ import annotations

import json
import os
import sys

import pytest

# 1) Point the DB at an ephemeral file BEFORE app.imports read DB_PATH.
_TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
_BUILD_ROOT = os.path.dirname(_TEST_ROOT)
_DB = os.path.join(_TEST_ROOT, "test_mcptruth.db")
os.environ["MCPTRUTH_DB"] = _DB
if _BUILD_ROOT not in sys.path:
    sys.path.insert(0, _BUILD_ROOT)

from app import db, oracle  # noqa: E402
from app.discovery import seed_registry  # noqa: E402
from app.harness import run_probe_cycle  # noqa: E402

MOCK_SERVER_ID = "mock:mock-mcp"


def reset_db() -> None:
    db.close_conn()
    for suffix in ("", "-wal", "-shm"):
        p = _DB + suffix
        if os.path.exists(p):
            os.remove(p)
    db.DB_PATH = _DB
    db.init_db()


@pytest.fixture(scope="session", autouse=True)
def seeded_db():
    reset_db()
    seed_registry(force=True)
    yield
    db.close_conn()


@pytest.fixture(scope="session")
def mock_server() -> dict:
    s = db.get_server(MOCK_SERVER_ID)
    assert s is not None, "seed must register mock:mock-mcp"
    return s


@pytest.fixture(scope="session", autouse=True)
def mock_probe_summary(seeded_db, mock_server):
    """Probe the real local mock server once; shared across tests.

    autouse so every test (API, reducer, integrity) sees a real probed DB.
    Also refreshes derived windows so /v1/healthiest has real input.
    """
    summary = run_probe_cycle(mock_server)
    assert summary["status"] == "SUCCESS", f"mock probe must succeed: {summary}"
    from app import reducer
    reducer.reduce_windows()
    return summary


def agents_db_path() -> str:
    return os.path.join(_BUILD_ROOT, "data", "runs", "agent-steps.jsonl")