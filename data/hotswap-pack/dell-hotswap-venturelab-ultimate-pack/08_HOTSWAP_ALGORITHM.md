# HotSwap v1 Algorithm

## Inputs

- TaskSpec
- Dell route candidates
- configured account state
- local quota reservations
- live breaker state
- local task-cell success posterior
- optional LiteLLM live deployment health

## Step 1 — candidate universe

Ask Dell for routes satisfying factual hard requirements.

Do not ask Dell for "best" only.

Retrieve enough alternatives to compute:
- free frontier
- paid frontier
- fallback chain

## Step 2 — account readiness

Exclude:
- account not configured
- expired credentials
- manual setup not completed
- region not available
- activation conditions not met

Do NOT discard attractive unconfigured deals permanently.
Send them to Account Opportunity Queue.

## Step 3 — hard capability gates

Examples:
- context
- tools
- JSON
- output length
- automation policy
- task budget
- freshness
- endpoint circuit breaker

UNKNOWN under a hard requirement → exclude by default.

## Step 4 — quota feasibility

Reserve estimated:
- requests
- input tokens
- output tokens

against every relevant quota window.

Concurrency-safe reservation occurs BEFORE execution.

## Step 5 — success probability

For task cell C and route R:

```text
p_success =
posterior(C,R)
```

If insufficient local data:

```text
prior =
Dell task-quality evidence
× Dell evidence confidence
```

Never use context length as quality.

## Step 6 — expected completion cost

For first route i with escalation plan E:

```text
ECPS_i =
C_i
+ (1 - P_i) * E_cost
+ latency_penalty
+ quota_shadow_cost
+ uncertainty_penalty
```

For deeper chain recursively:

```text
E_k = C_k + (1-P_k) * E_{k+1}
```

This is the primary economic objective.

## Step 7 — free-first policy

If `free_policy=require`:
only free qualified routes.

If `free_policy=prefer`:
choose from qualified free frontier if one meets quality floor and quota constraints.

Paid route becomes eligible when:
- no free route meets quality floor;
- free capacity exhausted;
- release-gate policy requires stronger route;
- expected failure/rework cost makes paid route cheaper per successful task.

"Free-first" does not mean "free even if it repeatedly fails."

## Step 8 — Pareto pruning

Remove a candidate if another candidate is no worse in:
- conservative success probability
- expected cost
- reliability
- latency/throughput
- quota availability
and strictly better in at least one.

This reduces noisy model pools and aligns with LLMRouterBench's model-curation lesson.

## Step 9 — exploration

Low criticality only.

Stage 1:
Thompson sampling among near-frontier candidates.

Never explore on:
- certification
- release gates
- security review
- expensive high-impact builds

## Step 10 — fallback plan

Order:
1. same model, alternate healthy deployment/key when possible
2. comparable model in same quality tier
3. stronger escalation model
4. final emergency reliable model if policy permits

Return exact reason codes.

## Step 11 — execute

Hermes receives primary + fallback chain.
LiteLLM handles normalized provider calls and accounting.

## Step 12 — reconcile

After each request/session:
- actual tokens
- actual cost
- actual route/deployment
- latency
- rate-limit/error
- quota headers
- task evaluator result

update ledgers and outcome posterior.
