"""Cost accounting tests: basis selection, never-fabricated zero, math."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.prices import account_cost, price_for


def test_price_for_known_model():
    p = price_for("deepseek-v4-flash")
    assert p is not None and p[0] > 0
    in_p, out_p = p


def test_price_for_unknown_model_is_none():
    assert price_for("definitely-not-a-model") is None


def test_account_cost_uses_table():
    acct = account_cost("deepseek-v4-flash", 1_000_000, 500_000)
    assert acct["basis"] == "price_table_estimate"
    in_p, out_p = price_for("deepseek-v4-flash")
    expected = in_p + out_p / 2
    assert abs(acct["amount_usd"] - expected) < 1e-6


def test_account_cost_zero_for_unknown():
    acct = account_cost("unknown-model", 10_000, 5_000)
    assert acct["amount_usd"] == 0.0  # never fabricate a cost


def test_provider_reported_wins():
    acct = account_cost("deepseek-v4-flash", 1_000_000, 500_000, provider_reported_usd=0.123)
    assert acct["basis"] == "provider_reported"
    assert abs(acct["amount_usd"] - 0.123) < 1e-9


def test_provider_zero_falls_back_to_table():
    acct = account_cost("deepseek-v4-flash", 1_000_000, 0, provider_reported_usd=0.0)
    assert acct["basis"] == "price_table_estimate"
    assert acct["amount_usd"] > 0