# Workflow Graph

A WorkflowSpec is a versioned DAG.

Every node declares:
- node ID
- executor
- input schema
- output schema
- dependencies
- retry policy
- timeout
- budget
- TaskSpec/model slot if LLM-backed
- verifier
- external commit effect, if any

Executor types:
- python
- shell
- hermes
- agent_system
- http
- mcp
- human_gate
- release_transaction

## Conditions

Critical branching conditions operate on structured validated outputs, not on prose.

## Fan-out

Dynamic children inherit:
- workflow run ID
- budget envelope
- epoch/snapshot
- cancellation token
- evidence policy

## Fan-in

Aggregators start only when required child terminal conditions are explicit.
Failed/missing children remain represented; they do not silently disappear.
