# Factory Lifecycle

*The complete lifecycle from idea to scale*

---

## State Machine

```text
INBOX
  ↓
DEDUPLICATED
  ↓
RESEARCHING
  ↓
SCORED
  ↓
┌───────────┬──────────┬──────────┐
│ BUILD     │ WATCH    │ REJECT   │
└────┬──────┴──────────┴──────────┘
     ↓
EXPERIMENT
     ↓
MVP
     ↓
CERTIFICATION
     ↓
PUBLISHED
     ↓
DEPLOYED
     ↓
MEASURED
     ↓
┌─────────┬────────────┬──────────┐
│ SCALE   │ ITERATE    │ KILL     │
└─────────┴────────────┴──────────┘
```

---

## Stage Definitions

### INBOX
Raw idea from any source. Not yet processed.

### DEDUPLICATED
Idea has been checked for duplicates. Signal count updated.

### RESEARCHING
Research packet being generated.

### SCORED
Idea has been scored with evidence.

### BUILD / WATCH / REJECT
Decision made based on scores.

### EXPERIMENT
Cheapest falsification experiment running.

### MVP
Minimum viable product built.

### CERTIFICATION
12-check certification suite passed.

### PUBLISHED
GitHub repository created and published.

### DEPLOYED
Product deployed to production.

### MEASURED
Product metrics being collected.

### SCALE / ITERATE / KILL
Based on metrics, product is scaled, iterated, or killed.

---

## Transitions

Every transition needs evidence:

```text
INBOX → DEDUPLICATED
  evidence: deduplication check passed

DEDUPLICATED → RESEARCHING
  evidence: research packet generation started

RESEARCHING → SCORED
  evidence: scoring completed with evidence

SCORED → BUILD
  evidence: score ≥ threshold, recommendation = BUILD

BUILD → EXPERIMENT
  evidence: experiment spec created

EXPERIMENT → MVP
  evidence: experiment passed thresholds

MVP → CERTIFICATION
  evidence: MVP built and ready

CERTIFICATION → PUBLISHED
  evidence: 12-check certification passed

PUBLISHED → DEPLOYED
  evidence: deployment successful

DEPLOYED → MEASURED
  evidence: metrics collection started

MEASURED → SCALE
  evidence: metrics show growth

MEASURED → ITERATE
  evidence: metrics show issues

MEASURED → KILL
  evidence: metrics show failure
```

---

*Factory lifecycle v1.0*
