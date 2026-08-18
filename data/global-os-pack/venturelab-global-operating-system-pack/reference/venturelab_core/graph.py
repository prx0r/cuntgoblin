from collections import defaultdict,deque

class GraphError(ValueError): pass

def validate_dag(nodes,edges):
    nodes=set(nodes); indeg={n:0 for n in nodes}; adj=defaultdict(list)
    for a,b in edges:
        if a not in nodes or b not in nodes: raise GraphError("missing node")
        adj[a].append(b); indeg[b]+=1
    q=deque(sorted(n for n,d in indeg.items() if d==0)); seen=[]
    while q:
        x=q.popleft(); seen.append(x)
        for y in adj[x]:
            indeg[y]-=1
            if indeg[y]==0:q.append(y)
    if len(seen)!=len(nodes): raise GraphError("cycle")
    return seen

def ready_nodes(nodes,edges,states):
    validate_dag(nodes,edges); preds=defaultdict(list)
    for a,b in edges: preds[b].append(a)
    return sorted(n for n in nodes if states.get(n)=="PENDING" and all(states.get(p)=="SUCCEEDED" for p in preds[n]))
