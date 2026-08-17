# Validation and Certification

## Source gates

SRC-001 connector failure produces UNKNOWN/DEGRADED, not zero
SRC-002 raw artifact is content-addressed
SRC-003 source family preserved through aggregators
SRC-004 observation has time window
SRC-005 source terms/license note recorded
SRC-006 stale observation cannot masquerade as current

## Topic gates

TOP-001 two independent source families unless official event exception
TOP-002 growth near zero baseline cannot explode via naive percent change
TOP-003 source breadth counts families not endpoints
TOP-004 TDS deterministic for fixed signals
TOP-005 missing signal cannot silently become .5

## Opportunity gates

OPP-001 Opportunity != SolutionHypothesis
OPP-002 score has evidence IDs
OPP-003 mandatory UNKNOWN => RESEARCH, not BUILD
OPP-004 one attention source cannot create BUILD
OPP-005 causal wording rejected for correlational join
OPP-006 source leave-one-out sensitivity computed for join

## Factory Genesis gates

GEN-001 fewer than 3 opportunities cannot spawn normal factory
GEN-002 existing FactoryFit >= .75 blocks new factory
GEN-003 fit .60-.75 chooses extension
GEN-004 evidence confidence below .70 blocks spawn
GEN-005 <3 source families blocks spawn
GEN-006 repeatability <.65 blocks spawn
GEN-007 shared infra reuse <.60 blocks spawn
GEN-008 FGS .58-.72 => experiment only
GEN-009 FGS >=.72 + gates => candidate, not ACTIVE
GEN-010 activation requires reference product + completion contract

## Cross-oracle gates

JOIN-001 invalid dimension mapping blocks join
JOIN-002 non-overlapping windows blocked unless lag declared
JOIN-003 semantic plausibility <.70 blocked
JOIN-004 duplicate parent source not independent
JOIN-005 random high correlation cannot bypass rule template
JOIN-006 source failure cannot create shortage/gap

## Outcome gates

OUT-001 stars != users
OUT-002 downloads != unique users
OUT-003 product telemetry is timestamped
OUT-004 negative outcomes update factory assumptions

## Evolution gates

EVO-001 provenance schema immutable
EVO-002 zero-tolerance gates cannot be mutated
EVO-003 candidate evaluated before promotion
EVO-004 lineage recorded
EVO-005 shadow/offline test before production
EVO-006 evaluator evolution only at epoch boundary
