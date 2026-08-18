# HotSwap Integration

Architecture search and model routing are related but must be experimentally separable.

## Every node/role declares ModelSlot requirements

```yaml
model_slot:
  task_kind: coding_patch
  difficulty: hard
  quality_floor: .80
  free_policy: prefer
  tools: required
```

HotSwap chooses the current economic route.

## Benchmark modes

### Frozen-model architecture benchmark

All comparable nodes use fixed models/model families.

Goal:
isolate architecture.

### Frozen-policy benchmark

All architectures use identical HotSwap policy version.

Goal:
compare architectures under realistic dynamic routing.

### Production benchmark

Each architecture may have specialized slot policies.

Goal:
measure deployable system value.

Store which mode was used.
