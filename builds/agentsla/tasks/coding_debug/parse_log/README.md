# parse_log debug task

`src/parse_log.py` contains a log parser for the line format

    <timestamp> method=GET path=/index status=200 bytes=512 [skip=0|1]

An optional trailing `skip=N` fragment marks lines that must be excluded when
N=1 (`skip=1`) and parsed normally when N=0 (`skip=0`).

Two behaviours are wrong:

1. The trailing `skip=` fragment is handled AFTER the regex match. The regex
   anchors on `bytes=\d+$` (end of string), so any well-formed line that
   carries a trailing fragment (e.g. `... bytes=512 skip=0`) fails the regex
   and is silently DROPPED — even though the fragment says "do NOT skip".
2. When the fragment branch is reached on other inputs, its meaning is
   inverted: `skip=0` returns None instead of keeping the line.

A correct parser must:

- parse every line in `data/sample.log` that does NOT carry `skip=1`,
- drop blank lines and `skip=1` lines,
- return a `LogRecord` with numeric `status` and `bytes_` fields,
- still reject genuinely malformed lines (i.e. the fix must not weaken the
  format check by, say, ignoring all fragments or matching anything).

Inspect the source, find the root cause, and produce a minimal unified diff.

Output format: end your answer with a fenced block containing the unified
diff, e.g.

```diff
--- a/src/parse_log.py
+++ b/src/parse_log.py
@@ ...
```

The grader applies it with `patch -p1` and runs a hidden test suite.