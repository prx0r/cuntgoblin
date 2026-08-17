from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    task_kind: str
    difficulty: str = "medium"
    criticality: str = "routine"
    quality_floor: float = 0.70
    free_policy: str = "prefer"
    paid_allowed: bool = True
    context_tokens_min: int = 0
    tools_required: bool = False
    json_required: bool = False
    estimated_input_tokens: int = 1000
    estimated_output_tokens: int = 500
    task_budget_usd: Optional[float] = None
    exploration_allowed: bool = True

    @property
    def cell_id(self) -> str:
        return "|".join([
            self.task_kind,
            self.difficulty,
            self.criticality,
            "tools" if self.tools_required else "no-tools",
            _context_bin(self.context_tokens_min),
        ])


def _context_bin(n: int) -> str:
    if n <= 16000: return "ctx16k"
    if n <= 64000: return "ctx64k"
    if n <= 128000: return "ctx128k"
    return "ctx128k+"


@dataclass
class Route:
    route_id: str
    model_id: str
    provider_id: str
    endpoint_id: Optional[str] = None
    account_id: Optional[str] = None
    active: bool = True
    free: bool = False
    input_per_m: Optional[float] = None
    output_per_m: Optional[float] = None
    context_tokens: Optional[int] = None
    tools_supported: Optional[bool] = None
    json_supported: Optional[bool] = None
    reliability: Optional[float] = None  # [0,1]
    latency_ms: Optional[float] = None
    prior_success: Optional[float] = None
    prior_confidence: float = 0.0
    breaker_open: bool = False
    quota_pressure: float = 0.0
    cheapest_paid_replacement_cost: float = 0.0
    evidence_ids: list[str] = field(default_factory=list)

    def request_cost(self, task: TaskSpec) -> Optional[float]:
        if self.free:
            return 0.0
        if self.input_per_m is None:
            return None
        if task.estimated_output_tokens > 0 and self.output_per_m is None:
            return None
        out_price = self.output_per_m or 0.0
        return (
            self.input_per_m * task.estimated_input_tokens
            + out_price * task.estimated_output_tokens
        ) / 1_000_000


@dataclass(frozen=True)
class Posterior:
    alpha: float
    beta: float

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)


@dataclass
class CandidateAssessment:
    route: Route
    p_success: float
    p_lower: float
    request_cost: float
    quota_shadow_cost: float
    expected_completion_cost: float
    excluded: list[str] = field(default_factory=list)
    exploration_sample: Optional[float] = None


@dataclass
class ExecutionPlan:
    task_id: str
    primary: Optional[CandidateAssessment]
    fallbacks: list[CandidateAssessment]
    excluded: dict[str, list[str]]
    reason_codes: list[str]
