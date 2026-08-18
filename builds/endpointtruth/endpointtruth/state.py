"""CURRENT STATE projection: emit the universal evidence envelope for the
currently-known value of a metric, from freshest windows (spec: OBSERVATIONS
-> MEASUREMENTS -> WINDOW AGGREGATOR -> CURRENT STATE).
"""

from __future__ import annotations

from typing import Optional

from .aggregator import DEFAULT_STALE_SECONDS, current_windows
from .db import DB
from .schema import State, utcnow


def current_observation(db: DB, endpoint_id: str, predicate: str,
                        window: Optional[dict] = None,
                        stale_after_seconds: int = DEFAULT_STALE_SECONDS,
                        now: Optional[str] = None) -> dict:
    """Envelope-style current value for one metric of one endpoint."""
    now_str = now or utcnow()
    wins = current_windows(db, stale_after_seconds=stale_after_seconds, now=now_str)
    info = wins.get(endpoint_id)
    if info is None:
        return {"subject": {"type": "endpoint", "id": endpoint_id},
                "predicate": predicate, "value": {}, "state": State.UNKNOWN.value,
                "observed_at": None, "confidence": 0.0, "evidence": []}
    w = info.get("window") or {}
    metric = predicate.removeprefix("endpoint.")
    col = {
        "ttft_ms": "ttft_p50", "output_tps": "tps_p50",
    }.get(metric, "")
    value = w.get(col) if col else None
    state = info["state"]
    return {
        "subject": {"type": "endpoint", "id": endpoint_id},
        "predicate": predicate,
        "value": {"number": value} if value is not None else {},
        "state": state,
        "observed_at": w.get("latest_observed_at"),
        "freshness_seconds": info.get("freshness_seconds"),
        "confidence": 0.95 if state == "KNOWN" else (0.5 if state == "STALE" else 0.0),
        "evidence": [{"window_start": w.get("window_start"), "window_end": w.get("window_end"),
                      "samples": w.get("samples")}] if w else [],
    }


def current_state_map(db: DB, stale_after_seconds: int = DEFAULT_STALE_SECONDS,
                      now: Optional[str] = None) -> dict[str, dict]:
    """Full CURRENT STATE for the API: per endpoint, per key metric."""
    wins = current_windows(db, stale_after_seconds=stale_after_seconds, now=now)
    out: dict[str, dict] = {}
    for eid, info in wins.items():
        out[eid] = {
            "state": info["state"],
            "freshness_seconds": info["freshness_seconds"],
            "observed": {
                "ttft_ms_p50": info["window"].get("ttft_p50") if info.get("window") else None,
                "output_tps_p50": info["window"].get("tps_p50") if info.get("window") else None,
                "success_rate": info["window"].get("success_rate") if info.get("window") else None,
                "tool_success_rate": info["window"].get("tool_success_rate") if info.get("window") else None,
                "json_success_rate": info["window"].get("json_success_rate") if info.get("window") else None,
                "reachable_rate": info["window"].get("reachable_rate") if info.get("window") else None,
                "samples": info["window"].get("samples") if info.get("window") else None,
            },
        }
    return out