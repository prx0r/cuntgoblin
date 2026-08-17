"""Schema: universal evidence envelope + state enum + entity dataclasses.

Envelope shape (spec section 0):
{
  "subject":   {"type": "endpoint", "id": "openrouter:deepseek-r1:novita"},
  "predicate": "endpoint.throughput",
  "value":     {"number": 67.4, "unit": "tokens_per_second"},
  "state":     "KNOWN",
  "observed_at": "...", "valid_until": "...",
  "source":    {"type": "synthetic_probe", "id": "..."},
  "method":    {"id": "throughput-probe-v1", "version": "1.0.0"},
  "confidence": 0.98,
  "evidence":   [{"artifact_sha256": "...", "selector": "$.metrics.output_tps"}]
}
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class State(str, Enum):
    """Common state enum (spec section 0), extended with RATE_LIMITED so the
    required scenario 'rate limit response distinguished from outage' is
    representable as a distinct state. Extension is explicit, documented and
    used by both API and tests."""
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    ABSENT = "ABSENT"
    NOT_OBSERVED = "NOT_OBSERVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    STALE = "STALE"
    CONFLICTED = "CONFLICTED"
    UNAVAILABLE = "UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"  # extension beyond the spec's 8-state enum


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


@dataclass
class EvidenceRef:
    artifact_sha256: str
    selector: str = "$"

    def to_dict(self) -> dict:
        return {"artifact_sha256": self.artifact_sha256, "selector": self.selector}


@dataclass
class Observation:
    """One factual observation emitted by a collector, in the universal
    envelope. Persisted one-per-row in probe_measurements and one-per-line in
    data/runs/<run-id>/results.jsonl."""
    subject_type: str = "endpoint"
    subject_id: str = ""
    predicate: str = ""
    value_number: Optional[float] = None
    value_text: Optional[str] = None
    unit: str = ""
    state: str = State.UNKNOWN.value
    observed_at: str = field(default_factory=utcnow)
    valid_until: Optional[str] = None
    source_type: str = "probe"
    source_id: str = ""
    method_id: str = ""
    method_version: str = ""
    confidence: float = 0.98
    artifact_sha256: Optional[str] = None
    evidence_selector: str = "$"

    def envelope(self) -> dict:
        value: dict[str, Any] = {}
        if self.value_number is not None:
            value["number"] = self.value_number
        if self.value_text is not None:
            value["text"] = self.value_text
        if self.unit:
            value["unit"] = self.unit
        ev: list[dict] = []
        if self.artifact_sha256:
            ev.append({"artifact_sha256": self.artifact_sha256,
                       "selector": self.evidence_selector})
        return {
            "subject": {"type": self.subject_type, "id": self.subject_id},
            "predicate": self.predicate,
            "value": value,
            "state": self.state,
            "observed_at": self.observed_at,
            "valid_until": self.valid_until,
            "source": {"type": self.source_type, "id": self.source_id},
            "method": {"id": self.method_id, "version": self.method_version},
            "confidence": self.confidence,
            "evidence": ev,
        }


@dataclass
class Artifact:
    """Raw bytes captured during a probe, content-addressed by sha256."""
    sha256: str
    filename: str
    content_type: str
    size: int
    stored_path: str
    created_at: str = field(default_factory=utcnow)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ProbeResult:
    status: str = "SUCCESS"            # SUCCESS | FAILURE
    measurements: list[Observation] = field(default_factory=list)
    raw_artifacts: list[dict] = field(default_factory=list)  # dicts -> stored as json artifacts
    errors: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)


@dataclass
class Endpoint:
    """Entity `Endpoint` from the common entities list (spec section 0)."""
    endpoint_id: str
    provider_id: str
    model_id: str
    provider_model_name: str
    base_url: str
    region: str = ""
    deployment_variant: str = ""
    quantization_state: str = "unknown"
    advertised_context_tokens: Optional[int] = None
    tools_advertised: bool = False
    json_advertised: bool = False
    pricing: dict = field(default_factory=dict)  # {"prompt_per_1k": n, "completion_per_1k": n, "currency": "USD"}
    api_key_env: Optional[str] = None
    base_url_env: Optional[str] = None
    discovered_at: str = field(default_factory=utcnow)
    retired_at: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def with_resolved_url(self) -> "Endpoint":
        """Resolve base_url from env if base_url_env is set (never leaks secrets)."""
        out = self
        if self.base_url_env:
            import os
            v = os.environ.get(self.base_url_env)
            if v:
                out = Endpoint(**{**asdict(self), "base_url": v.rstrip("/")})
        return out

    def key_missing(self) -> bool:
        if not self.api_key_env:
            return False
        import os
        return not os.environ.get(self.api_key_env)


def json_dumps(obj: Any) -> str:
    return json.dumps(obj, default=str, sort_keys=True)