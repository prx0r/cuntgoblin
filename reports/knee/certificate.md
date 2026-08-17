# Knee MVP — Certification Certificate

*Generated 2026-08-17T20:32:29Z by patala (kanban task t_944c3981) · build `mvp_VENT_KNEE` @ `b9f0593cfe5cb3e3e0749f67b1ed8c5b7303bc57`*

## Verdict: **CONDITIONAL PASS**

10 passed, 1 partial, 1 not implemented (MCP tools absent; content hashes certified externally but not stored by product). Core API + database MVP is real and reproducible; MCP layer is the outstanding gap.

## Checklist

| Check | Status | Evidence |
|---|---|---|
| clean_install | PASS | fresh git clone @ b9f0593 -> python3 -m venv -> pip install -r requirements.txt (rc=0) -> uvicorn boot from empty dir (no data/) -> lifespan created DB + seeded -> GET /health 200 data_source=synthetic-seed-v1; POST /knee 200 rec=deepseek-v3@0.925 cliff=0.075 |
| deterministic_fixtures | PASS | two fresh sqlite DBs seeded independently; task_observations 2560 rows byte-identical (sha256 784ff04181f6c99f11ca0f8f4b055ce99834ae6eb2336ad009f4f8193bd171e3); model_registry + knee_meta identical modulo timestamp columns only (updated_at, seeded_at); determinism flag: False |
| schema_valid | PASS | PG 18.4: 4 tables (task_observations, knee_calculations, model_registry, knee_meta), 11 indexes incl. composite ix_task_observations_task_model; column parity SQLAlchemy<->PG exact for all 4 tables (parity=True); schema.sql re-apply idempotent rc=0 |
| unit_tests | PASS | pytest tests/ : 31 passed on sqlite (1.47s, 1 deprecation warning); 31 passed on PostgreSQL knee_test (1.58s) |
| integration_tests | PASS | live uvicorn against PG knee db; 16/16 HTTP probes passed: /health, POST /knee, GET /knee/{t}, GET /knee/history/{t}, GET /knee/compare, POST /knee/batch, POST /classify, GET /models, GET /models/{id}, abstention, constraints, adversarial inputs, openapi, docs, provenance tags, root |
| provenance | PASS | knee_meta rows: data_source=synthetic-seed-v1, seed_version=synthetic-seed-v1, seeded_at=2026-08-17T20:18:58+00:00; every API payload carries meta.data_source=synthetic-seed-v1; algorithm tagged baseline-knee-v1 |
| observations_logged | PASS | PostgreSQL knee db: task_observations=2560, model_registry=8, knee_calculations=22 (persisted on every computation), knee_meta=3. Note: arch-spec universal data/runs/<run-id>/ envelope NOT produced by the app (observations live in the DB, which the knee spec explicitly allows: 'Postgres eventually; SQLite is acceptable for MVP'). Certification run log written to data/runs/ by this certifier. |
| api_contract | PASS | OpenAPI: 9 documented paths (/knee, /knee/{task_type}, /knee/history/{task_type}, /knee/batch, /knee/compare, /classify, /models, /models/{model_id}, /health); response shapes match spec PRODUCT 3 (recommended/next_cheaper/cliff/confidence/threshold/reason/meta + ModelPerformance blocks); task alias (task) supported; 422 on malformed input |
| mcp_contract | NOT IMPLEMENTED | specs/knee/architecture.md lines 841-847 require MCP tools find_cheapest_sufficient, compare_cost_quality, get_task_frontier. No MCP server/config/tools found anywhere in builds/mvp_VENT_KNEE (searched find_cheapest_sufficient|compare_cost_quality|get_task_frontier across build + profile: rc=1 no matches). This is a genuine gap vs spec and vs Run 2 plan requirement 'Every product must expose MCP tools'. |
| adversarial_tests | PASS | suite-internal: impossible threshold abstains, cost constraint abstains, dual-latency 422, unknown model 422, task-alias unknown type abstains, cached 404, batch partial failure; live adversarial probes: missing task_type 422, minimum_success>1 422, non-JSON body 422, short classify 422, unknown model filter 422 |
| documentation | PASS | README.md (quick start, endpoints, honesty notes, scope board), OPERATING-NOTES.md (layout, rules, gate), MANIFEST.json (documents + gate), db/provision.sh + db/schema.sql (idempotent), tests; DB task VERIFICATION.md attached to t_eb5f8f5b |
| content_hashes | PARTIAL | Certification snapshot computes sha256 for all 18 build files (see CERTIFICATE.json content_hashes). PRODUCT DOES NOT STORE per-artifact or per-row sha256 in schema (no hash columns) or MANIFEST.json. Run 2 plan requires DigestSet sha256+sha512; gap to close upstream (recommend adding hash columns + MANIFEST digests). |

