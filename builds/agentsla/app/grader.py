"""app/grader.py — DETERMINISTIC graders. No LLM anywhere in evaluation.

Spec: "Do not use another LLM as the only grader." These graders are plain
subprocesses (patch/pytest/python compile) and string/regex normalization.

Every grader returns an EvalResult; nothing here depends on network or models.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

EVALUATORS = {
    "compile": "graders/compile-v1",
    "patch_apply": "graders/patch-apply-v1",
    "pytest": "graders/pytest-v1",
    "diff_scope": "graders/diff-scope-v1",
    "kb_answer": "graders/kb-facts-v1",
    "kb_citation": "graders/kb-citations-v1",
}


@dataclass
class EvalResult:
    evaluator: str
    passed: bool
    detail: dict = field(default_factory=dict)
    score: float | None = None  # fraction of sub-checks passed


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------- helpers

def extract_diff_block(text: str) -> str | None:
    """Pull the LAST fenced ```diff ... ``` block out of model output text."""
    pattern = re.compile(r"```diff\s*\n(.*?)```", re.DOTALL)
    matches = pattern.findall(text or "")
    if not matches:
        return None
    candidate = matches[-1].strip()
    return candidate if candidate else None


def apply_unified_diff(workdir: Path, diff_text: str) -> tuple[bool, str]:
    """Apply a unified diff with `patch -p1` inside workdir. Deterministic."""
    if not diff_text or not diff_text.strip():
        return False, "empty diff"
    with tempfile.NamedTemporaryFile("w", suffix=".patch", delete=False) as fh:
        fh.write(diff_text)
        patch_path = Path(fh.name)
    try:
        proc = subprocess.run(
            ["patch", "-p1", "-i", str(patch_path)],
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        ok = proc.returncode == 0
        return ok, (proc.stdout + proc.stderr).strip()[-2000:]
    except subprocess.TimeoutExpired:
        return False, "patch timed out"
    finally:
        patch_path.unlink(missing_ok=True)


def diff_touched_files(diff_text: str) -> list[str]:
    """File paths mentioned by a unified diff (--- a/... / +++ b/... lines)."""
    files: list[str] = []
    for m in re.finditer(r"^\+\+\+\s+b?/?(.*)$", diff_text, re.MULTILINE):
        files.append(m.group(1).strip())
    return files


def run_subprocess(cmd: list[str], cwd: Path, timeout: int = 60) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout + proc.stderr).strip()
        return proc.returncode, out[-3000:]
    except subprocess.TimeoutExpired:
        return -1, "subprocess timed out"
    except FileNotFoundError as exc:
        return -2, f"binary missing: {exc}"


# ---------------------------------------------------------------- coding

# Hidden test sources are embedded here (not shipped inside the task dir) so
# the agent can never read its own grader. The hidden tests exercise edge
# cases deliberately absent from the visible tests.
HIDDEN_TESTS: dict[str, str] = {
    "coding_patch": """
import math
from src.mathlib import median, clamp, quantile

def test_median_even_floats():
    assert math.isclose(median([0.5, 2.5]), 1.5, abs_tol=1e-9)
    assert math.isclose(median([1.0, 2.0, 3.0, 4.0]), 2.5, abs_tol=1e-9)

def test_median_negative():
    assert median([-5, -1, -2]) == -2
    assert math.isclose(median([-4, -1, -3, -2]), -2.5, abs_tol=1e-9)

def test_median_stability_odd_float():
    assert median([0.1, 0.2, 0.3]) == 0.2
""",
    "coding_debug": """
from src.parse_log import parse_line, parse_file

def test_skip0_is_parsed():
    rec = parse_line("2026-08-01T12:00:04Z method=GET path=/index status=200 bytes=512 skip=0")
    assert rec is not None
    assert rec.path == "/index"

def test_skip1_dropped():
    rec = parse_line("2026-08-01T12:00:05Z method=GET path=/health status=204 bytes=0 skip=1")
    assert rec is None

