"""Window aggregator (spec Architecture): raw measurements -> window buckets
with p50/p90/p95 and success rates. Raw measurements are never modified;
endpoint_windows is a derived, recomputable projection.

Percentile: nearest-rank method (robust to outliers; a single outlier TTFT
cannot destroy the p50 — required scenario).
"""

from __future__ import annotations

import math
import statistics
from datetime import datetime, timedelta, timezone
from typing import Optional

from .db import DB
from .schema import parse_ts, utcnow

DEFAULT_WINDOW_SECONDS = 900   # 15 min
DEFAULT_STALE_SECONDS = 3600   # windows older than this are stale


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile. Empty -> nan."""
    if not values:
        return float("nan")
    s = sorted(values)
    n = len(s)
    rank = max(1, math.ceil(p / 100.0 * n))
    return s[min(rank, n) - 1]


def _fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def aggregate_windows(db: DB, window_seconds: int = DEFAULT_WINDOW_SECONDS,
                      now: Optional[str] = None) -> int:
    """Build endpoint_windows rows for every endpoint+window bucket.

    Returns number of window rows upserted.
    """
    now_str = now or utcnow()
    endpoints = db.list_endpoints()

    window_rows = 0
    for ep in endpoints:
        rows = db.conn.execute(
            """SELECT predicate, value_numeric, observed_at FROM probe_measurements
               WHERE subject_id=? AND value_numeric IS NOT NULL
               ORDER BY observed_at""", (ep.endpoint_id,)).fetchall()
        if not rows:
            continue
        buckets: dict[int, dict] = {}
        for r in rows:
            try:
                ts = parse_ts(r["observed_at"])
            except Exception:
                continue
            chunk = int(ts.timestamp() // window_seconds)
            start_dt = datetime.fromtimestamp(chunk * window_seconds, tz=timezone.utc)
            end_dt = start_dt + timedelta(seconds=window_seconds)
            b = buckets.setdefault(chunk, {
                "start": _fmt(start_dt), "end": _fmt(end_dt),
                "metrics": {}, "latest": ts,
            })
            if ts > b["latest"]:
                b["latest"] = ts
            metric = r["predicate"].removeprefix("endpoint.")
            b["metrics"].setdefault(metric, []).append(float(r["value_numeric"]))

        for chunk, b in buckets.items():
            m = b["metrics"]
            window_row = {
                "endpoint_id": ep.endpoint_id,
                "window_start": b["start"],
                "window_end": b["end"],
                "samples": len(db.probe_success_flags(ep.endpoint_id, b["start"], b["end"]))
                          or _bucket_size(m),
                "success_rate": _avg_or_none(_known_flags(db, ep.endpoint_id, "probe.success", b)),
                "reachable_rate": _avg_or_none(_known_flags(db, ep.endpoint_id, "endpoint.reachable", b)),
                "ttft_p50": _p(m.get("ttft_ms", []), 50, db, ep.endpoint_id, "ttft_ms", b),
                "ttft_p90": _p(m.get("ttft_ms", []), 90, db, ep.endpoint_id, "ttft_ms", b),
                "ttft_p95": _p(m.get("ttft_ms", []), 95, db, ep.endpoint_id, "ttft_ms", b),
                "tps_p50": _p(m.get("output_tps", []), 50, db, ep.endpoint_id, "output_tps", b),
                "tps_p90": _p(m.get("output_tps", []), 90, db, ep.endpoint_id, "output_tps", b),
                "tps_p95": _p(m.get("output_tps", []), 95, db, ep.endpoint_id, "output_tps", b),
                "tool_success_rate": _avg_or_none(_known_flags(db, ep.endpoint_id, "endpoint.tool_success", b)),
                "json_success_rate": _avg_or_none(_known_flags(db, ep.endpoint_id, "endpoint.json_success", b)),
                "latest_observed_at": _fmt(b["latest"]),
            }
            db.upsert_window(window_row)
            window_rows += 1
    return window_rows


def _p(vals: list[float], p: float, db, ep, metric, bucket) -> Optional[float]:
    v = percentile(vals, p)
    if math.isnan(v):
        # fall back to raw lookup-by-metric for this bucket
        rows = db.metric_flag_values(ep, metric, bucket["start"], bucket["end"])
        if not rows:
            return None
        v = percentile(rows, p)
    return round(v, 3) if not math.isnan(v) else None


def _avg_or_none(vals: list[float]) -> Optional[float]:
    if not vals:
        return None
    return round(statistics.fmean(vals), 4)


def _known_flags(db, ep: str, predicate: str, bucket: dict) -> list[float]:
    return db.flag_values_for_predicate(ep, predicate, bucket["start"], bucket["end"])


def _bucket_size(m: dict) -> int:
    return max((len(v) for v in m.values()), default=0)


def current_windows(db: DB, stale_after_seconds: int = DEFAULT_STALE_SECONDS,
                    now: Optional[str] = None) -> dict[str, dict]:
    """Project CURRENT STATE per endpoint: freshest window if within TTL,
    else a STALE marker.

    Merge semantics: metrics are taken newest-first across all window rows
    whose window_end is within the staleness horizon. A live endpoint that
    was probed at 20:39 (ttft/tps bucket 20:30-20:45) and again at 20:47
    (context bucket 20:45-21:00) must report BOTH — the per-metric freshest
    value — otherwise a split bucket wrongly looks like 'no ttft data'."""
    now_str = now or utcnow()
    now_dt = parse_ts(now_str)
    out: dict[str, dict] = {}
    merge_cols = ["samples", "success_rate", "reachable_rate", "ttft_p50", "ttft_p90",
                  "ttft_p95", "tps_p50", "tps_p90", "tps_p95", "tool_success_rate",
                  "json_success_rate"]
    for ep in db.list_endpoints():
        wins = db.windows_for_endpoint(ep.endpoint_id, limit=10)
        if not wins:
            out[ep.endpoint_id] = {"state": "UNKNOWN", "freshness_seconds": None}
            continue
        fresh = []
        for w in wins:
            try:
                end_dt = parse_ts(w["window_end"])
            except Exception:
                continue
            age = (now_dt - end_dt).total_seconds()
            if age <= stale_after_seconds:
                fresh.append((w, age))
        if not fresh:
            newest = wins[0]
            end_dt = parse_ts(newest["window_end"])
            out[ep.endpoint_id] = {
                "state": "STALE",
                "freshness_seconds": round(max((now_dt - end_dt).total_seconds(), 0.0), 1),
                "window": dict(newest),
            }
            continue
        fresh.sort(key=lambda pair: pair[0]["window_end"], reverse=True)
        primary, primary_age = fresh[0]
        merged = dict(primary)
        latest_ts = primary["latest_observed_at"]
        for col in merge_cols:
            for w, _age in fresh:
                if w[col] is not None:
                    merged[col] = w[col]
                    break
        for w, _age in fresh:
            if w["latest_observed_at"] and w["latest_observed_at"] > latest_ts:
                latest_ts = w["latest_observed_at"]
        merged["latest_observed_at"] = latest_ts
        merged["window_start"] = min(w["window_start"] for w, _ in fresh)
        out[ep.endpoint_id] = {
            "state": "KNOWN",
            "freshness_seconds": round(max(primary_age, 0.0), 1),
            "window": merged,
        }
    return out