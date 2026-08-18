# Router Algorithm Adapter

External algorithms are wrapped behind one contract:

```python
class RouterAlgorithm:
    id: str
    version: str

    def fit(self, training_records, model_pool): ...
    def route(self, request_features, model_pool): ...
    def explain(self, decision): ...
```

Canonical evaluation compares against:
1. best fixed single model;
2. cheapest sufficient;
3. deterministic HotSwap ECPS;
4. task-cell Bayesian HotSwap;
5. Oracle upper bound when complete labels exist.

Training/evaluation records include:
- TaskSpec/version
- model/route
- quality outcome
- cost
- latency
- availability
- timestamp
- selection propensity if exploration occurred.

Router complexity itself is a cost/maintenance dimension.
