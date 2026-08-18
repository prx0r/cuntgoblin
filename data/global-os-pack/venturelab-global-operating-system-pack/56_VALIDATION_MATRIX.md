# Validation Matrix

## Manager
MGR-001 duplicate trigger creates one Run
MGR-002 duplicate logical Job blocked
MGR-003 expired lease recoverable
MGR-004 concurrent workers never lease same Job
MGR-005 illegal transition rejected
MGR-006 nonretryable error not looped
MGR-007 budget reservation prevents overspend
MGR-008 catch-up deterministic

## Graph
GR-001 cycle rejected
GR-002 missing node/dependency rejected
GR-003 fan-in waits for declared requirements
GR-004 critical conditions use structured fields

## Integrity
INT-001 artifact hash
INT-002 canonical JSON hash
INT-003 Merkle order sensitivity
INT-004 inclusion proof
INT-005 mutated event changes root
INT-006 checkpoint chain continuity

## Release
REL-001 no certified->released shortcut
REL-002 remote SHA verified
REL-003 CI required
REL-004 production smoke required
REL-005 partial external effects reconcile

## Dell
DELL-001 manifest SHA current
DELL-002 critical mutation 100%
DELL-003 certificate digest linked

## HotSwap
HS-001 one cross-model routing owner
HS-002 bounded propagated retry budget
HS-003 actual route reconciled
HS-004 quota reservation concurrency safe

## Factory
FAC-001 Completion Contract exists
FAC-002 README clean-room
FAC-003 output schemas valid
FAC-004 PARTIAL never auto-publishes

## AgentHub
AH-001 pinned ArchitectureBuild
AH-002 benchmark model mode recorded
AH-003 one-off build not auto-promoted

## Paper
PAPER-001 pinned source repo
PAPER-002 sandboxed reproduction
PAPER-003 reproduction state explicit
PAPER-004 reconstructed code not called faithful without evidence
