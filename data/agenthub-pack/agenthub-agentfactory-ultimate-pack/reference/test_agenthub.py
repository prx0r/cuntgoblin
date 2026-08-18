from agenthub.types import (
    ArchitectureNeed, ArchitectureCapabilities, AgentSystem,
    Architecture, Node, Edge, ModelSlot, AssessmentVector, PromotionEvidence
)
from agenthub.resolver import resolve_architecture
from agenthub.metrics import pareto_frontier
from agenthub.identity import build_id
from agenthub.simulator import simulate, GraphError
from agenthub.lineage import apply_mutation
from agenthub.failures import FaultResult, aggregate_faults
from agenthub.promotion import promotion_decision
from agenthub.hermes import compile_hermes_plan


def sys(id, **kw):
    caps=ArchitectureCapabilities(
        persistent_state=kw.pop("persistent_state",True),
        independent_verification=kw.pop("independent_verification",True),
        resumable=kw.pop("resumable",True),
        tool_use=kw.pop("tool_use",True),
        max_parallelism=kw.pop("max_parallelism",8),
    )
    return AgentSystem(
        id,"hermes",["planner-worker"],caps,
        benchmark_fit=kw.pop("benchmark_fit",.9),
        economics_fit=kw.pop("economics_fit",.8),
        topology_fit=kw.pop("topology_fit",.9),
        state_fit=kw.pop("state_fit",.9),
        verification_fit=kw.pop("verification_fit",.9),
        **kw
    )


def test_unknown_hard_capability_excludes():
    n=ArchitectureNeed("n",persistent_state=True)
    s=sys("x",persistent_state=None)
    out=resolve_architecture(n,[s])
    assert out["decision"]=="SYNTHESIZE_EXPERIMENTAL_BUILD"
    assert "x" in out["excluded"]


def test_reuse_high_fit():
    n=ArchitectureNeed("n",persistent_state=True,independent_verification=True,parallelism=4)
    out=resolve_architecture(n,[sys("good")])
    assert out["decision"]=="REUSE"


def test_low_fit_synthesizes():
    n=ArchitectureNeed("n")
    s=sys("weak",benchmark_fit=.1,economics_fit=.1,topology_fit=.1,state_fit=.1,verification_fit=.1,runtime_fit=.1)
    out=resolve_architecture(n,[s])
    assert out["decision"]=="SYNTHESIZE_EXPERIMENTAL_BUILD"


def test_build_identity_changes_with_model_policy():
    a=build_id("s","abc",{"x":1},"hermes","1",{"policy":"a"})
    b=build_id("s","abc",{"x":1},"hermes","1",{"policy":"b"})
    assert a != b


def test_pareto_keeps_tradeoffs():
    xs={
      "cheap":AssessmentVector(.7,1,10,.8,2),
      "good":AssessmentVector(.9,2,10,.8,2),
      "bad":AssessmentVector(.6,3,20,.5,4),
    }
    f=pareto_frontier(xs)
    assert "cheap" in f and "good" in f and "bad" not in f


def test_simulator_information_retention():
    a=Architecture("a",
        [Node("p","planner",duration=1,token_cost=2),Node("w","worker",duration=2,token_cost=3)],
        [Edge("p","w",retention=.5)])
    r=simulate(a)
    assert r["makespan"]==3
    assert r["information_survival"]==.5


def test_cycle_rejected():
    a=Architecture("a",[Node("a","x"),Node("b","x")],[Edge("a","b"),Edge("b","a")])
    try:
        simulate(a)
        assert False
    except GraphError:
        pass


def test_semantic_fork_records_parent_and_mutation():
    a=Architecture("parent",[Node("worker","worker")],[])
    c=apply_mutation(a,{"op":"ADD_VERIFIER","from_node":"worker","child_id":"child"})
    assert "parent" in c.parent_ids
    assert c.mutations[-1]["op"]=="ADD_VERIFIER"
    assert any(n.role=="verifier" for n in c.nodes)


def test_failure_metrics():
    m=aggregate_faults([
        FaultResult("a",True,True,1,5),
        FaultResult("b",True,False,3,5),
    ])
    assert m["detection_rate"]==1
    assert m["recovery_rate"]==.5
    assert 0 < m["mean_cascade_radius"] < 1


def test_promotion_requires_multiple_evidence_gates():
    e=PromotionEvidence(1,1,1,True,True,True,True)
    d,fail=promotion_decision(e)
    assert d=="KEEP_AS_BUILD"
    assert "TOO_FEW_TASKS" in fail


def test_promotion_passes_strict_case():
    e=PromotionEvidence(4,2,3,True,True,True,True)
    d,fail=promotion_decision(e)
    assert d=="PROMOTE_VERIFIED_AGENT_SYSTEM"
    assert fail==[]


def test_hermes_requires_all_model_slots():
    a=Architecture("a",[Node("worker","worker","worker")],[],[ModelSlot("worker","coding_patch",.7)])
    try:
        compile_hermes_plan(a,{})
        assert False
    except ValueError:
        pass


def test_hermes_uses_hotswap_resolutions():
    a=Architecture("a",[Node("worker","worker","worker")],[],[ModelSlot("worker","coding_patch",.7)])
    p=compile_hermes_plan(a,{"worker":{"route_id":"r1","model_id":"m1"}})
    assert p["model_selection"]=="hotswap"
    assert p["nodes"][0]["model"]["route_id"]=="r1"
