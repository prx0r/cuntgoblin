"""Pydantic schemas for the MCPTruth API surface."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class Subject(BaseModel):
    type: str
    id: str


class Value(BaseModel):
    number: Optional[float] = None
    text: Optional[str] = None
    unit: Optional[str] = None


class Source(BaseModel):
    type: str = "probe"
    id: str


class Method(BaseModel):
    id: str
    version: str


class EvidenceRef(BaseModel):
    artifact_sha256: str
    selector: str


class OracleEnvelope(BaseModel):
    """The universal evidence envelope (spec §0)."""
    observation_id: Optional[str] = None
    subject: Subject
    predicate: str
    value: Optional[Value] = None
    state: str
    observed_at: str
    valid_until: Optional[str] = None
    source: Source
    method: Method
    confidence: float = 0.98
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ServerOut(BaseModel):
    server_id: str
    name: str
    description: str = ""
    source_registry: str
    source_url: str = ""
    transport: str
    command: Optional[str] = None
    args: list[str] = Field(default_factory=list)
    url: Optional[str] = None
    auth_scheme: str = "none"
    auth_notes: str = ""
    status: str = "REGISTERED"
    deep_test: int = 0
    discovered_at: str
    retired_at: Optional[str] = None
    current_version: Optional[dict] = None
    # current-state projections (populated by reducer API view)
    window: Optional[dict] = None


class ToolOut(BaseModel):
    tool_id: str
    server_id: str
    name: str
    description: str = ""
    schema_sha256: str
    schema_token_count: int
    safety_class: str
    first_seen: str
    last_seen: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    capabilities: list[dict] = Field(default_factory=list)


class MeasurementOut(BaseModel):
    measurement_id: str
    probe_run_id: str
    metric: str
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    unit: str = ""
    state: str
    observed_at: str
    server_id: Optional[str] = None
    run_status: Optional[str] = None
    error_class: Optional[str] = None


class ProbeRunOut(BaseModel):
    probe_run_id: str
    server_id: str
    probe_type: str
    started_at: str
    completed_at: Optional[str] = None
    status: str
    method_version: str
    run_dir: Optional[str] = None
    error_class: Optional[str] = None
    error_detail: Optional[str] = None


class SchemaChangeOut(BaseModel):
    change_id: str
    server_id: str
    tool_name: str
    old_schema_sha256: Optional[str] = None
    new_schema_sha256: Optional[str] = None
    change_type: str
    detected_at: str
    detail: str = ""


class WindowOut(BaseModel):
    server_id: str
    window_start: str
    window_end: str
    samples: int = 0
    init_success_rate: Optional[float] = None
    tools_list_success_rate: Optional[float] = None
    connection_ms_p50: Optional[float] = None
    connection_ms_p95: Optional[float] = None
    invocation_ms_p50: Optional[float] = None
    invocation_ms_p95: Optional[float] = None
    invocation_success_rate: Optional[float] = None
    tool_count: Optional[int] = None
    schema_break_count: int = 0


class HealthiestOut(BaseModel):
    rank: int
    server_id: str
    name: str
    transport: str
    deep_test: int
    observed: WindowOut
    freshness_seconds: int


class ResolveOut(BaseModel):
    """What a caller needs to decide 'should I use this server?'."""
    server_id: str
    name: str
    available: bool
    reason: str
    observed: Optional[WindowOut] = None
    freshness_seconds: Optional[int] = None


class HealthOut(BaseModel):
    status: str = "ok"
    ts: str
    db_observations: int
    db_servers: int
    version: str = "0.1.0"


class StatsOut(BaseModel):
    servers_tracked: int
    servers_deep_tested: int
    servers_active: int
    tools: int
    tools_by_safety: dict[str, int]
    capabilities: int
    tool_capability_mappings: int
    observations: int
    probe_runs: int
    schema_changes: int
    breaking_schema_changes: int
    measurements: int


class CoverageOut(BaseModel):
    servers_total: int
    servers_deep_test: int
    by_registry: dict[str, int]
    by_transport: dict[str, int]
    by_auth: dict[str, int]
    probe_types: list[dict]
    deep_tested_endpoints: list[dict]


class CapabilityImplementationOut(BaseModel):
    server_id: str
    server_name: str
    tool_id: str
    tool_name: str
    safety_class: str
    confidence: float
    mapping_method: str
    schema_sha256: str