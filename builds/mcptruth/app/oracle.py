"""Oracle-compatible universal evidence envelope (specs/mcptruth/architecture.md §0).

Every factual observation emitted by a collector has this shape:

{
  "subject":  {"type": ..., "id": ...},
  "predicate": ...,
  "value":    {"number": ..., "unit": ...} | {"text": ...} | null,
  "state":    KNOWN|UNKNOWN|ABSENT|NOT_OBSERVED|NOT_APPLICABLE|STALE|CONFLICTED|UNAVAILABLE,
  "observed_at":  "ISO8601",
  "valid_until":  "ISO8601",
  "source":   {"type": ..., "id": ...},
  "method":   {"id": ..., "version": ...},
  "confidence": 0-1,
  "evidence": [{"artifact_sha256": ..., "selector": ...}]
}

observation_id = sha256 of the canonical JSON of the envelope (minus the id).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from . import db

STATE_KNOWN = db.STATE_KNOWN
STATE_NONE = db.STATE_NOT_OBSERVED
STATE_UNAVAILABLE = db.STATE_UNAVAILABLE


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def valid_until(seconds: int = 900) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat(timespec="milliseconds")


def content_address(envelope: dict) -> str:
    payload = {k: v for k, v in envelope.items() if k != "observation_id"}
    canon = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def build_envelope(
    subject_type: str,
    subject_id: str,
    predicate: str,
    state: str,
    source_id: str,
    method_id: str,
    method_version: str,
    value_number: Optional[float] = None,
    value_text: Optional[str] = None,
    unit: str = "",
    observed_at: Optional[str] = None,
    valid_for: Optional[int] = 900,
    confidence: float = 0.98,
    artifacts: Optional[list[dict]] = None,
    source_type: str = "probe",
) -> dict:
    obs_at = observed_at or now_iso()
    value: dict[str, Any] = {}
    if value_number is not None:
        value["number"] = value_number
    if value_text is not None:
        value["text"] = value_text
    if unit:
        value["unit"] = unit
    envelope = {
        "subject": {"type": subject_type, "id": subject_id},
        "predicate": predicate,
        "value": value or None,
        "state": state,
        "observed_at": obs_at,
        "valid_until": valid_until(valid_for) if valid_for else None,
        "source": {"type": source_type, "id": source_id},
        "method": {"id": method_id, "version": method_version},
        "confidence": confidence,
        "evidence": artifacts or [],
    }
    return envelope


def persist_envelope(envelope: dict) -> dict:
    oid = db.record_observation(envelope)
    env = dict(envelope)
    env["observation_id"] = oid
    return env


def artifact_sha256(raw: Any) -> str:
    """Content-address an artifact payload."""
    if isinstance(raw, (dict, list)):
        data = json.dumps(raw, sort_keys=True, separators=(",", ":")).encode("utf-8")
    elif isinstance(raw, str):
        data = raw.encode("utf-8")
    else:
        data = str(raw).encode("utf-8")
    return hashlib.sha256(data).hexdigest()