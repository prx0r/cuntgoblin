# Failure Injection Harness

Architecture quality is partly what happens AFTER something fails.

## Failure modes

### TOOL_DOWN
Tool/endpoint returns failure.

### WORKER_CRASH
Worker disappears mid-task.

### BAD_DELEGATION
Subtask goes to wrong role.

### STALE_ARTIFACT
Worker receives old dependency output.

### CORRUPT_ARTIFACT
Artifact schema/hash fails.

### LATENT_SEMANTIC_ERROR
Artifact looks structurally valid but is wrong.

### CONTEXT_LOSS
Critical upstream information omitted.

### RATE_LIMIT
Model/provider temporarily unavailable.

## Injection object

```yaml
at:
  node: worker-2
  event: after_first_tool
type: TOOL_DOWN
recoverable: true
seed: 42
```

## Metrics

```text
detection_rate
recovery_rate
mean_time_to_detection
mean_time_to_recovery
cascade_radius
quality_after_recovery
extra_cost
```

## Trusted-state caveat

If benchmark gives explicit fault labels/trusted checkpoints, report that separately.

Do not imply autonomous detection if the architecture was handed the error location.
