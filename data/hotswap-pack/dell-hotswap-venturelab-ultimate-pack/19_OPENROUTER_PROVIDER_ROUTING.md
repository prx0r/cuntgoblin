# OpenRouter as an Optional Lower Routing Layer

OpenRouter already performs provider routing within a model.

Use it deliberately.

## If HotSwap only chooses model

Allow OpenRouter to:
- avoid recent provider outages;
- prefer low price;
- fallback provider endpoints.

## If Dell needs exact endpoint reproducibility

Constrain OpenRouter using:
- provider order/only
- quantization
- max price
- required parameters
- data collection/ZDR policy
where supported.

## Performance preferences

Dell/HotSwap may pass:
- preferred minimum throughput
- preferred maximum latency

But distinguish:
preferred performance vs hard constraints.

## Do not confuse layers

OpenRouter provider routing does not replace:
- task-specific model routing
- local free-quota allocation
- factory outcome learning

That remains HotSwap.
