from __future__ import annotations
from .types import Architecture


def compile_hermes_plan(arch: Architecture, slot_resolutions: dict[str,dict]) -> dict:
    nodes=[]
    for n in arch.nodes:
        model=None
        if n.model_slot:
            if n.model_slot not in slot_resolutions:
                raise ValueError(f"missing model slot resolution: {n.model_slot}")
            model=slot_resolutions[n.model_slot]
        nodes.append({
            "id":n.node_id,
            "role":n.role,
            "model":model,
        })
    return {
        "runtime":"hermes",
        "architecture_id":arch.architecture_id,
        "nodes":nodes,
        "edges":[{"from":e.src,"to":e.dst,"kind":e.kind,"retention":e.retention} for e in arch.edges],
        "model_selection":"hotswap",
    }
