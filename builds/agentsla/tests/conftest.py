"""Pytest fixtures: isolated DB + run-envelope dirs per test session.

CRITICAL: env vars are set at CONFTEST IMPORT TIME (module level), not in a
fixture, because test modules import `app.*` during collection and those
modules read AGENTSLA_DB / AGENTSLA_RUNS_DIR at import time.
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

_TMP = tempfile.mkdtemp(prefix="agentsla_tests_")
os.environ["AGENTSLA_RUNS_DIR"] = str(Path(_TMP) / "runs")
os.environ["AGENTSLA_DB"] = str(Path(_TMP) / "db" / "agentsla.db")


@pytest.fixture(scope="session")
def db_path() -> str:
    return os.environ["AGENTSLA_DB"]