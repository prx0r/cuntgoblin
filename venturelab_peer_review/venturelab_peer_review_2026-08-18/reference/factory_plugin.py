from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

@dataclass(frozen=True)
class Opportunity:
    id: str
    title: str
    data: dict[str, Any]

@dataclass(frozen=True)
class EvidenceBundle:
    opportunity_id: str
    evidence_ids: tuple[str, ...]
    coverage: float
    confidence: float
    unknowns: tuple[str, ...]

@dataclass(frozen=True)
class BuildPlan:
    id: str
    factory_type: str
    jobs: tuple[dict[str, Any], ...]
    acceptance: dict[str, Any]

@dataclass(frozen=True)
class ArtifactSet:
    artifacts: tuple[str, ...]

@dataclass(frozen=True)
class Certificate:
    id: str
    accepted: bool
    checks: tuple[dict[str, Any], ...]

@dataclass
class FactoryContext:
    store: Any
    artifacts: Any
    evidence: Any
    scheduler: Any
    executor: Any
    router: Any
    verifiers: Any
    sources: Any
    publishers: Any

@runtime_checkable
class FactoryPlugin(Protocol):
    factory_type: str
    def discover(self, ctx: FactoryContext) -> list[Opportunity]: ...
    def research(self, ctx: FactoryContext, opportunity: Opportunity) -> EvidenceBundle: ...
    def plan(self, ctx: FactoryContext, opportunity: Opportunity, evidence: EvidenceBundle) -> BuildPlan: ...
    def build(self, ctx: FactoryContext, plan: BuildPlan) -> ArtifactSet: ...
    def verify(self, ctx: FactoryContext, plan: BuildPlan, artifacts: ArtifactSet) -> Certificate: ...
    def publish(self, ctx: FactoryContext, certificate: Certificate) -> Any: ...
    def observe(self, ctx: FactoryContext, publication: Any) -> Any: ...
