"""Resolution scoring (spec section 'Resolution scoring'):

    hard constraints first
        remove stale
        remove unavailable
        remove unsupported capability
    Pareto rank
    weighted preference

Never mix eligibility with ranking:
    eligible = hard_filter(...)
    ranked = pareto_rank(eligible)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .aggregator import DEFAULT_STALE_SECONDS, current_windows
from .db import DB
from .schema import Endpoint


@dataclass
class RankedEndpoint:
    endpoint: Endpoint
    window: dict
    state: str
    freshness_seconds: Optional[float]
    observations: dict = field(default_factory=dict)
    pareto_front: bool = False
    preference_score: float = 0.0
    excluded_reasons: list[str] = field(default_factory=list)

    def as_dict(self, include_endpoint: bool = True) -> dict:
        d = {
            "endpoint_id": self.endpoint.endpoint_id,
            "model_id": self.endpoint.model_id,
            "provider": self.endpoint.provider_id,
            "observed": self.observations,
            "freshness_seconds": self.freshness_seconds,
            "state": self.state,
            "pareto_front": self.pareto_front,
            "preference_score": round(self.preference_score, 4),
        }
        if self.excluded_reasons:
            d["excluded_reasons"] = self.excluded_reasons
        if include_endpoint:
            d["advertised"] = {
                "context_tokens": self.endpoint.advertised_context_tokens,
                "tools": self.endpoint.tools_advertised,
                "json": self.endpoint.json_advertised,
                "pricing": self.endpoint.pricing,
            }
        return d


def hard_filter(db: DB,
                capability: str = "chat",
                tools: bool = False,
                min_context: Optional[int] = None,
                min_success_rate: float = 0.5,
                min_tool_success: float = 0.5,
                stale_after_seconds: int = DEFAULT_STALE_SECONDS,
                endpoints: Optional[list[Endpoint]] = None,
                now: Optional[str] = None,
                ) -> list[RankedEndpoint]:
    """Eligibility only. Returns (eligible ranked endpoint wrappers)."""
    eps = endpoints if endpoints is not None else db.list_endpoints()
    wins = current_windows(db, stale_after_seconds=stale_after_seconds, now=now)
    out: list[RankedEndpoint] = []
    for ep in eps:
        reasons: list[str] = []
        info = wins.get(ep.endpoint_id)
        if ep.retired_at:
            reasons.append("retired")
        if info is None or info.get("window") is None \
                or (info.get("window") or {}).get("samples", 0) == 0:
            reasons.append("no_observations")
        else:
            w = info["window"]
            if info["state"] == "STALE":
                reasons.append("stale")
            sr = w.get("success_rate")
            if sr is not None and sr < min_success_rate:
                reasons.append(f"success_rate_below_{min_success_rate}")
            # Advertised-only endpoints (catalog rows with no live probe) must
            # never be eligible for resolution: no success_rate, no ttft/tps.
            if (sr is None and w.get("ttft_p50") is None
                    and w.get("tps_p50") is None):
                reasons.append("no_live_observations")
            # capability map for MVP: coding -> needs ttft+throughput data
            if capability == "coding":
                if w.get("ttft_p50") is None:
                    reasons.append("no_ttft_data")
                if w.get("tps_p50") is None:
                    reasons.append("no_throughput_data")
            if tools:
                tsr = w.get("tool_success_rate")
                if tsr is None:
                    # advertised-only is not proof; require observed
                    reasons.append("no_tool_observations")
                elif tsr < min_tool_success:
                    reasons.append(f"tool_success_below_{min_tool_success}")
            if min_context:
                observed_ctx = _tested_context(db, ep)
                advertised = ep.advertised_context_tokens
                if observed_ctx is not None and observed_ctx < min_context:
                    reasons.append(f"tested_context_{observed_ctx}_below_{min_context}")
                elif observed_ctx is None and (advertised or 0) < min_context:
                    reasons.append(f"advertised_context_{advertised or 0}_below_{min_context}")
        if reasons:
            # still represent the exclusion so /v1/resolve can explain
            r = RankedEndpoint(endpoint=ep, window=(info or {}).get("window") or {},
                               state=(info or {}).get("state") or "UNKNOWN",
                               freshness_seconds=(info or {}).get("freshness_seconds"),
                               excluded_reasons=reasons)
            out.append(r)
            continue
        # Candidate is eligible
        w = info["window"]
        r = RankedEndpoint(endpoint=ep, window=w, state=info["state"],
                           freshness_seconds=info["freshness_seconds"],
                           observations={
                               "ttft_ms_p50": w.get("ttft_p50"),
                               "output_tps_p50": w.get("tps_p50"),
                               "success_rate": w.get("success_rate"),
                               "tool_success": w.get("tool_success_rate"),
                               "json_success": w.get("json_success_rate"),
                               "samples": w.get("samples"),
                           })
        out.append(r)
    return out


def _tested_context(db: DB, ep: Endpoint) -> Optional[int]:
    """Largest context bucket that was observed OK. Only rows whose
    value_text='ok' count (context-smoke writes ok/failed on every run)."""
    rows = db.conn.execute(
        """SELECT MAX(value_numeric) FROM probe_measurements
           WHERE subject_id=? AND predicate='endpoint.context_bucket'
             AND value_numeric IS NOT NULL AND value_numeric > 0
             AND value_text='ok'""",
        (ep.endpoint_id,)).fetchone()
    v = rows[0] if rows else None
    return int(v) if v else None


def pareto_rank(candidates: list[RankedEndpoint],
                objectives: Optional[list[str]] = None,
                eps: float = 1e-6) -> list[RankedEndpoint]:
    """Non-dominated front over: max output_tps_p50, min ttft_ms_p50,
    max success_rate, max tool_success (when present), min price (when present).
    NaN values are treated as incomparable (absent objective).
    """
    objs = objectives or ["tps", "ttft", "success", "tool_success", "price"]
    dominated = [False] * len(candidates)
    for i in range(len(candidates)):
        for j in range(len(candidates)):
            if i == j:
                continue
            if _dominates(candidates[j], candidates[i], objs, eps):
                dominated[i] = True
                break
    for i, c in enumerate(candidates):
        c.pareto_front = not dominated[i]
    return candidates


def _dominates(a: RankedEndpoint, b: RankedEndpoint, objs: list[str], eps: float) -> bool:
    """True if a is not worse than b on every compared objective and strictly
    better on at least one (with tolerance eps)."""
    at_least_one_strict = False
    for obj in objs:
        av = _obj_value(a, obj)
        bv = _obj_value(b, obj)
        if av is None or bv is None:
            continue  # incomparable on this objective
        if obj in ("tps", "success", "tool_success"):
            if av < bv - eps:
                return False
            if av > bv + eps:
                at_least_one_strict = True
        else:  # ttft, price -> lower is better
            if av > bv + eps:
                return False
            if av < bv - eps:
                at_least_one_strict = True
    return at_least_one_strict


def _obj_value(c: RankedEndpoint, obj: str) -> Optional[float]:
    w = c.window
    if obj == "tps":
        v = w.get("tps_p50")
        return float(v) if v is not None else None
    if obj == "ttft":
        v = w.get("ttft_p50")
        return float(v) if v is not None else None
    if obj == "success":
        v = w.get("success_rate")
        return float(v) if v is not None else None
    if obj == "tool_success":
        v = w.get("tool_success_rate")
        return float(v) if v is not None else None
    if obj == "price":
        p = c.endpoint.pricing
        v = p.get("prompt_per_1k") if isinstance(p, dict) else None
        return float(v) if v is not None else None
    return None


def weighted_preference(candidates: list[RankedEndpoint],
                        weights: Optional[dict[str, float]] = None,
                        ) -> list[RankedEndpoint]:
    """Weighted Z-score preference among candidates (typically the Pareto
    front). Defaults: throughput 0.30, ttft 0.25, success 0.20,
    tool_success 0.15, price 0.10 (price only when known)."""
    w = weights or {"tps": 0.30, "ttft": 0.25, "success": 0.20,
                    "tool_success": 0.15, "price": 0.10}
    # z-scores per objective over candidates that have the value
    z: dict[str, dict[str, float]] = {}
    for obj in w:
        vals = {}
        for c in candidates:
            v = _obj_value(c, obj)
            if v is not None:
                vals[c.endpoint.endpoint_id] = v
        if not vals:
            continue
        mean = sum(vals.values()) / len(vals)
        std = (sum((v - mean) ** 2 for v in vals.values()) / len(vals)) ** 0.5
        for eid, v in vals.items():
            z.setdefault(eid, {})[obj] = (v - mean) / std if std > 0 else 0.0
    for c in candidates:
        eid = c.endpoint.endpoint_id
        score = 0.0
        for obj, wgt in w.items():
            zv = z.get(eid, {}).get(obj)
            if zv is None:
                continue
            score += wgt * zv * (1 if obj in ("tps", "success", "tool_success") else -1)
        c.preference_score = score
    return sorted(candidates, key=lambda c: c.preference_score, reverse=True)


def resolve(db: DB, capability: str = "chat", tools: bool = False,
            min_context: Optional[int] = None, limit: int = 5,
            min_success_rate: float = 0.5, min_tool_success: float = 0.5,
            stale_after_seconds: int = DEFAULT_STALE_SECONDS,
            now: Optional[str] = None) -> dict:
    """Full resolution pipeline: hard filter -> pareto -> weighted preference.
    Returns a normalized response (MVP user story)."""
    candidates = hard_filter(db, capability=capability, tools=tools,
                             min_context=min_context,
                             min_success_rate=min_success_rate,
                             min_tool_success=min_tool_success,
                             stale_after_seconds=stale_after_seconds, now=now)
    eligible = [c for c in candidates if not c.excluded_reasons]
    pareto_rank(eligible)
    front = [c for c in eligible if c.pareto_front]
    ranked = weighted_preference(front or eligible)
    recommended = None
    if ranked:
        top = ranked[0]
        recommended = {
            "endpoint_id": top.endpoint.endpoint_id,
            "model_id": top.endpoint.model_id,
            "provider": top.endpoint.provider_id,
            "region": top.endpoint.region or None,
            "observed": top.observations,
            "freshness_seconds": top.freshness_seconds,
            "pareto_front": top.pareto_front,
            "preference_score": round(top.preference_score, 4),
            "advertised": {
                "context_tokens": top.endpoint.advertised_context_tokens,
                "tools": top.endpoint.tools_advertised,
                "json": top.endpoint.json_advertised,
                "pricing": top.endpoint.pricing,
            },
        }
    return {
        "request": {"capability": capability, "tools": tools, "min_context": min_context},
        "recommended": recommended,
        "eligible_count": len(eligible),
        "front_count": len(front),
        "total_candidates": len(candidates),
        "alternatives": [c.as_dict() for c in ranked[1:limit]],
        "excluded": [c.as_dict(include_endpoint=False) for c in candidates
                     if c.excluded_reasons][:20],
    }