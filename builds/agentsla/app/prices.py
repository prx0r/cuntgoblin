"""app/prices.py — price table for cost accounting.

The AgentSLA provider endpoint (https://opencode.ai/zen/go/v1) returns
`cost: "0"` in chat completions, i.e. it does NOT report real billed amounts.
Cost accounting therefore uses a CONFIGURABLE PER-TOKEN PRICE TABLE.

EPISTEMIC STATUS (read carefully):
  - `basis="provider_reported"` : the provider returned a nonzero cost field.
  - `basis="price_table_estimate"` : amount computed as
        input_tokens/1e6 * input_price + output_tokens/1e6 * output_price
    from PRICE_TABLE below. These are ESTIMATES for accounting/ranking, NOT
    invoices. Every cost number in AgentSLA carries its basis in cost_events.

The table can be overridden with the AGENTSLA_PRICE_TABLE env var pointing at
a JSON file of the same shape (see README). Models missing from the table
account at $0 so a missing row can never fabricate a cost.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# USD per 1M tokens, (input, output). Marked estimates; edit to match your
# actual provider invoice. Keys are the model ids this endpoint serves.
DEFAULT_PRICE_TABLE: dict[str, tuple[float, float]] = {
    "deepseek-v4-flash": (0.14, 0.28),
    "deepseek-v4": (0.56, 1.68),
    "kimi-k2.7-code": (0.60, 2.40),
    "kimi-k3": (0.90, 3.25),
    "glm-5.1": (0.30, 0.84),
    "glm-5.2": (0.90, 2.20),
    "glm-5.3": (1.20, 3.00),
    "minimax-m2.5": (0.30, 1.10),
    "minimax-m2.7": (0.40, 1.60),
    "minimax-m3": (0.60, 2.20),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "claude-sonnet-4": (3.00, 15.00),
    "claude-opus-4": (15.00, 75.00),
    "llama-3.3-70b": (0.25, 0.75),
    "qwen2.5-coder-32b": (0.90, 0.90),
}


def _load_override() -> dict[str, tuple[float, float]]:
    raw = os.environ.get("AGENTSLA_PRICE_TABLE")
    if not raw:
        return dict(DEFAULT_PRICE_TABLE)
    path = Path(raw)
    if not path.exists():
        return dict(DEFAULT_PRICE_TABLE)
    data = json.loads(path.read_text(encoding="utf-8"))
    table: dict[str, tuple[float, float]] = {}
    for model, entry in data.items():
        if isinstance(entry, dict):
            table[model] = (float(entry.get("input", 0.0)), float(entry.get("output", 0.0)))
        elif isinstance(entry, list) and len(entry) == 2:
            table[model] = (float(entry[0]), float(entry[1]))
    return table


def price_for(model_id: str) -> tuple[float, float] | None:
    return _load_override().get(model_id)


def account_cost(
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    provider_reported_usd: float | None = None,
) -> dict:
    """Account one inference call. Returns {amount_usd, basis, unit_price_input,
    unit_price_output}. Provider-reported nonzero amounts win; otherwise use the
    price table; unknown models account at $0 with basis 'price_table_estimate'
    (never a fabricated nonzero number)."""
    if provider_reported_usd and provider_reported_usd > 0:
        return {
            "amount_usd": round(provider_reported_usd, 8),
            "basis": "provider_reported",
            "unit_price_input": None,
            "unit_price_output": None,
        }
    prices = price_for(model_id)
    if prices is None:
        return {
            "amount_usd": 0.0,
            "basis": "price_table_estimate",
            "unit_price_input": 0.0,
            "unit_price_output": 0.0,
        }
    in_price, out_price = prices
    amount = (input_tokens / 1_000_000) * in_price + (output_tokens / 1_000_000) * out_price
    return {
        "amount_usd": round(amount, 8),
        "basis": "price_table_estimate",
        "unit_price_input": in_price,
        "unit_price_output": out_price,
    }