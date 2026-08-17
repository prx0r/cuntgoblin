"""Reducer + current-state tests: windows, percentile robustness, staleness,
and eligibility/ranking separation (spec §Resolution scoring)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app import db, reducer


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="milliseconds")


def _insert_raw(server_id: str, metric: str, value: float, unit: str = "",
                observed_at: str | None = None, run_id: str | None = None) -> None:
    """Insert raw measurement + run rows exactly as a probe would."""
    if run_id is None:
        run_id = f"run_{server_id.replace(':','_')}_{metric}_{value}"
        db.get_conn().execute(
            """INSERT OR IGNORE INTO probe_runs
               (probe_run_id, server_id, probe_type, started_at, probe_region,
                method_version, status)
               VALUES (?,?,?,?,?,?,?)""",
            (run_id, server_id, "full", observed_at or _iso(datetime.now(timezone.utc)),
             "local", "test-v1", "SUCCESS"),
        )
    db.record_measurement(run_id, metric, value, None, unit, db.STATE_KNOWN,
                          observed_at=observed_at or _iso(datetime.now(timezone.utc)))


def _window_result(server_id: str) -> dict:
    rows = db.get_windows_for_server(server_id, limit=1)
    assert rows, f"no window for {server_id}"
    return rows[0]


def test_outlier_does_not_destroy_p50():
    """One 60-second outlier among 1s latencies must not destroy p50.
    (p95 SHOULD reflect the tail — that is why it is p95, not median.)"""
    now = datetime.now(timezone.utc)
    for i in range(9):
        _insert_raw("p:srv-outlier", "connection.ms", 1.0, "ms",
                    _iso(now - timedelta(minutes=i)))
    _insert_raw("p:srv-outlier", "connection.ms", 60000.0, "ms", _iso(now))
    _insert_raw("p:srv-outlier", "init.success", 1.0, "", _iso(now))
    _insert_raw("p:srv-outlier", "tools_list.success", 1.0, "", _iso(now))

    reducer.reduce_windows(server_id="p:srv-outlier", window_minutes=30)
    w = _window_result("p:srv-outlier")
    assert w["connection_ms_p50"] == 1.0, f"p50 destroyed by outlier: {w['connection_ms_p50']}"
    assert w["connection_ms_p95"] > w["connection_ms_p50"], "p95 must track the tail"
    assert w["connection_ms_p95"] < 60000.0, "p95 must still be a percentile, not the max"
    assert w["samples"] >= 11


def test_stale_server_excluded_from_healthiest():
    from app.discovery import seed_registry
    seed_registry(force=True)
    fresh_id = "p:srv-fresh"
    stale_id = "p:srv-stale"
    now = datetime.now(timezone.utc)
    for sid in (fresh_id, stale_id):
        if db.get_server(sid) is None:
            db.upsert_server(sid, sid, "stdio", description="", deep_test=1)
    # fresh server: observations in the window
    _insert_raw(fresh_id, "init.success", 1.0, "", _iso(now))
    _insert_raw(fresh_id, "tools_list.success", 1.0, "", _iso(now))
    _insert_raw(fresh_id, "connection.ms", 42.0, "ms", _iso(now))
    # stale server: ONLY observations from 3 hours ago -> no fresh window
    old = _iso(now - timedelta(hours=3))
    _insert_raw(stale_id, "init.success", 1.0, "", old)
    _insert_raw(stale_id, "tools_list.success", 1.0, "", old)
    _insert_raw(stale_id, "connection.ms", 42.0, "ms", old)

    reducer.reduce_windows(server_id=fresh_id, window_minutes=5)
    reducer.reduce_windows(server_id=stale_id, window_minutes=5)  # old rows -> empty bucket
    ranked = reducer.healthiest(fresh_seconds=900, require_deep=False)
    ids = [h["server"]["server_id"] for h in ranked]
    assert fresh_id in ids
    assert stale_id not in ids, "stale benchmark must be removed from current ranking"


def test_init_failure_excluded_but_ranked_separated():
    """Eligibility first, ranking second: a server with init failure is not
    eligible regardless of how fast it might be."""
    ok_id = "p:srv-ok"
    fail_id = "p:srv-fail"
    now = datetime.now(timezone.utc)
    for sid in (ok_id, fail_id):
        if db.get_server(sid) is None:
            db.upsert_server(sid, sid, "stdio", description="", deep_test=1)
    _insert_raw(ok_id, "init.success", 1.0, "", _iso(now))
    _insert_raw(ok_id, "tools_list.success", 1.0, "", _iso(now))
    _insert_raw(ok_id, "connection.ms", 10.0, "ms", _iso(now))
    _insert_raw(fail_id, "init.success", 0.0, "", _iso(now))
    _insert_raw(fail_id, "connection.ms", 1.0, "ms", _iso(now))  # fast but broken
    reducer.reduce_windows(server_id=ok_id, window_minutes=5)
    reducer.reduce_windows(server_id=fail_id, window_minutes=5)
    ranked = reducer.healthiest(fresh_seconds=900, require_deep=False)
    ids = [h["server"]["server_id"] for h in ranked]
    assert ok_id in ids
    assert fail_id not in ids


def test_percentile_rank_math():
    vals = [1.0, 2.0, 3.0, 4.0]
    assert reducer.percentile_rank(vals, 50) == 2.5
    assert reducer.percentile_rank(vals, 0) == 1.0
    assert reducer.percentile_rank(vals, 100) == 4.0
    assert reducer.percentile_rank([], 50) is None
    assert reducer.percentile_rank([7.0], 50) == 7.0


def test_reduce_idempotent():
    """Recomputing the same window must not duplicate measurements or create
    multiple buckets for the same wall-clock window."""
    srv = "p:srv-idem"
    now = datetime.now(timezone.utc)
    if db.get_server(srv) is None:
        db.upsert_server(srv, srv, "stdio", description="", deep_test=1)
    _insert_raw(srv, "connection.ms", 5.0, "ms", _iso(now))
    _insert_raw(srv, "init.success", 1.0, "", _iso(now))
    reducer.reduce_windows(server_id=srv, window_minutes=5)
    window_key = db.get_windows_for_server(srv)[0]["window_start"]
    measurements_before = db.stats()["measurements"]
    reducer.reduce_windows(server_id=srv, window_minutes=5)
    windows = db.get_windows_for_server(srv)
    same_bucket = [w for w in windows if w["window_start"] == window_key]
    assert len(same_bucket) == 1, "same window bucket must not be duplicated"
    assert db.stats()["measurements"] == measurements_before, "reduce must not write measurements"