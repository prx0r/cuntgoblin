# Architecture Lineage

A fork is not just a Git diff.

Record a semantic architecture diff.

Example:

```yaml
parent: venturelab-factory@build17

mutations:
  - op: CHANGE_PARALLELISM
    path: topology.worker_pool.max
    before: 5
    after: 8

  - op: ADD_VERIFIER
    node: adversarial-reviewer

  - op: CHANGE_MODEL_SLOT_POLICY
    slot: worker
    before:
      quality_floor: .76
    after:
      quality_floor: .72
      free_policy: prefer
```

This enables:
- architecture genealogy
- mutation-performance studies
- reusable pattern extraction
- community forks
