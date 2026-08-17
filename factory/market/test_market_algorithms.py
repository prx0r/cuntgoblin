from market_algorithms import (
    TopicFeatures, topic_discovery_score,
    OpportunityFeatures, opportunity_score,
    JoinFeatures, join_score,
    FactoryFit, factory_fit_score,
    FactoryGenesisFeatures, factory_genesis_decision,
    ResearchAction, choose_next_research,
    robust_zscore, log_growth,
)


def test_topic_needs_independent_sources():
    f = TopicFeatures(.9,.9,.9,.2,.9,.9,.9,.9,.9,.9,1,False)
    score, decision = topic_discovery_score(f)
    assert score == 0
    assert decision == "INSUFFICIENT_SOURCE_BREADTH"


def test_primary_policy_event_exception():
    f = TopicFeatures(.8,.8,.9,.2,.8,.8,.7,.95,.9,.9,1,True)
    score, decision = topic_discovery_score(f)
    assert score > 0
    assert decision in {"WATCH","ACTIVE_RESEARCH"}


def test_mandatory_unknown_cannot_build():
    f = OpportunityFeatures(.95,.95,.95,.95,.8,.8,.1,.95,.95,True,True)
    _, decision = opportunity_score(f)
    assert decision == "RESEARCH"


def test_join_blocks_semantic_nonsense():
    f = JoinFeatures(.4,.95,.95,.95,.95,.95,.95)
    score, decision = join_score(f)
    assert score == 0
    assert decision == "SEMANTICALLY_IMPLAUSIBLE"


def test_existing_factory_blocks_genesis():
    f = FactoryGenesisFeatures(
        5,.8,.9,.9,.9,5,.3,.9,2,.9,.9,.9
    )
    score, decision, failures = factory_genesis_decision(f)
    assert decision == "USE_EXISTING"


def test_factory_requires_three_opportunities():
    f = FactoryGenesisFeatures(
        2,.2,.9,.9,.9,5,.3,.9,2,.9,.9,.9
    )
    score, decision, failures = factory_genesis_decision(f)
    assert decision == "NO_FACTORY"
    assert "TOO_FEW_OPPORTUNITIES" in failures


def test_factory_spawn_candidate():
    f = FactoryGenesisFeatures(
        5,.2,.85,.85,.9,5,.3,.85,1.5,.85,.8,.85
    )
    score, decision, failures = factory_genesis_decision(f)
    assert score >= .72
    assert decision == "SPAWN_CANDIDATE"
    assert failures == []


def test_fit_boundaries():
    high = FactoryFit(.9,.9,.9,.9,.9)
    assert factory_fit_score(high) >= .75


def test_voi_picks_decision_sensitive_uncertainty():
    actions = [
        ResearchAction("more papers", .70,.72,.9,.9,.1,.01),
        ResearchAction("competitor census", .45,.80,.2,.9,.3,.01),
    ]
    name, score = choose_next_research(actions)
    assert name == "competitor census"
    assert score > 0


def test_log_growth_does_not_divide_by_zero():
    assert log_growth(5,0) > 0


def test_robust_zscore_requires_variance():
    assert robust_zscore(5,[1,1,1,1,1]) is None
