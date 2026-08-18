# ArchitectureNeed

Solution Lab should not ask:
"make a multi-agent system."

It produces requirements.

Example:

```yaml
need_id: ...
solution_id: ...

task_profile:
  dominant_tasks:
    - coding_patch
    - research_synthesis
  horizon: long
  parallelizable: true

requirements:
  persistent_state: true
  independent_verification: true
  resumable: true
  tool_use: required
  max_parallel_workers: 6

quality:
  success_floor: .80
  evidence_required: true

economics:
  cost_sensitive: true
  free_first: true

security:
  filesystem_write: required
  shell: required
  network: restricted
```

Resolver compares this object to verified architecture capabilities.
