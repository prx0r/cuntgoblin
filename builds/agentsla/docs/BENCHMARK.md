# AgentSLA — MVP Benchmark Report

*Date: 2026-08-17*
*Build SHA: see `data/runs/<id>/run.json` (each run records the git SHA that
produced it)*
*Model: deepseek-v4-flash via the configured OpenAI-compatible endpoint
(https://opencode.ai/zen/go/v1)*

## What was run

24-cell live benchmark (`benchmarks/bench_v1.json`): 3 task classes ×
4 architectures × 2 attempts, plus follow-up cells for the patch-apply
agentic fix. Every cell executed real model calls, was graded by
DETERMINISTIC graders (patch apply, py_compile, pytest visible+hidden,
citation/rubric checks — never an LLM grader), and wrote a per-run evidence
envelope.

## Observations (raw)

| metric | value |
|--------|-------|
| runs completed | 25 |
| successful runs | 12 |
| model calls | 167 |
| tool calls | 187 |
| evaluations | 69 |
| cost_events | 167 |
| total accounted cost | $0.0518 |
| cost basis | 100% `price_table_estimate` (provider reports `cost:"0"`) |
| evidence envelopes | 25 |

## Results by task class × architecture (n=2)

### coding.patch — fix median bug in mathlib
| architecture | succ | $/attempt | $/success | wilson_LB |
|--------------|------|-----------|-----------|-----------|
| worker_verifier | 2/2 | 0.0025 | 0.0025 | 0.342 |
| parallel_candidates_judge | 1/2 | 0.0016 | 0.0031 | 0.095 |
| planner_worker | 1/2 | 0.0013 | 0.0026 | 0.095 |
| single_agent | 1/2 | 0.0005 | 0.0010 | 0.095 |

### coding.debug — fix skip=0 handling in parse_log
| architecture | succ | $/attempt | $/success | wilson_LB |
|--------------|------|-----------|-----------|-----------|
| single_agent | 0/2 | 0.0019 | — | 0.000 |
| planner_worker | 0/2 | 0.0011 | — | 0.000 |
| parallel_candidates_judge | 0/2 | 0.0047 | — | 0.000 |
| worker_verifier | 0/2 | 0.0065 | — | 0.000 |

### research.answer — answer from local KB with citations
| architecture | succ | $/attempt | $/success | wilson_LB |
|--------------|------|-----------|-----------|-----------|
| single_agent | 2/2 | 0.0006 | 0.0006 | 0.342 |
| planner_worker | 2/2 | 0.0009 | 0.0009 | 0.342 |
| worker_verifier | 2/2 | 0.0025 | 0.0025 | 0.342 |
| parallel_candidates_judge | 1/2 | 0.0010 | 0.0019 | 0.095 |

All cells are n=2 → every success_rate is below the `min_samples=3` evidential
threshold, so AgentSLA reports `insufficient_evidence=true` and KnEE-style
consumers must NOT act on these rates as facts. The Wilson lower bound is the
honest headline (e.g. worker_verifier on research = 34% lower-bound, plenty of
room to move with more runs).

## Honest reading of the numbers

1. **research.answer works well** — strong-model + tiny local KB + citation
   rubric passes deterministically. This is the "reference-backed factual
   rubric" workload behaving as intended.

2. **coding.patch is mixed, but real** — worker_verifier went 2/2 (the only
   architecture that did), and at 2-cell resolution it is the highest-cost but
   highest-success cell. single_agent is the cheapest per attempt. With n=2,
   do not read ordering as fact.

3. **coding.debug is 0%** — and this is a *genuine* finding, not a harness
   bug: the model (deepseek-v4-flash) produces diffs whose hunk headers are
   malformed (`@@ -49,18 +50,12 @@ def parse_line...` — the function signature
   ended up inside the `@@` header), so GNU `patch -p1` rejects them
   mechanically even when the semantic fix is correct. The runner now traps
   this: an apply-validate loop copies the workspace, tries the patch, and on
   failure feeds the `patch` stderr back to the model for a corrected diff.
   Follow-up cell `agentsla-cell-c0ca6e28` confirmed the model retries but does
   not converge to a mechanically valid patch within the step budget. This is
   exactly the kind of real agentic failure AgentSLA is meant to surface.

## What this MVP proves

- The full pipeline is real: TASK DATASET → RUN MANIFEST → 4 architectures →
  RUNNER → execution trace → deterministic GRADER → COST ACCOUNTING → SLA DB
  → API + MCP, with evidence envelopes.
- Cost accounting records its basis per call; nothing is fabricated.
- SLA metrics carry sample counts + Wilson confidence; nothing claims 90% from
  9/10 (here, nothing claims anything above `min_samples`).
- Real blind-graded eval output exists (25 runs, 69 evaluations) and is
  served, not described.

## Reproduction

```bash
cd builds/agentsla
pip install -r requirements.txt
export OPENCODE_GO_BASE_URL=... OPENCODE_GO_API_KEY=...
python run_benchmark.py --bench benchmarks/bench_v1.json --live   # 24 live cells
python check.py                                                    # 6/6 gate
python run_benchmark.py --summary                                 # SLA table
python -m app.api                                                 # API :8790
python mcp/server.py                                              # MCP stdio
```
