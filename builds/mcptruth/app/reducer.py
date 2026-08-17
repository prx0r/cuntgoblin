"""Window reducer: raw measurements -> derived server_windows -> current state.

Raw probe measurements are NEVER overwritten (spec).  The reducer recomputes
derived windows on demand; stale/unavailable servers fall out of current-state
rankings automatically.

Quantiles are computed by percentile_rank from the actual sample distribution,
so a single outlier measurement cannot destroy the p50/p95.
"""

from __future__ import annotations

import statistics
from datetime import datetime, timedelta, timezone
from typing import Optional

from . import db


def _parse(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def percentile_rank(values: list[float], p: float) -> Optional[float]:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    s = sorted(values)
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def _rate(rows: list[dict], metric: str) -> Optional[float]:
    vals = [r["value_numeric"] for r in rows if r["metric"] == metric
            and r["value_numeric"] is not None]
    if not vals:
        return None
    return round(statistics.fmean(vals), 4)


def _values(rows: list[dict], metric: str) -> list[float]:
    return [r["value_numeric"] for r in rows if r["metric"] == metric
            and r["value_numeric"] is not None]


def reduce_windows(server_id: Optional[str] = None, window_minutes: int = 15) -> dict:
    """Compute server_windows from probe measurements in the last N minutes.

    Windows are keyed (server_id, window_start).  A window aggregates only
    measurements whose probe_run completed within the window bucket; repeated
    reduce() calls recompute the same bucket idempotently from raw data.
    """
    conn = db.get_conn()
    now = datetime.now(timezone.utc)
    # Quantize window_start to the minute so repeated reduces inside the same
    # minute hit the same bucket idempotently (derived projection, not raw).
    bucket = (now - timedelta(minutes=window_minutes)).replace(second=0, microsecond=0)
    window_start = bucket.isoformat(timespec="milliseconds")
    window_end = now.isoformat(timespec="milliseconds")

    if server_id:
        runs = db.get_probe_runs(server_id=server_id, limit=100000)
        server_ids = [server_id]
    else:
        runs = db.get_probe_runs(limit=100000)
        server_ids = [s["server_id"] for s in db.list_servers()]

    # aggregate per server
    per_server: dict[str, list[dict]] = {}
    for r in runs:
        if r["status"] not in ("SUCCESS", "FAILED"):
            continue
        if r["started_at"] < window_start:
            continue
        per_server.setdefault(r["server_id"], []).extend(db.get_measurements(server_id=r["server_id"]))

    counts = {"servers": 0, "windows": 0, "skipped_empty": 0}
    for sid in server_ids:
        # limit measurements to the window
        rows = [m for m in per_server.get(sid, []) if m.get("observed_at", "") >= window_start]
        # also include failure-time measurements from incomplete runs
        completed_runs = {r["probe_run_id"] for r in runs if r["server_id"] == sid
                          and r["started_at"] >= window_start}
        rows = [m for m in rows if m.get("probe_run_id") in completed_runs]
        if not rows:
            counts["skipped_empty"] += 1
            continue

        breaks = conn.execute(
            "SELECT COUNT(*) AS c FROM schema_changes WHERE server_id=? AND detected_at>=? AND change_type='BREAKING'",
            (sid, window_start),
        ).fetchone()["c"]

        tool_counts = [r["value_numeric"] for r in rows if r["metric"] == "tool.count"
                       and r["value_numeric"] is not None]
        window = {
            "server_id": sid,
            "window_start": window_start,
            "window_end": window_end,
            "samples": len(rows),
            "init_success_rate": _rate(rows, "init.success"),
            "tools_list_success_rate": _rate(rows, "tools_list.success"),
            "connection_ms_p50": percentile_rank(_values(rows, "connection.ms"), 50),
            "connection_ms_p95": percentile_rank(_values(rows, "connection.ms"), 95),
            "invocation_ms_p50": percentile_rank(_values(rows, "invocation.ms"), 50),
            "invocation_ms_p95": percentile_rank(_values(rows, "invocation.ms"), 95),
            "invocation_success_rate": _rate(rows, "invocation.success"),
            "tool_count": int(statistics.fmean(tool_counts)) if tool_counts else None,
            "schema_break_count": breaks,
        }
        db.upsert_window(window)
        counts["servers"] += 1
        counts["windows"] += 1
    return counts


def current_state(fresh_seconds: int = 900) -> list[dict]:
    """Latest derivative state per server with freshness metadata.

    A server whose newest window end is older than fresh_seconds is STALE and
    is marked as such in its current-state record (callers must drop it).
    """
    fresh_after = (datetime.now(timezone.utc) - timedelta(seconds=fresh_seconds)).isoformat(
        timespec="milliseconds"
    )
    windows = db.get_latest_windows(fresh_after=fresh_after)
    by_id: dict[str, dict] = {}
    for w in windows:
        srv = db.get_server(w["server_id"])
        if srv is None:
            continue
        age = (datetime.now(timezone.utc) - _parse(w["window_end"])).total_seconds()
        w["freshness_seconds"] = max(0, int(age))
        w["stale"] = age > fresh_seconds
        by_id[w["server_id"]] = {"server": srv, "window": w}
    return [{"server": v["server"], "window": v["window"]} for v in by_id.values()]


def healthiest(limit: int = 20, fresh_seconds: int = 900,
               require_deep: bool = False) -> list[dict]:
    """Current-state ranking.

    Eligibility (never mixed with ranking, spec §Resolution scoring):
      - not RETIRED
      - has a fresh window (not stale)
      - init_success_rate is 1.0 (or null -> no evidence -> ineligible)
      - tools_list_success_rate is 1.0 (or null -> ineligible)
      - connection latency observed

    Ranking: invocation_success_rate desc, connection_ms_p50 asc,
             invocation_ms_p50 asc, schema_break_count asc, name asc.
    """
    states = current_state(fresh_seconds=fresh_seconds)
    eligible = []
    rejected = []
    for st in states:
        srv, w = st["server"], st["window"]
        if srv["status"] == "RETIRED":
            rejected.append({"server_id": srv["server_id"], "reason": "retired"})
            continue
        if w.get("stale"):
            rejected.append({"server_id": srv["server_id"], "reason": "stale"})
            continue
        if require_deep and not srv["deep_test"]:
            rejected.append({"server_id": srv["server_id"], "reason": "not_deep_test"})
            continue
        if w.get("init_success_rate") != 1.0:
            rejected.append({"server_id": srv["server_id"], "reason": "init_not_ok",
                             "rate": w.get("init_success_rate")})
            continue
        if w.get("tools_list_success_rate") != 1.0:
            rejected.append({"server_id": srv["server_id"], "reason": "tools_list_not_ok"})
            continue
        if w.get("connection_ms_p50") is None and w.get("invocation_ms_p50") is None:
            rejected.append({"server_id": srv["server_id"], "reason": "no_latency_evidence"})
            continue
        eligible.append(st)

    eligible.sort(
        key=lambda st: (
            0 if (st["window"].get("invocation_success_rate") or 0) >= 1.0 else 1,
            -(st["window"].get("invocation_success_rate") or 0),
            st["window"].get("connection_ms_p50") if st["window"].get("connection_ms_p50") is not None else 1e12,
            st["window"].get("invocation_ms_p50") if st["window"].get("invocation_ms_p50") is not None else 1e12,
            st["window"].get("schema_break_count") or 0,
            st["server"]["server_id"],
        )
    )
    ranked = []
    for i, st in enumerate(eligible[:limit], start=1):
        ranked.append({**st, "rank": i})
    return ranked