from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

class JobState(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    LEASED = "LEASED"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    RETRY_WAIT = "RETRY_WAIT"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

TERMINAL = {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}

@dataclass(frozen=True)
class JobRequest:
    factory_type: str
    task_kind: str
    input: dict[str, Any]
    idempotency_key: str
    budget_usd: float | None = None
    quality_floor: float = 0.70
    max_attempts: int = 3
    priority: int = 0
    dependencies: tuple[str, ...] = ()

@dataclass(frozen=True)
class WorkerResult:
    ok: bool
    payload: dict[str, Any] | None = None
    failure_class: str | None = None
    retryable: bool = False
    cost_usd: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Verification:
    accepted: bool
    checks: tuple[dict[str, Any], ...]
    retryable: bool = False
    missing: tuple[str, ...] = ()
