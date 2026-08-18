# Factory Plugin Contract

No factory gets its own mini-platform.

```python
class FactoryPlugin(Protocol):
    factory_type: str
    def discover(ctx): ...
    def research(ctx, opportunity): ...
    def plan(ctx, opportunity, evidence): ...
    def build(ctx, plan): ...
    def verify(ctx, plan, artifacts): ...
    def publish(ctx, certificate): ...
    def observe(ctx, publication): ...
```

Shared context exposes:
- store,
- artifacts,
- evidence,
- scheduler,
- Hermes,
- HotSwap,
- verifiers,
- sources,
- publishers.

Factory manifest example:

```yaml
type: connector
version: 1
build:
  max_parallelism: 4
  default_budget_usd: 1.00
verification:
  required: [schema, unit, integration]
publication:
  human_approval: true
```
