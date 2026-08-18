# Product Repo Standard

Every generated software product requires:

```text
README.md
AGENTS.md
MANIFEST.json
LICENSE
SECURITY.md
CHANGELOG.md

app/
mcp/
skills/
schemas/
tests/
docs/
scripts/
migrations/
.github/workflows/

pyproject.toml
Dockerfile
compose.yaml
.env.example
```

README:
1. purpose
2. maturity
3. quick start
4. first API call
5. first MCP call
6. architecture
7. evidence/data method
8. testing
9. deployment
10. limitations

Clean-room README execution is a release test.

MANIFEST is generated from:
- git SHA/version
- schema digests
- API route digest
- MCP tool digest
- test/certificate result
- OCI image digest
- build timestamp
