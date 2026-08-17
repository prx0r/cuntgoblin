"""API tests against the FastAPI app with a seeded + mock-probed DB."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["db_servers"] >= 50


def test_v1_stats():
    r = client.get("/v1/stats")
    assert r.status_code == 200
    b = r.json()
    assert b["servers_tracked"] >= 50
    assert b["servers_deep_tested"] >= 8
    assert b["tools"] >= 6
    assert b["observations"] >= 3
    assert b["measurements"] >= 6
    assert "READ_ONLY" in b["tools_by_safety"]


def test_v1_coverage():
    r = client.get("/v1/coverage")
    assert r.status_code == 200
    b = r.json()
    assert b["servers_total"] >= 50
    deep = b["deep_tested_endpoints"]
    assert any(d["server_id"] == "mock:mock-mcp" for d in deep)
    assert b["by_transport"]["stdio"] >= 1


def test_v1_servers():
    r = client.get("/v1/servers")
    assert r.status_code == 200
    servers = r.json()
    assert len(servers) >= 50
    ids = {s["server_id"] for s in servers}
    assert "mock:mock-mcp" in ids
    mock = [s for s in servers if s["server_id"] == "mock:mock-mcp"][0]
    assert mock["status"] == "ACTIVE"
    assert mock["deep_test"] == 1


def test_v1_server_detail_and_404():
    r = client.get("/v1/servers/mock:mock-mcp")
    assert r.status_code == 200
    assert r.json()["transport"] == "stdio"
    r404 = client.get("/v1/servers/does-not-exist")
    assert r404.status_code == 404


def test_v1_server_tools():
    r = client.get("/v1/servers/mock:mock-mcp/tools")
    assert r.status_code == 200
    tools = r.json()
    names = {t["name"] for t in tools}
    assert names == {"echo", "add", "read_doc", "list_tree", "web_search", "mutate_state"}
    assert all(len(t["schema_sha256"]) == 64 for t in tools)
    assert all(t["schema_token_count"] > 0 for t in tools)


def test_v1_server_history():
    r = client.get("/v1/servers/mock:mock-mcp/history")
    assert r.status_code == 200
    b = r.json()
    assert b["probe_runs"], "history should contain the mock probe run"
    assert b["measurements"]
    assert b["observations"]
    assert any(w["server_id"] == "mock:mock-mcp" for w in b["windows"])


def test_v1_tools_filters():
    r = client.get("/v1/tools", params={"server_id": "mock:mock-mcp", "safety": "MUTATING"})
    assert r.status_code == 200
    tools = r.json()
    assert len(tools) == 1 and tools[0]["name"] == "mutate_state"


def test_v1_capabilities_endpoint():
    r = client.get("/v1/capabilities")
    assert r.status_code == 200
    caps = {c["capability_id"] for c in r.json()}
    assert "filesystem.read" in caps
    assert "web.search" in caps


def test_v1_capability_implementations():
    r = client.get("/v1/capabilities/filesystem.read/implementations")
    assert r.status_code == 200
    impls = r.json()
    assert any(i["tool_name"] == "read_doc" and i["server_id"] == "mock" for i in impls)
    # a capability nobody implements should be an empty 200 (not an error)
    r2 = client.get("/v1/capabilities/cloud.provision/implementations")
    assert r2.status_code == 200
    assert r2.json() == []


def test_v1_healthiest_ranks_mock():
    r = client.get("/v1/healthiest", params={"require_deep": "true"})
    assert r.status_code == 200
    ranked = r.json()
    assert ranked, "mock probe must produce a healthiest ranking"
    top = ranked[0]
    assert top["server_id"] == "mock:mock-mcp"
    assert top["rank"] == 1
    assert top["observed"]["connection_ms_p50"] is not None
    assert top["freshness_seconds"] < 3600


def test_v1_healthiest_excludes_unreachable():
    # a ghost server was probed (FAILED CONNECTION_ERROR) -> must not rank
    r = client.get("/v1/healthiest")
    ids = {h["server_id"] for h in r.json()}
    assert "ghost:does-not-exist" not in ids
    assert "ghost:garbage-stdio" not in ids


def test_v1_schema_changes():
    r = client.get("/v1/schema-changes")
    assert r.status_code == 200
    changes = r.json()
    assert any(c["change_type"] == "ADDED" for c in changes)
    types = {c["change_type"] for c in changes}
    assert types <= {"ADDED", "MODIFIED", "BREAKING", "REMOVED"}


def test_v1_evidence_roundtrip():
    obs = client.get("/v1/servers/mock:mock-mcp/history").json()["observations"]
    assert obs
    oid = obs[0]["observation_id"]
    r = client.get(f"/v1/evidence/{oid}")
    assert r.status_code == 200
    env = r.json()
    assert env["observation_id"] == oid
    assert "subject" in env and "predicate" in env and "state" in env
    assert "evidence" in env
    r404 = client.get("/v1/evidence/" + "0" * 64)
    assert r404.status_code == 404


def test_404_returns_json():
    r = client.get("/v1/endpoints/nope")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/json")