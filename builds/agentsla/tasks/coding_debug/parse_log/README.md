# parse_log debug task

`src/parse_log.py` contains a log parser for the line format

    <timestamp> method=GET path=/index status=200 bytes=512 [skip=0|1]

Two behaviours are wrong:

1. Lines with a trailing `skip=0` fragment (a legal server-variant log line
   meaning "do NOT skip this entry") are dropped instead of parsed.
2. Lines with `skip=1` are dropped, which is correct, but the implementation
   is fragile: the intent of the `skip=` marker is inverted in the trailing
   fragment branch, so `skip=0` lines disappear from the parsed output.

A correct parser must:

- parse every line in `data/sample.log` that does NOT carry `skip=1`,
- drop blank lines and `skip=1` lines,
- return a `LogRecord` with the numeric `status` and `bytes_` fields.

Inspect the source, find the root cause, and produce a minimal unified diff.

Output format: end your answer with a fenced block containing the unified
diff, e.g.

```diff
--- a/src/parse_log.py
+++ b/src/parse_log.py
@@ ...
```

The grader applies it with `patch -p1` and runs a hidden test suite.