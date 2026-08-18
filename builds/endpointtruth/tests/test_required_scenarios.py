"""Tests for the required scenarios in specs/endpointtruth/architecture.md:

    1. provider says model exists but inference 404s
    2. HTTP 200 but malformed stream
    3. tool capability advertised but fails
    4. endpoint switches model alias
    5. one outlier TTFT doesn't destroy p50
    6. stale benchmark removed from current ranking
    7. provider outage
    8. rate limit response distinguished from outage
"""

from __future__ import annotations

import asyncio

import httpx
import pytest

from endpointtruth.aggregator import DEFAULT_STALE_SECONDS, aggregate_windows, percentile
from endpointtruth.db import DB
from endpointtruth.probes import (ContextSmokeProbe, JSONModeProbe, ReachabilityProbe,
                                  TTFTProbe, ThroughputProbe, ToolsProbe,
                                  load_credentials)
from endpointtruth.resolve import hard_filter, resolve
from endpointtruth.schema import Endpoint, State, utcnow

CHAT_URL = "https://fake/v1/chat/completions"


def ep(endpoint_id="test:model-x", provider="test", model="model-x",
       tools=True, json_ok=True, context=None, base_url="https://fake/v1",
       key_env="NONE") -> Endpoint:
    return Endpoint(endpoint_id=endpoint_id, provider_id=provider, model_id=model,
                    provider_model_name=model, base_url=base_url,
                    api_key_env=key_env, tools_advertised=tools, json_advertised=json_ok,
                    advertised_context_tokens=context, discovered_at=utcnow())


def creds(e: Endpoint) -> object:
    return load_credentials(e, env={"NONE": ""})


def ok_chat(payload: dict) -> httpx.Response:
    return httpx.Response(200, json=payload)


def async_client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://fake")


def run(coro):
    return asyncio.run(coro)


# ---- Scenario 1: provider says model exists but inference 404s ----
def test_scenario1_inference_404_is_absent():
    def handler(request: httpx.Request):
        assert request.url.path.endswith("/chat/completions")
        return httpx.Response(404, json={"error": {"message": "model not found"}})
    e = ep()
    probe = ReachabilityProbe(client=async_client(handler))
    result = run(probe.run(e, creds(e)))
    assert result.status == "FAILURE"
    obs = {m.predicate: m for m in result.measurements}
    assert obs["endpoint.reachable"].state == State.ABSENT.value
    assert obs["endpoint.reachable"].value_number == 0.0


# ---- Scenario 2: HTTP 200 but malformed stream ----
def test_scenario2_malformed_stream():
    async def handler(request: httpx.Request):
        return httpx.Response(200, text="data: {not json}\n\n",
                              headers={"content-type": "text/event-stream"})
    e = ep()
    probe = TTFTProbe(client=async_client(handler))
    result = run(probe.run(e, creds(e)))
    assert result.status == "FAILURE"
    assert any("malformed_stream" in err for err in result.errors)
    obs = {m.predicate: m for m in result.measurements}
    assert obs["endpoint.stream_malformed"].state == State.UNAVAILABLE.value
    assert obs["probe.success"].value_number == 0.0

    # a well-formed stream must NOT trip malformed detection
    def ok_handler(request: httpx.Request):
        return httpx.Response(
            200,
            text="data: {\"choices\":[{\"delta\":{\"content\":\"hi\"}}]}\n\n"
                 "data: [DONE]\n\n",
            headers={"content-type": "text/event-stream"})
    e2 = ep(endpoint_id="test:model-y")
    probe2 = TTFTProbe(client=async_client(ok_handler))
    result2 = run(probe2.run(e2, creds(e2)))
    assert result2.status == "SUCCESS"
    obs2 = {m.predicate: m for m in result2.measurements}
    assert obs2["endpoint.stream_supported"].value_number == 1.0
    assert obs2["endpoint.ttft_ms"].value_number is not None


# ---- Scenario 3: tool capability advertised but fails ----
def test_scenario3_tool_advertised_but_fails():
    def handler(request: httpx.Request):
        import json as _json
        body = _json.loads(request.content or b"{}")
        assert body.get("tools"), "probe must send tools"
        return ok_chat({"model": "model-x", "choices": [
            {"message": {"role": "assistant", "content": "214 + 39 = 253"}}]})
    e = ep(tools=True)
    probe = ToolsProbe(client=async_client(handler))
    result = run(probe.run(e, creds(e)))
    assert result.status == "SUCCESS"  # endpoint worked, but capability failed
    obs = {m.predicate: m for m in result.measurements}
    assert obs["endpoint.tool_called"].value_number == 0.0
    assert obs["endpoint.tool_success"].value_number == 0.0

    # resolve(tools=True) must exclude an endpoint whose tool_success is 0
    db = DB(":memory:")
    db.upsert_endpoint(e)
    _inject(db, e, [("ttft_ms", 100, "ms", State.KNOWN.value),
                    ("output_tps", 50, "tokens_per_second", State.KNOWN.value),
                    ("tool_success", 0.0, "flag", State.KNOWN.value),
                    ("probe.success", 1.0, "flag", State.KNOWN.value)])
    aggregate_windows(db, window_seconds=3600)
    out = resolve(db, capability="coding", tools=True, min_success_rate=0.5,
                  min_tool_success=0.5)
    assert out["recommended"] is None
    reasons = [r["excluded_reasons"] for r in out["excluded"]]
    assert any("tool_success_below_0.5" in r for r in reasons)


