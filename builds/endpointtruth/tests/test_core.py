"""Unit tests: aggregator percentiles/windows, resolve pipeline, DB
invariants, envelope shape, discovery parity for the universal envelope.
"""

from __future__ import annotations

import datetime as dt

import json

from endpointtruth.aggregator import aggregate_windows, current_windows, percentile
from endpointtruth.db import DB
from endpointtruth.resolve import hard_filter, pareto_rank, resolve, weighted_preference
from endpointtruth.schema import Endpoint, Observation, State, utcnow
from endpointtruth.state import current_state_map
from tests.test_required_scenarios import _inject, ep


def _db_with_eps(db: DB, make_obs=True):
    a = ep(endpoint_id="prov:fast", model="fast", context=131072)
    b = ep(endpoint_id="prov:slow", model="slow", context=32768)
    c = ep(endpoint_id="prov:dead", model="dead", context=8192)
    c.retired_at = utcnow()
    d = ep(endpoint_id="prov:missing-ctx", model="missing-ctx", context=None)
    for e in (a, b, c, d):
        db.upsert_endpoint(e)
    if make_obs:
        _inject(db, a, [("ttft_ms", 100.0, "ms", State.KNOWN.value),
                        ("ttft_ms", 105.0, "ms", State.KNOWN.value),
                        ("ttft_ms", 98.0, "ms", State.KNOWN.value),
                        ("output_tps", 90.0, "tokens_per_second", State.KNOWN.value),
                        ("output_tps", 95.0, "tokens_per_second", State.KNOWN.value),
                        ("tool_success", 1.0, "flag", State.KNOWN.value),
                        ("probe.success", 1.0, "flag", State.KNOWN.value),
                        ("probe.success", 1.0, "flag", State.KNOWN.value),
                        ("json_success", 1.0, "flag", State.KNOWN.value),
                        ("context_bucket", 8192.0, "tokens", State.KNOWN.value)],
                value_texts={"context_bucket": "ok"})
        _inject(db, b, [("ttft_ms", 400.0, "ms", State.KNOWN.value),
                        ("output_tps", 30.0, "tokens_per_second", State.KNOWN.value),
                        ("tool_success", 0.0, "flag", State.KNOWN.value),
                        ("probe.success", 1.0, "flag", State.KNOWN.value),
                        ("json_success", 1.0, "flag", State.KNOWN.value)])
        _inject(db, d, [("ttft_ms", 120.0, "ms", State.KNOWN.value),
                        ("output_tps", 70.0, "tokens_per_second", State.KNOWN.value),
                        ("probe.success", 1.0, "flag", State.KNOWN.value)])
    return a, b, c, d


def test_percentile_nearest_rank():
    assert percentile([1, 2, 3, 4], 50) == 2
    assert percentile([1, 2, 3, 4, 5], 50) == 3
    assert percentile([], 50) != 50  # nan


def test_windows_aggregation():
    db = DB(":memory:")
    _db_with_eps(db)
    n = aggregate_windows(db, window_seconds=3600)
    assert n >= 3  # fast, slow, missing-ctx have observations; dead retired
    w = db.latest_windows()
    assert w["prov:fast"]["ttft_p50"] == 100.0
    assert w["prov:fast"]["tool_success_rate"] == 1.0
    assert w["prov:slow"]["ttft_p50"] == 400.0
    # context_bucket max observed -> tested context
    from endpointtruth.resolve import _tested_context
    assert _tested_context(db, db.get_endpoint("prov:fast")) == 8192


def test_current_state_map():
    db = DB(":memory:")
    _db_with_eps(db)
    aggregate_windows(db, window_seconds=3600)
    st = current_state_map(db)
    assert st["prov:fast"]["state"] == "KNOWN"
    # nearest-rank p50 of [90, 95]: rank=ceil(0.5*2)=1 -> 90.0
    assert st["prov:fast"]["observed"]["output_tps_p50"] == 90.0


