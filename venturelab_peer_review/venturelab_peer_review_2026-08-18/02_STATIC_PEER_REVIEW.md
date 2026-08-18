# Static Peer Review

## Strong parts

### HotSwap

The router has:
- hard exclusions,
- quota feasibility,
- posterior mean/lower-bound behavior,
- Thompson exploration restricted by criticality,
- free-quota shadow cost,
- reliability penalty,
- expected completion cost,
- Pareto dominance,
- quality floors,
- fallback ordering,
- route outcome updates.

Preserve it.

### Market algorithms

The market module contains mechanisms that actively reduce bullshit:
- source breadth gates,
- minimum coverage,
- geometric aggregation,
- mandatory-unknown blocking,
- factory reuse/genesis gates,
- value-of-information research selection.

These should become policy used by the live workflow.

### AgentHub resolver

REUSE → FORK_OR_COMPOSE → SYNTHESIZE is strategically sound. Its fit values need to become empirically grounded through eval outcomes.

## Weak parts

### Count-based research

Search result count is not:
- novelty,
- market demand,
- feasibility,
- adoption,
- research validity.

An API/search failure must be UNKNOWN, never “zero competitors.”

### Hard-coded business evidence

Fixed defaults for pain, willingness-to-pay, moat or strategic fit create precise-looking scores without evidence.

Required semantic rule:

```text
unknown != neutral
unknown => uncertainty + decision-sensitive research action
```

### Builder naming

Current `MVPBuilder` copies a template and substitutes placeholders. That is a useful template instantiator, but it is not yet an autonomous build loop.

### Global OS naming

The reviewed `go.py` is a self-check script and imports absent siblings. Implement durable scheduling first; call it an OS later if deserved.

## Highest-level defect

Truth is duplicated across JSONL, SQLite, filesystem artifacts, Hermes Kanban and docs. Pick one canonical application store and make everything else a projection/adapter.
