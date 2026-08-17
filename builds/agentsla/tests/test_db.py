"""DB schema + round-trip tests."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import SCHEMA_SQL, connect, table_names  # noqa: E402

REQUIRED = {"tasks", "task_versions", "architectures", "architecture_versions",
            "runs", "run_components", "model_calls", "tool_calls",
            "evaluations", "cost_events"}


def test_schema_creates_all_ten_tables(db_path):
    conn = connect(db_path)
    tables = set(table_names(conn))
    assert REQUIRED <= tables, f"missing: {REQUIRED - tables}"


def test_schema_idempotent(db_path):
    conn1 = connect(db_path)
    conn2 = connect(db_path)
    assert set(table_names(conn2)) == set(table_names(conn1))


def test_raw_rows_append_only(db_path):
    """model_calls/cost_events/tool_calls have no UPDATE path in the codebase;
    verify the schema supports append-only by inserting two calls with distinct ids."""
    conn = connect(db_path)
    conn.execute(
        """INSERT INTO runs (run_id, benchmark_id, architecture_version_id, task_version_id, attempt,
           status) VALUES ('r1','b','av','tv',1,'success')"""
    )
    conn.commit()
    from app.cost import record_inference_cost

    row1 = record_inference_cost(conn, run_id="r1", model_call_id="mc1", model_id="deepseek-v4-flash",
                                 input_tokens=100, output_tokens=50, provider_cost=None)
    row2 = record_inference_cost(conn, run_id="r1", model_call_id="mc2", model_id="deepseek-v4-flash",
                                 input_tokens=200, output_tokens=100, provider_cost=None)
    assert row1["cost_event_id"] != row2["cost_event_id"]
    total = conn.execute("SELECT COALESCE(SUM(amount_usd),0) FROM cost_events WHERE run_id='r1'").fetchone()[0]
    assert total == row1["amount_usd"] + row2["amount_usd"]