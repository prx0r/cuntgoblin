# Registry Model

## Tables / objects

- systems
- builds
- patterns
- build_patterns
- benchmark_suites
- assessments
- lineages
- installations
- runs
- popularity_events
- certifications

## Identity

Never key benchmark results by repo name only.

Use build ID derived from:
- system ID
- source SHA
- manifest digest
- runtime adapter version
- environment/build digest
- model policy digest

## Epistemic states

Use:
- KNOWN
- UNKNOWN
- ABSENT
- NOT_OBSERVED
- NOT_APPLICABLE
- STALE
- CONFLICTED
- UNAVAILABLE

Missing README text is not ABSENT capability.
