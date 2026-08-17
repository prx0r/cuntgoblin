# Snatchable Patterns from Cloned Repos

*What we can reuse without complete rebuild*

---

## From dell (LLM Deals)

### 1. Certification Pattern
Location: `app/certify.py`
- 12-check certification suite
- Content-addressed certificates
- JSON certificate format
- **Already integrated into Knee MVP**

### 2. Canonical Database
Location: `app/canonical_db.py`
- Content-addressed storage
- SQLite with WAL mode
- Transaction management
- **Already integrated into Knee MVP**

### 3. Adapter Contract
Location: `app/adapter_contract.py`
- Standardized adapter interface
- Consistent data extraction
- **Use for new products**

### 4. Oracle Identity
Location: `app/oracle_identity.py`
- ModelIdentity, EndpointIdentity, OfferIdentity
- Content-addressed identity system
- **Use for product identification**

---

## From agentic-infra

### 1. Run Recorder
Location: `pipeline/run_recorder.py`
- Content-addressed runs
- sha256(gold ‖ code ‖ config) → out_hash
- Nanopublication: {assertion, evidence, provenance}
- **Use for all experiments**

### 2. Trace System
Location: `agent/trace.py`
- Centralized run/experiment trace
- Query with: `python3 agent/trace.py --recent`
- **Use for logging**

### 3. Audit System
Location: `agent/audit.py`
- Golden-file audit
- Recomputes on fixed gold
- Fails on mismatch
- **Use for verification**

### 4. Objective Scoring
Location: `pipeline/objective.py`
- Weighted multi-axis scoring
- Pick next checkpoint by value/cost
- **Use for prioritization**

### 5. Checkpoint DAG
Location: `pipeline/checkpoint.py`
- Vision → checkpoint DAG
- Deterministic gates
- **Use for goal tracking**

---

## From moltwork-research

### 1. Exception-Driven Payment Gating
From: a2a-x402
```python
raise x402PaymentRequiredException(price, address, resource)
```
Middleware handles payment. Agent never touches mechanics.

### 2. Executor Middleware Wrapping
From: a2a-x402, lucid-agents
```python
x402ServerExecutor(baseExecutor)
```
Cross-cutting concerns as decorators.

### 3. Single Definition → Multiple Projections
From: lucid-agents
One typed entrypoint → schemas + routes + OpenAPI + MCP tools.
Schema IS the source of truth.

### 4. Trust Level Taxonomy
From: internet-court-skill
Three levels: Basic → Guarded → Adjudicated.
Force honest disclosure.

### 5. Append-Only Receipts
From: a2a-x402
Receipts array never replaces, only appends.
Complete audit trail.

---

## From sanskritbenchy

### 1. Hypothesis Lab
Location: `pipeline/hypothesis_lab.py`
- Open-ended exploration loop
- Observer → reason → hypothesize → test → keep/discard
- Judge's reasoning drives next hypotheses
- **Use for venture exploration**

### 2. Checkpoint DAG
Location: `pipeline/checkpoint.py`
- Vision → checkpoint decomposition
- Each checkpoint has gate
- **Use for goal tracking**

### 3. Objective Scoring
Location: `pipeline/objective.py`
- Weighted multi-axis scoring
- Pick next checkpoint by value/cost
- **Use for prioritization**

---

## From engram

### 1. Learning System
- Spaced repetition (FSRS-4.5)
- Blind assessor
- Concept maps
- **Use for knowledge retention**

### 2. Cross-Platform Skills
- Works on Claude Code, OpenCode, Hermes, etc.
- Same state folder across platforms
- **Use for skill portability**

---

## From fuck-off

### 1. Coherence Audit
Location: `COHERENCE-AUDIT.md`
- System coherence checking
- Drift detection
- **Use for quality assurance**

### 2. Drift Audit
Location: `DRIFT-AUDIT.md`
- Track system drift over time
- **Use for maintenance**

---

## From smellycock

### 1. Object Model
Location: `OBJECT-MODEL.md`
- Canonical entity definitions
- **Use for data modeling**

### 2. Check System
Location: `check.py`
- Manifest validation
- Reference checking
- **Use for validation**

---

## Priority Snatches

### Immediate (already done)
1. ✅ Certification pattern (dell)
2. ✅ Content hashing (agentic-infra)
3. ✅ MCP server pattern

### Next
1. Run Recorder (agentic-infra)
2. Trace System (agentic-infra)
3. Adapter Contract (dell)
4. Oracle Identity (dell)

### Later
1. Exception-Driven Payment Gating (moltwork)
2. Hypothesis Lab (sanskritbenchy)
3. Learning System (engram)

---

*Snatchable patterns v1.0*
