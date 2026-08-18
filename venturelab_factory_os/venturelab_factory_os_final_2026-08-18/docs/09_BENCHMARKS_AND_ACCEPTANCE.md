# Benchmarks

## OS

- dependencies prevent premature readiness
- atomic claim admits one winner
- stale lease reclaim works
- retry limit works
- mutated ledger event breaks verification
- Merkle inclusion valid/mutated invalid
- manifest versions immutable
- negative-net-value work can be withheld
- opportunity-cost estimate uses actual ready set
- exploration bonus shrinks with sample count
- mandatory teams block publish when failing
- unknown commerce fees => unknown margin

## Every factory type

Must provide:
- tiny deterministic fixture
- expected WorkGraph
- expected artifacts
- expected gates
- maximum fixture cost
- failure fixture

A factory is CANDIDATE until its fixture passes CI.
