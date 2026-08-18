# HotSwap Troubleshooting Catalogue

## Identity drift
Model aliases/deprecations change.
Fix: Dell canonical model/version/endpoint aliases.

## Nested fallback explosion
Fix: one cross-model owner: HotSwap. LiteLLM/provider routing only within declared
deployment equivalence unless HotSwap explicitly delegates.

## Free quota race
Fix: transactional quota reservations before parallel work.

## Unknown quota becomes unlimited
Fix: UNKNOWN remains unknown; no completion promise.

## Token accounting differs
Fix: estimate for reservations; reconcile provider-reported usage; track estimator error.

## Hidden/reasoning tokens
Fix: store visible tokens and provider-reported billable usage separately.

## Tool support is flaky
Fix: factual advertised capability separate from measured tool-call success.

## Tool/JSON protocol variation
Fix: per-route integration tests; strict tasks exclude non-proven routes.

## Streaming differences
Fix: streaming is endpoint/route capability, not model-family assumption.

## Model switches mid-session
Fix: log fallback epoch; critical coherent sessions may pin a route until safe boundary.

## Price changes mid-task
Fix: plan pins price snapshot; actual billing reconciled; future jobs re-resolve.

## Promo expires
Fix: Dell invalidates offer; queued jobs re-plan.

## Aggregator hides provider route
Fix: choose explicit mode: delegated routing or provider-constrained reproducibility.

## Circuit breaker overreaction
Fix: breaker scoped to exact deployment/account and failure class.

## Retry amplification
Fix: one retry budget propagated down all layers.

## Cache biases benchmark
Fix: cold/warm/cache-state labels.

## Weak learning label
Fix: Hermes exit success never equals task success. Evaluator controls outcome posterior.

## Nonstationarity
Fix: route/model versions have separate posterior; supersede/decay old evidence.

## Prompt/task drift
Fix: TaskSpec version + distribution drift checks + shadow evaluation.

## Premium free capacity starvation
Fix: quota shadow prices/reserve bands.

## Multi-turn/history routing
Test MTRouter-like approaches in lab before adding history-conditioned production routing.

## Vision economics
Use modality-specific image/resolution accounting.

## Video economics
Use per-second/resolution/FPS/audio/generation-mode units; never force into text token schema.

## Privacy/retention
Policy/privacy constraints are hard route filters, not soft ranking factors.
