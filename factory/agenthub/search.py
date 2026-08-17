from __future__ import annotations
from dataclasses import dataclass
from .types import Architecture, AssessmentVector
from .lineage import apply_mutation
from .metrics import pareto_frontier


@dataclass
class Evaluated:
    arch: Architecture
    metrics: AssessmentVector


def beam_search(seed: Architecture, mutation_templates: list[dict], evaluator, generations: int = 2, beam: int = 4):
    archive: dict[str,Evaluated] = {}
    current=[seed]
    for _ in range(generations):
        candidates=[]
        for parent in current:
            for i,m in enumerate(mutation_templates):
                mm=dict(m)
                mm.setdefault("child_id",f"{parent.architecture_id}_m{i}")
                try:
                    child=apply_mutation(parent,mm)
                except ValueError:
                    continue
                metrics=evaluator(child)
                archive[child.architecture_id]=Evaluated(child,metrics)
                candidates.append(child)
        if not candidates:
            break
        vectors={c.architecture_id:archive[c.architecture_id].metrics for c in candidates}
        frontier=pareto_frontier(vectors)
        current=[archive[k].arch for k in frontier[:beam]]
    return archive
