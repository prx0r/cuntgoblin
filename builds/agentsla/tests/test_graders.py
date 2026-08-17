"""Deterministic grader tests — the anti-LLM-judge guarantee."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.fake import MATHLIB_FIX, PARSE_LOG_FIX, RESEARCH_PERFECT  # noqa: E402
from app.grader import (  # noqa: E402
    apply_unified_diff,
    extract_diff_block,
    extract_citations,
    grade_coding,
    grade_research,
    normalize_answer,
)

TASKS = Path(__file__).resolve().parent.parent / "tasks"


def test_extract_diff_block():
    text = "some prose\n```diff\n--- a/x\n+++ b/x\n-1\n+2\n```\ntail"
    block = extract_diff_block(text)
    assert block and "+++ b/x" in block


def test_extract_diff_block_none():
    assert extract_diff_block("no block here") is None


def test_normalize_answer():
    assert normalize_answer("Alpha, 1998!") == "alpha 1998"


def test_extract_citations():
    assert extract_citations("use F01 and F05 here") == ["F01", "F05"]
    assert extract_citations("no cites") == []


def test_mathlib_good_patch_passes():
    results = grade_coding(TASKS / "coding_patch" / "mathlib", MATHLIB_FIX)
    assert all(r.passed for r in results), [(r.evaluator, r.detail) for r in results if not r.passed]


def test_mathlib_wrong_semantics_fails():
    wrong = """--- a/src/mathlib.py
+++ b/src/mathlib.py
@@ -17,7 +17,7 @@
-    return ordered[mid - 1] + ordered[mid] / 2.0
+    return 0.0
"""
    results = grade_coding(TASKS / "coding_patch" / "mathlib", wrong)
    assert not all(r.passed for r in results)


def test_forbidden_test_modification_fails():
    evil = """--- a/tests/test_mathlib.py
+++ b/tests/test_mathlib.py
@@ -10,7 +10,7 @@
-    assert math.isclose(median([4, 1, 3, 2]), 2.5, abs_tol=1e-9)
+    assert True
"""
    results = grade_coding(TASKS / "coding_patch" / "mathlib", evil)
    assert not all(r.passed for r in results)
    assert any(r.evaluator == "graders/diff-scope-v1" and not r.passed for r in results)


def test_non_applying_patch_fails():
    garbage = "--- a/src/mathlib.py\n+++ b/nonexistent.py\n@@ -1 +1 @@\n-nope\n+flat\n"
    results = grade_coding(TASKS / "coding_patch" / "mathlib", garbage)
    assert not all(r.passed for r in results)
    assert any(r.evaluator == "graders/patch-apply-v1" and not r.passed for r in results)


def test_apply_unified_diff_roundtrip(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    target = src_dir / "mathlib.py"
    target.write_text(
        (TASKS / "coding_patch" / "mathlib" / "src" / "mathlib.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    ok, msg = apply_unified_diff(tmp_path, MATHLIB_FIX)
    assert ok, msg
    assert "return (ordered[mid - 1] + ordered[mid]) / 2.0" in target.read_text(encoding="utf-8")


def test_parse_log_good_patch_passes():
    results = grade_coding(TASKS / "coding_debug" / "parse_log", PARSE_LOG_FIX)
    assert all(r.passed for r in results), [(r.evaluator, r.detail) for r in results if not r.passed]


def test_parse_log_bad_patch_fails():
    bad = """--- a/src/parse_log.py
+++ b/src/parse_log.py
@@ -38,10 +38,10 @@
-    if "skip=" in stripped:
-        trailing = stripped.split("skip=", 1)[1]
-        if trailing == "0":
-            return None
+    if "skip=" in stripped:
+        return None
"""
    results = grade_coding(TASKS / "coding_debug" / "parse_log", bad)
    assert not all(r.passed for r in results)


def test_grade_research_perfect_passes():
    results = grade_research(RESEARCH_PERFECT, TASKS / "research_answer" / "kb")
    assert all(r.passed for r in results), [(r.evaluator, r.detail) for r in results if not r.passed]


def test_grade_research_wrong_answer_fails():
    results = grade_research("Beta was founded in 2005. Rome is the capital of Italy. Citations: F02",
                             TASKS / "research_answer" / "kb")
    assert not all(r.passed for r in results)


def test_grade_research_hallucinated_citation_fails():
    answer = "Alpha in 1998, Nairobi. Citations: F01, F05, F99"
    results = grade_research(answer, TASKS / "research_answer" / "kb")
    assert not all(r.passed for r in results)
    assert any(r.evaluator == "graders/kb-citations-v1" and not r.passed for r in results)


def test_grade_research_missing_citation_fails():
    answer = "Alpha was founded in 1998. Nairobi is the capital. Citations: F01"
    results = grade_research(answer, TASKS / "research_answer" / "kb")
    assert not all(r.passed for r in results)
    assert any(r.evaluator == "graders/kb-citations-v1" and "F05" in str(r.detail) for r in results)