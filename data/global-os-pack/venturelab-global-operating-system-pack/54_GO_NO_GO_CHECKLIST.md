# Autonomous GO Checklist

GO only if:
- Dell MANIFEST regenerated/current
- global DB migrated
- event append tested
- queue idempotency tested
- lease recovery tested
- global paid budget set
- one-owner routing rule enforced
- Kanban projection/reconciliation tested
- artifact store verified
- Merkle unit/integration tests pass
- release saga tested
- dry-run looks sane
- no secrets in source control
- critical chaos subset passes

Otherwise run only:
- read-only source collection
- simulation
- router shadow mode.