## Content hashes (sha256, all build files @ b9f0593cfe5cb3e3e0749f67b1ed8c5b7303bc57)

```
875141023bba239027deab2d2adb05c265d8ac3ea33ab3cddcbcbd584e5e197e  ./.gitignore
4d95bbc145eb6b8ac6cc96f7c5dbe9f2bbb8c3e9a3308f59c5722a25f0d9d261  ./MANIFEST.json
762c922e07b198dd944e75b9142f1ff0d26e071c0ee19c6a855a5e760e2d7447  ./OPERATING-NOTES.md
f8681274adc1f0764e8709b4058fe68232921b409ca5be5d0855fb7fb03334d4  ./README.md
5b2c2c08ad338f2f8708376c917f47a9e25255e37fb74d88274163350faff591  ./app/__init__.py
eaa71c0fd58784b12cd095801a167cc3479346e41b472855481e9b09980fbd37  ./app/api.py
76fad011095e2857906d65a433772dcfd68b94ebda1b63732072f2487f95b36d  ./app/classifier.py
3b06895e5f8b944ac16cd2c769c65e687676a94bdfa828a79a340f1af50b3c26  ./app/config.py
8ef3f26e1e89d4bc8c29092af460f051531910a72d4bb02ae4296c173d208161  ./app/db.py
477d34712a9fc7a873e0fcb10e86743ee2f58d6abbebfa3bc7c1fc7056445fff  ./app/knee_algorithm.py
3665278093579fa1583c23fbc798345ab7e2de8104ff0afab2a58a85ed24e733  ./app/schemas.py
3b6b8cea348a4d1399b298aa208d08b0d92f993277fffbb5e90a57e5c3479ab5  ./app/seed.py
5ce2c400a392713500eb7e4cc2ea8c247e14b0a20005b356fa2b21f7799c7c6c  ./db/provision.sh
bec458d884c2b3b3536020c8f33cdec687961589e3fb79c0cdf236045e8fbe6f  ./db/schema.sql
97de7d4564ad9a67422638976b8d2b7dd84e66601b610c6d123e5f5780658ffb  ./requirements.txt
6ea76187b8784f19b2c3cb42b6cf41b5d97bff7df0f9de7c8836d5af701a5d86  ./tests/conftest.py
f38b906468e028e53861f4f53ca37a6d18955843571287a74525b740aeb432e6  ./tests/test_algorithm.py
177086ee0ba9c09aa37168a577ba3f3b0b681d70ebf6a7324f3745ea66fa681b  ./tests/test_api.py
```

## Evidence

- pytest: 31 passed on sqlite; 31 passed on PostgreSQL (`knee_test`)
- live integration: 16/16 HTTP probes passed against uvicorn + PostgreSQL
- PG rows: task_observations=2560, model_registry=8, knee_calculations=22, knee_meta=3
- schema: 4 tables, 11 indexes, column parity SQLAlchemy↔PG exact, idempotent schema.sql
- fixture determinism: task_observations byte-identical across fresh seeds
- run log: `data/runs/knee-cert-v1-20260817T203229Z/`

## Gaps (honest, not hidden)

1. **MCP contract NOT IMPLEMENTED** — spec requires `find_cheapest_sufficient`,
   `compare_cost_quality`, `get_task_frontier`; no MCP server exists in the build.
   Required by Run 2 plan ("every product must expose MCP tools").
2. **Content hashes not stored by product** — no sha256 columns in schema, none in
   MANIFEST.json. This cert computes them externally; upstream should store digests.
3. **data/runs/ envelope** — app does not write run archives; observations live in the
   DB (allowed by spec). This certification writes its own evidence under
   `data/runs/knee-cert-v1-20260817T203229Z/`.

---
*Certificate format: venturelab/certificate/1. Machine-generated from real tool output; NOT a
markdown-only claim. Re-run `pytest` and `integration_probe.py` to re-verify.*
