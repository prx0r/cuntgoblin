# Evaluation & Certification

Nothing publishes because the producer says “done.”

## Verification order

1. schema,
2. deterministic tests,
3. domain checks,
4. adversarial cases,
5. independent semantic check where necessary,
6. packaged/deployed smoke,
7. provenance completeness.

## Certificate

```json
{
  "certificate_id":"cert_...",
  "artifact_hash":"sha256:...",
  "policy_version":"cert-v1",
  "accepted":true,
  "checks":[],
  "issued_at":"..."
}
```

## Independence

Verifier gets:
- specification,
- artifact,
- evidence,
- acceptance contract.

It does not need producer reasoning history.

## Frozen evals

Each factory maintains:
- gold passes,
- known failures,
- production regressions.

Skill/template/model upgrades rerun them.

## Failure attribution

Allow multiple plausible causes:
- MODEL_CAPABILITY
- BAD_SPEC
- MISSING_CONTEXT
- TOOL_FAILURE
- PROVIDER_FAILURE
- SOURCE_FAILURE
- VERIFIER_FALSE_NEGATIVE
- TEMPLATE_DEFECT
- ORCHESTRATION_DEFECT

This prevents HotSwap from learning the wrong lesson.
