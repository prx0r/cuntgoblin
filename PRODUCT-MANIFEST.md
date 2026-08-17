# Product Manifest

*Machine-readable product specification*

---

## Schema

```yaml
# factory.yaml

product:
  id: mcptruth
  name: MCPTruth
  stage: mvp

idea:
  source: idea_mcp_truth

archetype:
  data-oracle-v2

repository:
  provider: github
  visibility: public

runtime:
  language: python
  api: fastapi
  database: sqlite
  deploy: cloudflare-container

interfaces:
  rest: true
  mcp: true
  cli: false

docs:
  required:
    - README
    - AGENTS
    - ARCHITECTURE
    - TESTING

tests:
  certification: mvp-v1

deployment:
  auto: true

portfolio:
  publish: true
```

---

## Usage

The factory reads `factory.yaml` to understand:
- What to build
- How to build it
- Where to deploy it
- What tests to run
- What docs to generate

---

## Validation

Before building, validate:

```bash
python3 -c "
import yaml
with open('factory.yaml') as f:
    config = yaml.safe_load(f)
print('Valid:', bool(config))
"
```

---

*Product manifest v1.0*