def test_resolve_pipeline_order():
    db = DB(":memory:")
    _db_with_eps(db)
    aggregate_windows(db, window_seconds=3600)
    out = resolve(db, capability="coding", tools=True, min_context=8000, limit=3)
    assert out["recommended"]["endpoint_id"] == "prov:fast"
    # retired endpoint must never appear anywhere
    blob = json.dumps(out)
    assert "prov:dead" not in blob
    # tools=true must exclude prov:slow (tool_success 0)
    excluded = [c for c in out["excluded"]]
    assert any(c["endpoint_id"] == "prov:slow" and
               any("tool_success_below_0.5" in r for r in c["excluded_reasons"])
               for c in excluded)


def test_pareto_front_shape():
    db = DB(":memory:")
    _db_with_eps(db)
    aggregate_windows(db, window_seconds=3600)
    cands = hard_filter(db, capability="coding", tools=False, min_context=8000)
    eligible = [x for x in cands if not x.excluded_reasons]
    pareto_rank(eligible)
    front = [x for x in eligible if x.pareto_front]
    # fast dominates slow, so slow is not on the front
    ids = {x.endpoint.endpoint_id for x in front}
    assert "prov:fast" in ids
    assert "prov:slow" not in ids


def test_weighted_preference_ranks_fast_first():
    db = DB(":memory:")
    _db_with_eps(db)
    aggregate_windows(db, window_seconds=3600)
    cands = hard_filter(db, capability="coding", tools=False, min_context=8000)
    eligible = [x for x in cands if not x.excluded_reasons]
    pareto_rank(eligible)
    ranked = weighted_preference([x for x in eligible if x.pareto_front])
    assert ranked[0].endpoint.endpoint_id == "prov:fast"


def test_db_raw_invariant():
    db = DB(":memory:")
    a = ep(endpoint_id="prov:fast", model="fast")
    db.upsert_endpoint(a)
    _inject(db, a, [("ttft_ms", 100.0, "ms", State.KNOWN.value)])
    n1 = db.count_observations()
    # re-running aggregation must not change raw observation count
    aggregate_windows(db, window_seconds=3600)
    n2 = db.count_observations()
    assert n1 == n2
    # windows are derived: recompute and compare
    w1 = db.latest_windows()["prov:fast"]["ttft_p50"]
    aggregate_windows(db, window_seconds=3600)
    w2 = db.latest_windows()["prov:fast"]["ttft_p50"]
    assert w1 == w2


def test_envelope_shape():
    obs = Observation(subject_id="prov:fast", predicate="endpoint.throughput",
                      value_number=67.4, unit="tokens_per_second",
                      state=State.KNOWN.value, method_id="throughput-probe-v1",
                      method_version="1.0.0", artifact_sha256="abc",
                      evidence_selector="$.metrics.output_tps")
    env = obs.envelope()
    assert env["subject"] == {"type": "endpoint", "id": "prov:fast"}
    assert env["value"] == {"number": 67.4, "unit": "tokens_per_second"}
    assert env["evidence"] == [{"artifact_sha256": "abc", "selector": "$.metrics.output_tps"}]
    assert set(env.keys()) == {"subject", "predicate", "value", "state", "observed_at",
                               "valid_until", "source", "method", "confidence", "evidence"}


def test_hard_filter_never_mixes_eligibility():
    db = DB(":memory:")
    _db_with_eps(db)
    aggregate_windows(db, window_seconds=3600)
    cands = hard_filter(db, capability="coding", tools=False, min_context=8000)
    eligible = [c for c in cands if not c.excluded_reasons]
    excluded = [c for c in cands if c.excluded_reasons]
    # eligibility and exclusion are mutually exclusive: no id appears in both
    eids = {c.endpoint.endpoint_id for c in eligible}
    xids = {c.endpoint.endpoint_id for c in excluded}
    assert eids.isdisjoint(xids)
    assert len(eids) + len(xids) == len(cands)