def test_plain_line_parsed():
    rec = parse_line("2026-08-01T12:00:00Z method=GET path=/index status=200 bytes=512")
    assert rec is not None and rec.status == 200 and rec.bytes_ == 512

def test_file_parse_counts():
    # 7 lines: 2 skipped (blank? none; skip=1 line) -> 6 records; the skip=0
    # line must be included, so sample.log yields 6 records, not 5.
    records = parse_file("data/sample.log")
    assert len(records) == 6
    assert sum(1 for r in records if r.method == "GET") == 5
    assert sum(1 for r in records if r.path == "/index") == 2
""",
}


def grade_coding(task_dir: Path, patch_text: str, *, use_hidden: bool = True) -> list[EvalResult]:
    """Grade a coding task end-to-end against hidden + visible criteria.

    Steps (in order, all deterministic):
      1. diff_scope  — patch must not touch tests/, hidden/, or the README.
      2. patch_apply — `patch -p1` must apply cleanly on a fresh copy.
      3. compile     — python compile of every .py under src/.
      4. pytest      — visible tests, then hidden tests, must both pass.
    """
    results: list[EvalResult] = []

    touched = diff_touched_files(patch_text)
    forbidden = [f for f in touched if f.startswith(("tests/", "hidden/")) or f.endswith("README.md")]
    results.append(
        EvalResult(
            evaluator=EVALUATORS["diff_scope"],
            passed=len(forbidden) == 0,
            detail={"touched_files": touched, "forbidden": forbidden},
        )
    )
    if forbidden:
        detail = {"touched": touched, "forbidden": forbidden}
        return [EvalResult(EVALUATORS["diff_scope"], False, detail)]

    with tempfile.TemporaryDirectory(prefix="agentsla_grade_") as tmp:
        workdir = Path(tmp)
        import shutil

        shutil.copytree(task_dir, workdir, dirs_exist_ok=True)
        ok, msg = apply_unified_diff(workdir, patch_text)
        results.append(
            EvalResult(
                evaluator=EVALUATORS["patch_apply"],
                passed=ok,
                detail={"ok": ok, "message": msg},
            )
        )
        if not ok:
            return results

        src_files = sorted((workdir / "src").glob("*.py")) if (workdir / "src").exists() else []
        compile_ok, compile_out = run_subprocess(
            [sys.executable, "-m", "py_compile", *[str(f) for f in src_files]], workdir
        )
        compile_passed = compile_ok == 0
        results.append(
            EvalResult(
                evaluator=EVALUATORS["compile"],
                passed=compile_passed,
                detail={"files": [f.name for f in src_files], "output": compile_out[-500:]},
            )
        )
        if not compile_passed:
            return results

        pytest_out: list[str] = []

        # 1. visible tests (tests/ dir inside the task)
        visible_dir = workdir / "tests"
        if visible_dir.exists():
            rc, out = run_subprocess(
                [sys.executable, "-m", "pytest", str(visible_dir), "-q", "--no-header", "-p", "no:cacheprovider"],
                workdir,
                timeout=90,
            )
            pytest_out.append(f"[visible] rc={rc}\n{out}")
            results.append(
                EvalResult(
                    evaluator=EVALUATORS["pytest"],
                    passed=rc == 0,
                    detail={"suite": "visible", "rc": rc, "output": out[-1500:]},
                )
            )
            if rc != 0:
                return results

        # 2. hidden tests (from the grader itself, never written to the task dir)
        if use_hidden:
            hidden_path = workdir / "hidden_test_grader.py"
            # Select the hidden suite by what the task directory contains.
            if (workdir / "src" / "parse_log.py").exists():
                hidden_source = HIDDEN_TESTS["coding_debug"]
            elif (workdir / "src" / "mathlib.py").exists():
                hidden_source = HIDDEN_TESTS["coding_patch"]
            else:
                hidden_source = ""
            if hidden_source:
                hidden_path.write_text(hidden_source, encoding="utf-8")
                rc, out = run_subprocess(
                    [sys.executable, "-m", "pytest", str(hidden_path), "-q", "--no-header", "-p", "no:cacheprovider"],
                    workdir,
                    timeout=90,
                )
                pytest_out.append(f"[hidden] rc={rc}\n{out}")
                results.append(
                    EvalResult(
                        evaluator=EVALUATORS["pytest"],
                        passed=rc == 0,
                        detail={"suite": "hidden", "rc": rc, "output": out[-1500:]},
                    )
                )
                if rc != 0:
                    return results

    passed_count = sum(1 for r in results if r.passed)
    results.append(
        EvalResult(
            evaluator="graders/summary-v1",
            passed=all(r.passed for r in results),
            score=passed_count / len(results) if results else 0.0,
            detail={"checks": [r.evaluator for r in results]},
        )
    )
    return results


# ---------------------------------------------------------------- research

def normalize_answer(text: str) -> str:
    """Lowercase, strip punctuation and run whitespace -> searchable form."""
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_citations(text: str) -> list[str]:
    return re.findall(r"\bF\d{2}\b", text or "")


def load_kb(kb_dir: Path) -> tuple[list[dict], list[dict]]:
    facts = json.loads((kb_dir / "facts.json").read_text(encoding="utf-8"))
    refs = json.loads((kb_dir / "references.json").read_text(encoding="utf-8"))
    return facts["facts"], refs["references"]


def grade_research(answer: str, kb_dir: Path) -> list[EvalResult]:
    """Grade a research answer against the local KB.

    Rubric (spec: 'reference-backed factual rubric / coverage / citation
    correctness'):
      1. coverage: every required fact's key tokens appear in the answer
         (configurable via facts.json's required_tokens / required_facts).
      2. citation: every cited ID exists in the KB; the required facts are
         actually cited.
    Score = fraction of sub-checks passed. All determinism, no LLM.
    """
    facts, refs = load_kb(kb_dir)
    facts_json = json.loads((kb_dir / "facts.json").read_text(encoding="utf-8"))
    required_facts = facts_json.get("required_facts", [])
    required_tokens = facts_json.get("required_tokens", [])
    fact_ids = {f["id"] for f in facts}
    ref_ids = {r["id"] for r in refs}

    norm = normalize_answer(answer)
    results: list[EvalResult] = []

    missing_tokens = [t for t in required_tokens if normalize_answer(t) not in norm]
    cov_checks = len(required_tokens) + len(required_facts)
    cov_done = cov_checks - len(missing_tokens) - sum(1 for f in required_facts if f not in normalize_answer(answer))
    # token containment is the primary check; required fact ids must be cited
    cited = extract_citations(answer)
    cited_unknown = sorted(set(cited) - fact_ids)
    missing_cited_required = [f for f in required_facts if f not in cited]
    cov_passed = len(missing_tokens) == 0 and len(missing_cited_required) == 0

    results.append(
        EvalResult(
            evaluator=EVALUATORS["kb_answer"],
            passed=cov_passed,
            score=cov_done / max(1, cov_checks),
            detail={
                "missing_tokens": missing_tokens,
                "missing_required_citations": missing_cited_required,
                "required_tokens": required_tokens,
                "required_facts": required_facts,
            },
        )
    )
    results.append(
        EvalResult(
            evaluator=EVALUATORS["kb_citation"],
            passed=len(cited_unknown) == 0 and len(missing_cited_required) == 0,
            score=(len(set(cited)) / max(1, len(set(cited) | set(cited_unknown)))) if cited else 0.0,
            detail={"cited": cited, "unknown_citations": cited_unknown, "valid_ids": sorted(fact_ids)},
        )
    )

    passed_count = sum(1 for r in results if r.passed)
    results.append(
        EvalResult(
            evaluator="graders/summary-v1",
            passed=all(r.passed for r in results),
            score=passed_count / len(results) if results else 0.0,
            detail={"checks": [r.evaluator for r in results]},
        )
    )
    return results