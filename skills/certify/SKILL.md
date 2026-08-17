---
name: certify
description: "Certify MVPs pass production readiness checks."
version: 1.0.0
date: 2026-08-18
author: venturelab
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Certify, Validate, Production]
    related_skills: [factory-build, factory-verify]
---

# Certify Skill

You certify MVPs pass production readiness checks.

## Certification Checklist

1. Clean install — works from empty database
2. Deterministic fixtures — seed data is reproducible
3. Schema valid — tables/indexes exist
4. Unit tests pass — pytest returns 0
5. Integration tests — API endpoints work
6. Provenance — all data has content hashes
7. Observations logged — data/runs/ has entries
8. API contract — OpenAPI schema valid
9. Documentation — README.md exists
10. Certificate — JSON certificate generated

## Certificate Format

```json
{
  "product": "knee",
  "certified_at": "2026-08-18T06:00:00Z",
  "tests_passed": true,
  "schema_valid": true,
  "api_contract": true,
  "provenance": true,
  "documentation": true,
  "certificate": "PASS"
}
```

## Anti-cheat

Certificate only valid if tests actually pass, API actually responds, code actually runs.
