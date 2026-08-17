from __future__ import annotations
from .types import PromotionEvidence


def promotion_decision(e: PromotionEvidence) -> tuple[str,list[str]]:
    failures=[]
    if e.zero_tolerance_failure:
        failures.append("ZERO_TOLERANCE_FAILURE")
    if not e.passed_target_suite:
        failures.append("TARGET_SUITE_NOT_PASSED")
    if not e.beats_simple_baseline:
        failures.append("NO_BASELINE_UPLIFT")
    if not e.reproducible:
        failures.append("NOT_REPRODUCIBLE")
    if not e.ablation_supports_claim:
        failures.append("NO_STRUCTURAL_ABLATION")
    if e.distinct_tasks < 3:
        failures.append("TOO_FEW_TASKS")
    if not e.narrow_domain and e.task_categories < 2:
        failures.append("TOO_NARROW")
    if e.repetitions_per_key_task < 2:
        failures.append("TOO_FEW_REPETITIONS")

    if failures:
        return "KEEP_AS_BUILD", failures
    return "PROMOTE_VERIFIED_AGENT_SYSTEM", []
