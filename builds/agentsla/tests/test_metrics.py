"""Metrics + knee tests: the 'never claim 90% from 9/10' guarantee."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.metrics import (  # noqa: E402
    RunRow,
    knee_from_runs,
    sla_summary,
    wilson_interval,
    wilson_lower_bound,
)


def row(success=True, cost=0.1, dur=30.0, inp=1000, out=500, tools=3, retries=0):
    return RunRow(success=success, cost_usd=cost, duration_seconds=dur,
                  input_tokens=inp, output_tokens=out, tool_calls=tools, retries=retries)


def test_wilson_known_values():
    # Exact Wilson 95% lower bound for 1 success in 1 trial is ~0.2065
    lb = wilson_lower_bound(1, 1)
    assert abs(lb - 0.2065) < 0.001
    # 9/10 -> lower bound ~0.596, never 0.90
    lb90 = wilson_lower_bound(9, 10)
    assert abs(lb90 - 0.5958) < 0.001
    # 0 samples -> 0
    assert wilson_lower_bound(0, 0) == 0.0


def test_wilson_interval_symmetric_edges():
    lo, hi = wilson_interval(0, 10)
    assert 0.0 <= lo <= hi <= 1.0
    lo2, hi2 = wilson_interval(10, 10)
    assert lo2 < 1.0 and hi2 == pytest.approx(1.0, abs=1e-2)  # float noise vs exact 1.0


def test_sla_summary_empty():
    s = sla_summary([])
    assert s.insufficient_evidence is True
    assert s.n == 0


def test_sla_summary_math():
    runs = [row(success=True, cost=0.1, dur=30, tools=3, retries=1),
            row(success=False, cost=0.1, dur=50, tools=5, retries=0),
            row(success=True, cost=0.1, dur=40, tools=4, retries=0)]
    s = sla_summary(runs)
    assert s.n == 3
    assert s.successes == 2
    assert abs(s.success_rate - 2 / 3) < 1e-12
    assert abs(s.cost_per_attempt - 0.1) < 1e-12
    assert abs(s.cost_per_success - 0.15) < 1e-12
    assert abs(s.duration_per_success - 35.0) < 1e-12
    assert abs(s.tokens_per_success - 1500) < 1e-12  # (1000+500)*2/2 = 1500
    assert abs(s.tool_calls_per_success - 3.5) < 1e-12
    assert abs(s.retry_rate - 1 / 3) < 1e-12
    assert s.efficiency > 0
    # min_samples default is 3; n=3 meets it -> evidence considered sufficient
    assert s.insufficient_evidence is False


def test_sla_summary_min_samples():
    s = sla_summary([row(), row()], min_samples=10)
    assert s.insufficient_evidence is True


def test_knee_ok_with_enough_evidence():
    # 20/20 successes -> Wilson LB ~0.839; both clear the 0.8 bar
    grouped = [
        ("cheap", sla_summary([row(True, 0.25)] * 20)),          # wilson lb ~0.839
        ("expensive", sla_summary([row(True, 0.50)] * 20)),
    ]
    res = knee_from_runs(grouped, min_success=0.8)
    assert res["status"] == "OK"
    assert res["recommended"]["architecture_id"] == "cheap"


def test_knee_no_qualifying():
    grouped = [
        ("good", sla_summary([row(True, 0.25)] * 5)),   # lb 5/5 ~0.478 < 0.9
    ]
    res = knee_from_runs(grouped, min_success=0.9)
    assert res["status"] == "NO_QUALIFYING"


def test_knee_insufficient_evidence():
    grouped = [
        ("tiny", sla_summary([row(True, 0.25)] * 1)),  # below min_samples
    ]
    res = knee_from_runs(grouped, min_success=0.2, min_samples=3)
    assert res["status"] == "NO_QUALIFYING"
    # the n=1 candidate is not eligible for recommendation
    assert "recommended" not in res


def test_knee_quality_cliff_reported():
    # cheapest DOES qualify; next-cheaper exists but does NOT qualify -> cliff
    grouped = [
        ("cheap", sla_summary([row(True, 0.02)] * 20)),    # lb ~0.839 qualifies
        ("mid", sla_summary([row(False, 0.01)] * 20)),     # 0/20 -> does not qualify
    ]
    res = knee_from_runs(grouped, min_success=0.8)
    assert res["status"] == "OK"
    assert res["recommended"]["architecture_id"] == "cheap"
    assert res["quality_cliff"]["next_cheaper"]["architecture_id"] == "mid"
    assert res["quality_cliff"]["success_drop"] > 0.5