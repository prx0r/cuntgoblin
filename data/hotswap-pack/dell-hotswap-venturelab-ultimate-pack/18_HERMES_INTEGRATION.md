# Hermes Integration

Hermes can override model/provider per invocation and already supports fallback chains.

## Factory runner

```text
TaskSpec
  ↓
hotswap resolve
  ↓
ExecutionPlan
  ↓
generate ephemeral Hermes profile/config
  ↓
hermes chat
```

## Main model

Set selected model for this task only.

Do NOT globally mutate the default model when running parallel factory workers.

Use per-task profile or CLI override.

## Fallback

HotSwap generates:

```yaml
fallback_providers:
  - provider: ...
    model: ...
```

from `ExecutionPlan.fallbacks`.

Set Hermes `agent.api_max_retries` according to error/failover policy.

For a factory that values fast failover, a lower retry count is preferable to repeatedly
hitting a rate-limited provider.

## Auxiliary slots

Use HotSwap task policies for:
- compression
- web extraction
- skill search
- MCP tool routing
- vision

These are often excellent free-first targets and should not inherit the expensive
main model unnecessarily.

## Session continuity

Prefer Hermes native fallback for model changes mid-session so context and tool history
remain intact.

## Execution wrapper

Add:

```text
factory/runtime/hermes_runner.py
```

It:
1. requests plan;
2. materializes ephemeral profile;
3. launches Hermes;
4. captures actual model/provider/fallback event;
5. invokes task evaluator;
6. records outcome.
