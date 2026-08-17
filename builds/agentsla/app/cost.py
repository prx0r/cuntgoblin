"""app/cost.py — cost accounting glue (spec: RUNNER -> COST ACCOUNTING).

Wraps prices.account_cost and writes cost_events rows + totals per run.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from .prices import account_cost


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_inference_cost(
    conn: sqlite3.Connection,
    *,
    run_id: str,
    model_call_id: str,
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    provider_cost: float | None,
) -> dict:
    """Write one cost_events row for a completed model call. Returns the row."""
    acct = account_cost(model_id, input_tokens, output_tokens, provider_cost)
    event_id = f"ce_{uuid.uuid4().hex[:12]}"
    row = {
        "cost_event_id": event_id,
        "run_id": run_id,
        "model_call_id": model_call_id,
        "kind": "inference",
        "basis": acct["basis"],
        "model_id": model_id,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "unit_price_input": acct["unit_price_input"],
        "unit_price_output": acct["unit_price_output"],
        "amount_usd": acct["amount_usd"],
        "recorded_at": _now(),
    }
    conn.execute(
        """INSERT INTO cost_events
           (cost_event_id, run_id, model_call_id, kind, basis, model_id,
            input_tokens, output_tokens, unit_price_input, unit_price_output,
            amount_usd, recorded_at)
           VALUES (:cost_event_id, :run_id, :model_call_id, :kind, :basis, :model_id,
                   :input_tokens, :output_tokens, :unit_price_input, :unit_price_output,
                   :amount_usd, :recorded_at)""",
        row,
    )
    conn.commit()
    return row


def run_totals(conn: sqlite3.Connection, run_id: str) -> dict:
    """Aggregate cost/tokens for one run from raw rows (never overwrites them)."""
    row = conn.execute(
        """SELECT
             COALESCE(SUM(c.amount_usd), 0.0) AS cost_usd,
             SUM(CASE WHEN c.basis='provider_reported' THEN 1 ELSE 0 END) AS provider_based,
             SUM(CASE WHEN c.basis='price_table_estimate' THEN 1 ELSE 0 END) AS table_based,
             COALESCE(SUM(m.prompt_tokens), 0) AS input_tokens,
             COALESCE(SUM(m.completion_tokens), 0) AS output_tokens
           FROM cost_events c LEFT JOIN model_calls m ON m.model_call_id = c.model_call_id
           WHERE c.run_id = ?""",
        (run_id,),
    ).fetchone()
    return {
        "cost_usd": round(float(row["cost_usd"] or 0.0), 6),
        "provider_based_events": int(row["provider_based"] or 0),
        "table_based_events": int(row["table_based"] or 0),
        "input_tokens": int(row["input_tokens"] or 0),
        "output_tokens": int(row["output_tokens"] or 0),
    }