import hashlib
from .identity import stable_json_for_tests

def h(b): return hashlib.sha256(b).digest()
def leaf_hash(r): return h(b"\x00"+stable_json_for_tests(r))
def node_hash(l,r): return h(b"\x01"+l+r)

def merkle_root(records):
    level=[leaf_hash(r) for r in records]
    if not level: return hashlib.sha256(b"").hexdigest()
    while len(level)>1:
        nxt=[]
        for i in range(0,len(level),2):
            nxt.append(node_hash(level[i],level[i+1]) if i+1<len(level) else level[i])
        level=nxt
    return level[0].hex()

def inclusion_proof(records,index):
    level=[leaf_hash(r) for r in records]
    if index<0 or index>=len(level): raise IndexError(index)
    idx=index; proof=[]
    while len(level)>1:
        if idx%2==0 and idx+1<len(level): proof.append(("R",level[idx+1].hex()))
        elif idx%2==1: proof.append(("L",level[idx-1].hex()))
        nxt=[]
        for i in range(0,len(level),2):
            nxt.append(node_hash(level[i],level[i+1]) if i+1<len(level) else level[i])
        idx//=2; level=nxt
    return proof

def verify_inclusion(record,index,proof,root_hex):
    cur=leaf_hash(record)
    for side,hx in proof:
        other=bytes.fromhex(hx)
        cur=node_hash(cur,other) if side=="R" else node_hash(other,cur)
    return cur.hex()==root_hex
