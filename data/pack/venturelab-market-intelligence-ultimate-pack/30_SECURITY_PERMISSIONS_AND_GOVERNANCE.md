# Permissions / Governance

Market Intelligence is mostly read-only, but Factory Genesis can eventually cause
large downstream actions. Keep permission boundaries.

## Safe autonomous
- public-source reads
- normalization
- scoring
- research tasks
- local experiments
- branch creation
- deterministic tests

## Require explicit policy/budget
- paid data source activation
- cloud spend
- mass outreach
- buying domains
- publishing legal/regulatory claims as advice
- deploying high-cost infrastructure
- merging security-sensitive changes

## Source legality/terms

Each adapter manifest stores:
- license/terms URL
- allowed redistribution notes
- attribution requirements
- whether raw payload can be republished

A public API does not automatically mean unrestricted redistribution.

## Sensitive data

Do not ingest personal data merely because a public endpoint exposes it.
The Market Oracle should focus on aggregated/entity-level market signals.
