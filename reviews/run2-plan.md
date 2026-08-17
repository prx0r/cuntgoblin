# Run 2 Plan — Proper Validation

*Date: 2026-08-18T06:45:00Z*

---

## What Went Wrong in Run 1

1. **No real validation** — Tests passed but used synthetic data
2. **No cryptographic provenance** — No content hashes, no merkle trees
3. **Too quick** — Workers generated code without real reasoning
4. **No real measurements** — No actual endpoint probing
5. **Missing MCP** — No MCP servers implemented

---

## What Run 2 Must Have

### 1. Content-Addressed Runs (from sanskritbenchy)

Every run must:
- Hash gold data
- Hash code
- Hash config
- Store: `sha256(gold ‖ code ‖ config) → out_hash`
- Log to `data/runs/`

### 2. Cryptographic Validation (from openpatala)

Every artifact must:
- Have UUIDv7 ID
- Have DigestSet (sha256 + sha512)
- Be verifiable
- Link to evidence

### 3. Real Measurements (from dell)

Every endpoint must:
- Actually call LLM APIs
- Measure real latency
- Track real costs
- Store real observations

### 4. MCP Integration

Every product must:
- Expose MCP tools
- Follow MCP protocol
- Be callable by agents

### 5. Certification (from dell)

Every MVP must:
- Pass certification checklist
- Generate JSON certificate
- Be verifiable by hermes

---

## Run 2 Process

```
1. SPECIFY (hermes reads spec)
2. VALIDATE (hermes checks requirements)
3. BUILD (hermes writes code)
4. TEST (hermes runs tests)
5. MEASURE (hermes probes endpoints)
6. CERTIFY (hermes generates certificate)
7. LOG (hermes logs to data/runs/)
```

---

## Anti-Cheat for Run 2

1. **No synthetic data** — Must use real LLM endpoints
2. **No mock measurements** — Must measure actual latency/cost
3. **No fake certificates** — Must pass actual tests
4. **Content hashes required** — Every artifact must be hashed
5. **Provenance required** — Every observation must link to evidence

---

*Run 2 plan*
