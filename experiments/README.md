# Experiments

*Internal experiments on the venture lab infrastructure*

---

## Structure

```text
experiments/
├── scoring/           # Scoring determinism tests
├── architecture/      # Architecture pattern tests
├── builds/            # Build process tests
└── README.md          # This file
```

## Running Experiments

```bash
# Run scoring determinism test
python3 experiments/scoring/determinism_test.py

# Run architecture pattern test
python3 experiments/architecture/pattern_test.py

# Run build process test
python3 experiments/builds/build_test.py
```

## Logging

All experiments log to:
- `data/runs/experiments.jsonl`
- `experiments/{type}/results.json`

## Anti-Cheat

**"Nothing written in markdown counts as evidence."**

All experiment results must be:
- Machine-produced
- Content-addressed
- Timestamped
- Reproducible

---

*Experiments v1.0*
