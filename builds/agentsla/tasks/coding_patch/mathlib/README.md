# mathlib fix task

Fix the buggy function in `src/mathlib.py`.

Acceptance criteria (what the grader checks):

1. All tests in `tests/` pass.
2. A hidden edge-case test suite passes:
   - `median([]) is None`
   - `median` of an even-length list with floats, e.g. `[0.5, 2.5]` -> 1.5,
   - `median` of negative values, e.g. `[-5, -1, -2]` -> -2.
3. The patch applies cleanly (`patch -p1`).
4. The patch does **not** modify anything under `tests/`.

Inspect the code, find the bug, and produce a minimal unified diff.

Output format: end your answer with a fenced block containing the unified diff,
for example:

```diff
--- a/src/mathlib.py
+++ b/src/mathlib.py
@@ -17,7 +17,7 @@
-    return ordered[mid - 1] + ordered[mid] / 2.0
+    return (ordered[mid - 1] + ordered[mid]) / 2.0
```