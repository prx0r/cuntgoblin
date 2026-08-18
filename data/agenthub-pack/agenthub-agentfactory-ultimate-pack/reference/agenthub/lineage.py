from __future__ import annotations
from copy import deepcopy
from .types import Architecture, Node, Edge


def apply_mutation(arch: Architecture, mutation: dict) -> Architecture:
    child = deepcopy(arch)
    child.parent_ids = list(dict.fromkeys(child.parent_ids + [arch.architecture_id]))
    child.mutations = child.mutations + [mutation]
    op = mutation["op"]

    if op == "ADD_VERIFIER":
        node_id = mutation.get("node_id","verifier")
        if any(n.node_id == node_id for n in child.nodes):
            raise ValueError("node already exists")
        child.nodes.append(Node(node_id=node_id,role="verifier",model_slot=mutation.get("model_slot","verifier")))
        from_node = mutation["from_node"]
        child.edges.append(Edge(from_node,node_id,"review",1.0))

    elif op == "CHANGE_PARALLELISM":
        # Reference representation stores policy as semantic mutation only.
        pass

    elif op == "ADD_CONTEXT_COMPACTION":
        child.patterns = list(dict.fromkeys(child.patterns + ["context-compaction"]))

    elif op == "ADD_PERSISTENT_TASK_GRAPH":
        child.patterns = list(dict.fromkeys(child.patterns + ["persistent-task-graph"]))

    else:
        raise ValueError(f"unsupported mutation {op}")

    child.architecture_id = mutation.get("child_id", child.architecture_id + "_child")
    return child
