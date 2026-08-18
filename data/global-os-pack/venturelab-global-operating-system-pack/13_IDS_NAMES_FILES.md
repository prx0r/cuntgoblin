# IDs / Names / File Conventions

## IDs

Type-prefixed UUIDv7:
- run_
- job_
- attempt_
- obs_
- opp_
- factory_
- product_
- build_
- artifact_

Human-readable slug is separate.

## Code

Python modules/functions: snake_case
Classes: PascalCase
Constants: UPPER_CASE
JSON/API keys: snake_case
URL slugs: kebab-case

## API

Version path `/v1`.
Do not encode minor versions in URLs.

## Generated software repo

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

MANIFEST is generated, never hand-maintained.
