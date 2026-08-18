from venturelab_core.state import transition
from venturelab_core.identity import dedupe_key,trigger_id
from venturelab_core.merkle import merkle_root,inclusion_proof,verify_inclusion
from venturelab_core.graph import validate_dag,ready_nodes,GraphError
from venturelab_core.queue import should_retry,backoff_seconds,priority
from venturelab_core.scheduler import due_trigger,catchup_times
from venturelab_core.release import transition as rtransition

def test_state_shortcut_rejected():
    try: transition("READY","SUCCEEDED"); assert False
    except ValueError: pass

def test_state_normal_path():
    s="PENDING"
    for t in ["READY","LEASED","RUNNING","VERIFYING","SUCCEEDED"]: s=transition(s,t)
    assert s=="SUCCEEDED"

def test_dedupe_by_stage():
    assert dedupe_key("w","1","t","i","a") != dedupe_key("w","1","t","i","b")

def test_trigger_idempotent():
    x=trigger_id("s","2026-08-18T00:00:00Z")
    assert due_trigger("s","2026-08-18T00:00:00Z",{x}) is None

def test_merkle_order_sensitive():
    assert merkle_root([{"seq":1},{"seq":2}]) != merkle_root([{"seq":2},{"seq":1}])

def test_merkle_proof():
    rs=[{"seq":i} for i in range(1,8)]
    root=merkle_root(rs); p=inclusion_proof(rs,4)
    assert verify_inclusion(rs[4],4,p,root)

def test_cycle_rejected():
    try: validate_dag(["a","b"],[("a","b"),("b","a")]); assert False
    except GraphError: pass

def test_ready_nodes():
    assert ready_nodes(["a","b","c"],[("a","c"),("b","c")],{"a":"SUCCEEDED","b":"SUCCEEDED","c":"PENDING"})==["c"]

def test_retry_policy():
    assert should_retry("SERVER",1,3)
    assert not should_retry("AUTH",1,3)

def test_backoff():
    assert backoff_seconds(3)>backoff_seconds(1)

def test_priority():
    assert priority(.9,.9,.9,.9,.1)>priority(.2,.9,.9,.9,.1)

def test_catchup():
    assert catchup_times("latest_only",[1,2,3])==[3]

def test_release_skip_rejected():
    try: rtransition("GITHUB_PUBLISHED","RELEASED"); assert False
    except ValueError: pass

def test_release_path():
    s="DRAFT"
    for t in ["CERTIFIED","GITHUB_STAGED","GITHUB_PUBLISHED","DEPLOYING","LIVE_VERIFIED","RELEASED"]: s=rtransition(s,t)
    assert s=="RELEASED"
