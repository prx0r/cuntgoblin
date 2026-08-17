from __future__ import annotations

from dataclasses import dataclass
from math import exp, log
from statistics import median
from typing import Iterable, Mapping, Sequence


EPS = 1e-9


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def weighted_geomean(values: Mapping[str, float], weights: Mapping[str, float]) -> float:
    """Weighted geometric mean for normalized positive scores."""
    denom = sum(weights.values())
    if denom <= 0:
        raise ValueError("weights must sum positive")
    total = 0.0
    for k, w in weights.items():
        if k not in values:
            raise KeyError(f"missing mandatory dimension: {k}")
        v = max(EPS, clamp01(values[k]))
        total += w * log(v)
    return exp(total / denom)


def robust_zscore(current: float, history: Sequence[float]) -> float | None:
    """MAD-based robust z-score. None when history has no dispersion."""
    if len(history) < 5:
        return None
    med = median(history)
    mad = median([abs(x - med) for x in history])
    if mad <= EPS:
        return None
    return 0.6745 * (current - med) / mad


def log_growth(current: float, baseline: float) -> float:
    """Stable growth transform that avoids percent-growth explosions near zero."""
    if current < 0 or baseline < 0:
        raise ValueError("counts/levels must be nonnegative")
    return log(1.0 + current) - log(1.0 + baseline)


@dataclass(frozen=True)
class TopicFeatures:
    velocity: float
    acceleration: float
    change_point: float
    source_breadth: float
    persistence: float
    magnitude: float
    novelty: float
    source_quality: float
    confidence: float
    coverage: float
    independent_source_families: int
    primary_policy_event: bool = False


TOPIC_WEIGHTS = {
    "velocity": 0.20,
    "acceleration": 0.15,
    "change_point": 0.15,
    "source_breadth": 0.15,
    "persistence": 0.10,
    "magnitude": 0.10,
    "novelty": 0.10,
    "source_quality": 0.05,
}


def topic_discovery_score(f: TopicFeatures) -> tuple[float, str]:
    if f.coverage < 0.50:
        return 0.0, "INSUFFICIENT_COVERAGE"
    if f.independent_source_families < 2 and not f.primary_policy_event:
        return 0.0, "INSUFFICIENT_SOURCE_BREADTH"
    score = sum(TOPIC_WEIGHTS[k] * clamp01(getattr(f, k)) for k in TOPIC_WEIGHTS)
    if score >= 0.68 and f.confidence >= 0.65:
        return round(score, 4), "ACTIVE_RESEARCH"
    if score >= 0.55:
        return round(score, 4), "WATCH"
    return round(score, 4), "STORE"


@dataclass(frozen=True)
class OpportunityFeatures:
    need: float
    gap: float
    feasibility: float
    economics: float
    moat: float
    portfolio: float
    risk: float
    confidence: float
    coverage: float
    positive_velocity: bool = False
    mandatory_unknown: bool = False


OPPORTUNITY_WEIGHTS = {
    "need": 0.22,
    "gap": 0.18,
    "feasibility": 0.18,
    "economics": 0.18,
    "moat": 0.10,
    "portfolio": 0.14,
}


def opportunity_score(f: OpportunityFeatures) -> tuple[float, str]:
    values = {k: getattr(f, k) for k in OPPORTUNITY_WEIGHTS}
    positive = weighted_geomean(values, OPPORTUNITY_WEIGHTS)
    risk_factor = 1.0 - 0.55 * clamp01(f.risk)
    evidence_factor = 0.55 + 0.45 * clamp01(f.confidence)
    score = clamp01(positive * risk_factor * evidence_factor)

    if f.mandatory_unknown:
        return round(score, 4), "RESEARCH"
    if score >= 0.72 and f.confidence >= 0.72 and f.coverage >= 0.70:
        return round(score, 4), "BUILD"
    if score >= 0.62:
        return round(score, 4), "RESEARCH"
    if score >= 0.48 and f.positive_velocity:
        return round(score, 4), "WATCH"
    if score < 0.48 and f.confidence >= 0.70:
        return round(score, 4), "REJECT"
    return round(score, 4), "LOW_PRIORITY"


@dataclass(frozen=True)
class JoinFeatures:
    semantic_plausibility: float
    signal_strength: float
    source_independence: float
    temporal_alignment: float
    persistence: float
    solution_gap: float
    novelty: float
    valid_mapping: bool = True
    independent_source_families: int = 2


JOIN_WEIGHTS = {
    "semantic_plausibility": 0.25,
    "signal_strength": 0.20,
    "source_independence": 0.15,
    "temporal_alignment": 0.10,
    "persistence": 0.10,
    "solution_gap": 0.15,
    "novelty": 0.05,
}


