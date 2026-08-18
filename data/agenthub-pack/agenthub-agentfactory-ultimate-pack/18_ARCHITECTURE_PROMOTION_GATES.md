# Promoting an Experimental Build Into a Reusable AgentSystem

## Experimental build

Can exist after one solution/task.

## Reusable system candidate

Require all:

1. passes its target benchmark suite;
2. improves over a simple baseline on at least one target objective;
3. improvement survives repeated trials;
4. architecture effect is not explained only by a stronger model;
5. clean install/doctor/run works;
6. manifest accurately describes topology;
7. no zero-tolerance security/truth failure.

## Verified AgentSystem

Initial promotion prior:

- >=3 distinct benchmark tasks or solution instances;
- >=2 task categories OR explicit narrow-domain designation;
- >=2 independent repeated runs per key task;
- success lower bound above configured floor;
- cost/complexity recorded;
- at least one ablation showing a claimed structural mechanism matters;
- lineage complete;
- pinned build reproducible.

If architecture is intentionally narrow, breadth gate may be replaced by:
`domain-specific` label.

## Promotion does NOT require popularity.

Popularity is downstream community metadata.
