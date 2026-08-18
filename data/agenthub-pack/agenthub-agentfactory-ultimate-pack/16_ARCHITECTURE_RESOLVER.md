# Architecture Resolver

## Hard constraints first

Examples:
- persistent state required
- browser required
- deterministic verifier integration required
- shell sandbox required
- parallel execution required

UNKNOWN does not satisfy a hard requirement.

## Fit dimensions

```text
capability_fit      .25
topology_fit        .20
state_fit           .15
verification_fit    .15
runtime_fit         .10
benchmark_fit       .10
economics_fit       .05
```

Initial decisions:

```text
best_fit >= .78
→ REUSE

.62 <= best_fit < .78
→ FORK_OR_COMPOSE

best_fit < .62
→ SYNTHESIZE_EXPERIMENTAL_BUILD
```

A low fit does NOT immediately create a reusable AgentSystem.

It creates an experimental ArchitectureBuild candidate.

## Benchmark-aware fit

Architecture claims may come from:
- declared manifest
- observed doctor
- benchmark evidence

For high-impact resolution, benchmark evidence outranks self-description.