def join_score(f: JoinFeatures) -> tuple[float, str]:
    if not f.valid_mapping:
        return 0.0, "INVALID_MAPPING"
    if f.independent_source_families < 2:
        return 0.0, "INSUFFICIENT_SOURCE_INDEPENDENCE"
    if f.semantic_plausibility < 0.70:
        return 0.0, "SEMANTICALLY_IMPLAUSIBLE"
    values = {k: getattr(f, k) for k in JOIN_WEIGHTS}
    score = weighted_geomean(values, JOIN_WEIGHTS)
    return round(score, 4), "CANDIDATE_JOIN" if score >= 0.60 else "WEAK_JOIN"


@dataclass(frozen=True)
class FactoryFit:
    vision_fit: float
    market_scope_fit: float
    product_archetype_support: float
    component_reuse: float
    completion_contract_compatibility: float


def factory_fit_score(f: FactoryFit) -> float:
    return round(
        0.30 * clamp01(f.vision_fit)
        + 0.20 * clamp01(f.market_scope_fit)
        + 0.20 * clamp01(f.product_archetype_support)
        + 0.15 * clamp01(f.component_reuse)
        + 0.15 * clamp01(f.completion_contract_compatibility),
        4,
    )


@dataclass(frozen=True)
class FactoryGenesisFeatures:
    opportunity_count: int
    best_existing_fit: float
    repeatability: float
    shared_infra_reuse: float
    evidence_confidence: float
    independent_source_families: int
    max_single_source_evidence_share: float
    opportunity_mass: float
    reuse_roi: float
    strategic_coherence: float
    shared_infra_savings: float
    persistence: float


GENESIS_WEIGHTS = {
    "opportunity_mass": 0.25,
    "repeatability": 0.20,
    "evidence_confidence": 0.15,
    "strategic_coherence": 0.15,
    "shared_infra_savings": 0.15,
    "persistence": 0.10,
}


def factory_genesis_decision(f: FactoryGenesisFeatures) -> tuple[float, str, list[str]]:
    if f.best_existing_fit >= 0.75:
        return 0.0, "USE_EXISTING", []
    if f.best_existing_fit >= 0.60:
        return 0.0, "EXTEND_EXISTING", []

    failures: list[str] = []
    if f.opportunity_count < 3:
        failures.append("TOO_FEW_OPPORTUNITIES")
    if f.repeatability < 0.65:
        failures.append("LOW_REPEATABILITY")
    if f.shared_infra_reuse < 0.60:
        failures.append("LOW_SHARED_INFRA_REUSE")
    if f.evidence_confidence < 0.70:
        failures.append("LOW_EVIDENCE_CONFIDENCE")
    if f.independent_source_families < 3:
        failures.append("LOW_SOURCE_BREADTH")
    if f.max_single_source_evidence_share > 0.60:
        failures.append("SOURCE_CONCENTRATION")
    if f.opportunity_mass < 0.65:
        failures.append("LOW_OPPORTUNITY_MASS")
    if f.reuse_roi < 0.50:
        failures.append("LOW_REUSE_ROI")
    if failures:
        return 0.0, "NO_FACTORY", failures

    score = sum(GENESIS_WEIGHTS[k] * clamp01(getattr(f, k)) for k in GENESIS_WEIGHTS)
    if score >= 0.72:
        return round(score, 4), "SPAWN_CANDIDATE", []
    if score >= 0.58:
        return round(score, 4), "FACTORY_EXPERIMENT", []
    return round(score, 4), "NO_FACTORY", ["LOW_GENESIS_SCORE"]


@dataclass(frozen=True)
class ResearchAction:
    name: str
    score_if_low: float
    score_if_high: float
    dimension_confidence: float
    researchability: float
    dimension_weight: float
    normalized_cost: float


def approximate_voi(action: ResearchAction) -> float:
    sensitivity = abs(action.score_if_high - action.score_if_low)
    uncertainty = 1.0 - clamp01(action.dimension_confidence)
    gross = (
        sensitivity
        * uncertainty
        * clamp01(action.researchability)
        * clamp01(action.dimension_weight)
    )
    return round(gross - max(0.0, action.normalized_cost), 6)


def choose_next_research(actions: Iterable[ResearchAction]) -> tuple[str | None, float]:
    scored = [(approximate_voi(a), a.name) for a in actions]
    if not scored:
        return None, 0.0
    score, name = max(scored)
    if score <= 0:
        return None, score
    return name, score