# ---- Scenario 4: endpoint switches model alias ----
def test_scenario4_model_alias_switch():
    def handler(request: httpx.Request):
        return ok_chat({"model": "some-other-model-3", "choices": [
            {"message": {"role": "assistant", "content": "pong"}}]})
    e = ep()
    probe = ReachabilityProbe(client=async_client(handler))
    result = run(probe.run(e, creds(e)))
    obs = {m.predicate: m for m in result.measurements}
    assert obs["endpoint.model_served"].state == State.CONFLICTED.value
    assert obs["endpoint.model_served"].value_text == "some-other-model-3"

    # matching alias stays KNOWN
    def ok_handler(request: httpx.Request):
        return ok_chat({"model": "model-x", "choices": [
            {"message": {"role": "assistant", "content": "pong"}}]})
    e2 = ep(endpoint_id="test:model-y")
    probe2 = ReachabilityProbe(client=async_client(ok_handler))
    result2 = run(probe2.run(e2, creds(e2)))
    obs2 = {m.predicate: m for m in result2.measurements}
    assert obs2["endpoint.model_served"].state == State.KNOWN.value


# ---- Scenario 5: one outlier TTFT doesn't destroy p50 ----
def test_scenario5_outlier_ttft():
    values = [100.0, 105.0, 110.0, 98.0, 102.0, 103.0, 5000.0]
    p50 = percentile(values, 50)
    p90 = percentile(values, 90)
    assert p50 == 103.0  # nearest-rank median robust to the 5000 outlier
    assert p50 < 3 * 103.0  # sanity
    assert p90 > p50


# ---- Scenario 6: stale benchmark removed from current ranking ----
def test_scenario6_stale_removed():
    import datetime as dt
    db = DB(":memory:")
    e = ep(context=64000)
    db.upsert_endpoint(e)
    old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _inject(db, e, [("ttft_ms", 90, "ms", State.KNOWN.value),
                    ("output_tps", 80, "tokens_per_second", State.KNOWN.value),
                    ("probe.success", 1.0, "flag", State.KNOWN.value)],
            observed_at=old)
    aggregate_windows(db, window_seconds=3600, now=utcnow())
    out = resolve(db, capability="coding", stale_after_seconds=60 * 15)
    assert out["recommended"] is None
    assert any("stale" in r["excluded_reasons"]
               for r in out["excluded"] if r.get("excluded_reasons"))


# ---- Scenario 7: provider outage ----
def test_scenario7_outage():
    async def handler(request: httpx.Request):
        raise httpx.ConnectError("connection refused", request=request)
    e = ep()
    client = async_client(handler)
    probe = ReachabilityProbe(client=client)
    result = run(probe.run(e, creds(e)))
    obs = {m.predicate: m for m in result.measurements}
    assert obs["endpoint.reachable"].state == State.UNAVAILABLE.value
    assert result.errors and "connect_error" in result.errors[0]

    db = DB(":memory:")
    db.upsert_endpoint(e)
    _inject(db, e, [("ttft_ms", None, "ms", State.UNAVAILABLE.value),
                    ("probe.success", 0.0, "flag", State.KNOWN.value)])
    aggregate_windows(db, window_seconds=3600)
    out = resolve(db, capability="coding")
    assert out["recommended"] is None
    assert any("success_rate_below_0.5" in r["excluded_reasons"]
               for r in out["excluded"] if r.get("excluded_reasons"))


# ---- Scenario 8: rate limit distinguished from outage ----
def test_scenario8_rate_limit_vs_outage():
    def handler(request: httpx.Request):
        return httpx.Response(429, json={"error": {"message": "rate limited"}})
    e = ep()
    probe = ReachabilityProbe(client=async_client(handler))
    result = run(probe.run(e, creds(e)))
    obs = {m.predicate: m for m in result.measurements}
    assert obs["endpoint.reachable"].state == State.RATE_LIMITED.value
    assert obs["endpoint.reachable"].value_text == "http 429"

    def handler503(request: httpx.Request):
        return httpx.Response(503, json={"error": {"message": "overloaded"}})
    e2 = ep(endpoint_id="test:model-z")
    probe2 = ReachabilityProbe(client=async_client(handler503))
    result2 = run(probe2.run(e2, creds(e2)))
    obs2 = {m.predicate: m for m in result2.measurements}
    assert obs2["endpoint.reachable"].state == State.UNAVAILABLE.value
    assert State.RATE_LIMITED != State.UNAVAILABLE


def _inject(db: DB, e: Endpoint, rows: list[tuple], observed_at: str = None,
            value_texts: dict = None):
    """Insert synthetic observations for an endpoint (test scaffolding;
    clearly labeled source_type='test_fixture'). Rows use bare metric names;
    probe.success stays bare (probe-level predicate)."""
    import uuid
    value_texts = value_texts or {}
    now = observed_at or utcnow()
    for metric, val, unit, state in rows:
        rid = f"testrun-{uuid.uuid4().hex[:8]}"
        db.insert_probe_run(rid, e.endpoint_id, "test-fixture", utcnow())
        predicate = metric if metric.startswith("probe.") else f"endpoint.{metric}"
        db.insert_observation_row(rid, metric, value_numeric=val, unit=unit, state=state,
                                  subject_id=e.endpoint_id, predicate=predicate,
                                  value_text=value_texts.get(metric),
                                  source_type="test_fixture", source_id="pytest",
                                  observed_at=now)
        db.finish_probe_run(rid, "SUCCESS")