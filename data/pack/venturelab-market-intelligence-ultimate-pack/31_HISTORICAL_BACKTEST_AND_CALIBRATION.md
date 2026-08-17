# Historical Replay / Threshold Calibration

The numeric thresholds in this pack are initial operational priors.

They become credible only after replay.

## Backtest design

For each historical cutoff T:

1. hide data after T;
2. build observations/signals as known at T;
3. rank topics/opportunities;
4. advance time;
5. measure subsequent adoption/outcome proxies.

## Questions

- Did high TDS topics continue rising?
- How many were one-week attention spikes?
- Which source combinations were predictive?
- Which miners had high false-positive rates?
- Did Factory Genesis clusters actually produce repeatable products?

## Calibration

Learn:
- source reliability
- optimal windows
- thresholds
- weights

Do not optimize on all history and then report the same history as validation.

Use:
- train period
- validation period
- held-out test period

## Avoid Goodhart

Never optimize solely for:
- number of opportunities
- number of products
- GitHub stars
- model-assessed novelty

Prefer real downstream outcomes and robustness.
