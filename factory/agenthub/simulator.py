from __future__ import annotations
from collections import defaultdict, deque
from .types import Architecture


class GraphError(ValueError):
    pass


def validate_dag(arch: Architecture):
    nodes={n.node_id for n in arch.nodes}
    indeg={n:0 for n in nodes}
    adj=defaultdict(list)
    for e in arch.edges:
        if e.src not in nodes or e.dst not in nodes:
            raise GraphError("edge references missing node")
        if not 0 <= e.retention <= 1:
            raise GraphError("retention out of range")
        adj[e.src].append(e.dst)
        indeg[e.dst]+=1
    q=deque([n for n,d in indeg.items() if d==0])
    seen=0
    while q:
        x=q.popleft(); seen+=1
        for y in adj[x]:
            indeg[y]-=1
            if indeg[y]==0:q.append(y)
    if seen != len(nodes):
        raise GraphError("cycle detected")
    return True


def simulate(arch: Architecture):
    validate_dag(arch)
    by={n.node_id:n for n in arch.nodes}
    preds=defaultdict(list)
    for e in arch.edges:
        preds[e.dst].append(e)

    # topological relaxation
    remaining=set(by)
    finish={}
    info={}
    while remaining:
        progressed=False
        for nid in list(remaining):
            if all(e.src in finish for e in preds[nid]):
                start=max([finish[e.src] for e in preds[nid]], default=0)
                finish[nid]=start+by[nid].duration
                incoming=[info[e.src]*e.retention for e in preds[nid]]
                info[nid]=min(incoming) if incoming else 1.0
                remaining.remove(nid); progressed=True
        if not progressed:
            raise GraphError("cannot simulate")

    sinks=set(by)-{e.src for e in arch.edges}
    information_survival=min([info[n] for n in sinks],default=1.0)
    return {
        "makespan":max(finish.values(),default=0),
        "token_cost":sum(n.token_cost for n in arch.nodes),
        "information_survival":round(information_survival,6),
        "node_count":len(arch.nodes),
        "edge_count":len(arch.edges),
    }
