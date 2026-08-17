"""parse_log.py — parse a simple access log into structured records.

Task: the parser mis-handles one class of valid log lines. Fix it so every
record in data/sample.log parses correctly (including the field the buggy
code drops), and the hidden edge cases pass. Do NOT modify anything under
tests/ (there is no visible tests dir; the grader supplies its own).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Line format:
#   2026-08-01T12:00:00Z method=GET path=/index status=200 bytes=512
#   2026-08-01T12:00:04Z method=GET path=/index status=200 bytes=512 skip=0
# The trailing `skip=N` fragment marks lines that must be ignored when N=1.
_LINE_RE = re.compile(
    r"^(?P<ts>\S+)\s+"
    r"method=(?P<method>\S+)\s+"
    r"path=(?P<path>\S+)\s+"
    r"status=(?P<status>\d+)\s+"
    r"bytes=(?P<bytes>\d+)$"
)


@dataclass
class LogRecord:
    ts: str
    method: str
    path: str
    status: int
    bytes_: int


def parse_line(line: str) -> LogRecord | None:
    """Parse one log line; return None for blank lines and `skip=1` lines.

    Correct behaviour:
      - blank lines            -> None
      - trailing `skip=0`      -> fragment stripped, line parsed normally
      - trailing `skip=1`      -> None (line marked for exclusion)
      - lines without fragment -> parsed normally

    BUG (current code): the trailing `skip=` fragment is handled AFTER the
    regex match. Because _LINE_RE requires `bytes=\d+$` (end-of-string), any
    line carrying a trailing fragment fails the match and is silently dropped,
    so legitimate `skip=0` lines disappear; and when the branch is reached on
    other inputs its skip semantics are inverted (`skip=0` -> None).
    """
    stripped = line.strip()
    if not stripped:
        return None
    m = _LINE_RE.match(stripped)
    if m is None:
        return None
    # BUG: trailing fragment handled too late (the regex already failed for
    # "bytes=512 skip=0" because of the $ anchor) AND the meaning is inverted:
    # a skip=0 fragment makes the line disappear even though it means
    # "do NOT skip".
    if "skip=" in stripped:
        trailing = stripped.split("skip=", 1)[1]
        if trailing == "0":
            return None  # ← wrong: skip=0 means "do NOT skip"
    return LogRecord(
        ts=m.group("ts"),
        method=m.group("method"),
        path=m.group("path"),
        status=int(m.group("status")),
        bytes_=int(m.group("bytes")),
    )


def parse_file(path: str) -> list[LogRecord]:
    records: list[LogRecord] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            rec = parse_line(line)
            if rec is not None:
                records.append(rec)
    return records