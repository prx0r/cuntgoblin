"""DB-level tests: schema fingerprinting, breaking-change detection,
capability mappings, and immutability of raw measurements."""

from __future__ import annotations

from app import db


def _serve(server_id: str) -> None:
    """Ensure a server row exists (tools have FK -> servers with FK on)."""
    if db.get_server(server_id) is None:
        db.upsert_server(server_id, server_id, "stdio", description="", deep_test=1)


def test_schema_fingerprint_content():
    canon = db.canonical_tool_schema("foo", "desc", {"type": "object", "properties": {"x": {"type": "string"}}})
    import hashlib
    manual = hashlib.sha256(
        '{"description":"desc","inputSchema":{"properties":{"x":{"type":"string"}},"type":"object"},"name":"foo"}'.encode()
    ).hexdigest()
    assert db._sha256(canon) == manual


def test_tool_insert_marks_added():
    _serve("p:srv-schema")
    res = db.upsert_tool("p:srv-schema", "newtool", "a brand new tool",
                         {"type": "object", "properties": {"q": {"type": "string"}},
                          "required": ["q"]}, "READ_ONLY")
    assert res["schema_token_count"] > 0
    changes = [c for c in db.list_schema_changes() if c["server_id"] == "p:srv-schema"]
    assert any(c["change_type"] == "ADDED" for c in changes)


def test_breaking_schema_change_detected():
    _serve("p:srv-schema")
    server = "p:srv-schema"
    new_schema = {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]}
    breaking_schema = {"type": "object", "properties": {"q": {"type": "string"}}, "required": []}
    db.upsert_tool(server, "api", "api tool", new_schema, "READ_ONLY")
    db.upsert_tool(server, "api", "api tool", breaking_schema, "READ_ONLY")
    changes = [c for c in db.list_schema_changes()
               if c["server_id"] == server and c["tool_name"] == "api"]
    breaking = [c for c in changes if c["change_type"] == "BREAKING"]
    assert breaking, "required-property removal must be BREAKING"
    assert breaking[0]["old_schema_sha256"] != breaking[0]["new_schema_sha256"]


def test_modified_schema_change_is_not_breaking():
    _serve("p:srv-schema-m")
    server = "p:srv-schema-m"
    s1 = {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]}
    s2 = {"type": "object", "properties": {"q": {"type": "string"}, "r": {"type": "number"}}, "required": ["q"]}
    db.upsert_tool(server, "api2", "api tool", s1, "READ_ONLY")
    db.upsert_tool(server, "api2", "api tool", s2, "READ_ONLY")
    changes = [c for c in db.list_schema_changes()
               if c["server_id"] == server and c["tool_name"] == "api2"]
    types = {c["change_type"] for c in changes}
    assert "MODIFIED" in types
    assert "BREAKING" not in types


def test_capability_mapping_curated_and_heuristic():
    from app.capabilities import map_tool_capabilities
    curated = map_tool_capabilities("mock", "read_doc", "read a document")
    assert any(c[0] == "filesystem.read" and c[1] == 1.0 and c[2] == "curated" for c in curated)
    heuristic = map_tool_capabilities("other", "lookup_user", "find a user in a repository")
    assert any(c[0] == "repository.read" for c in heuristic)
    assert any(c[2] == "heuristic" for c in heuristic)
    none = map_tool_capabilities("other", "xyzzy", "mystery")
    assert none == []


def test_tool_capability_persisted_folder():
    from app.capabilities import capability_implementations
    _serve("mock")
    t = db.upsert_tool("mock", "read_doc", "read a doc",
                       {"type": "object", "properties": {}}, "READ_ONLY")
    from app.capabilities import map_all_tools
    map_all_tools("mock", "read_doc", "read a doc", t["tool_id"])
    impls = capability_implementations("filesystem.read")
    assert any(i["tool_name"] == "read_doc" and i["confidence"] == 1.0 for i in impls)


def test_measurements_append_only():
    """Re-running probes never overwrites raw measurements; each row unique."""
    _serve("p:srv-imm")
    before = db.stats()["measurements"]
    run_id = db.start_probe_run("p:srv-imm", "full", "v1", "/tmp")
    db.record_measurement(run_id, "connection.ms", 1.0, None, "ms", db.STATE_KNOWN)
    db.record_measurement(run_id, "connection.ms", 1.0, None, "ms", db.STATE_KNOWN)
    # same content twice still yields distinct rows (timestamped ids)
    after = db.stats()["measurements"]
    assert after == before + 2


def test_upsert_server_preserves_registry():
    db.upsert_server("p:srv-upsert", "Upsert Test", "stdio", source_registry="github",
                     deep_test=1, auth_scheme="token")
    s = db.get_server("p:srv-upsert")
    assert s["source_registry"] == "github"
    assert s["auth_scheme"] == "token"
    assert s["deep_test"] == 1
    assert s["current_version"] is None or s["current_version"]["status"] == "CURRENT"