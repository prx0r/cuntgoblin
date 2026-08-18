# Future Router Evolution

After enough outcomes, the factory can evolve HotSwap itself.

Mutable:
- task cell partition
- candidate-pool policy
- quota shadow-price policy
- quality floors within governance bounds
- retry policy
- bandit exploration
- learned features
- fallback ordering

Immutable:
- hard task constraints
- evidence semantics
- credential boundaries
- outcome history
- release safety floor

Use historical replay + shadow deployment before promotion.

The router is one of the cleanest parts of VentureLab to evolve because its fitness
can be measured in:
- cost per success
- quality floor violations
- latency
- quota waste
- release defects.
