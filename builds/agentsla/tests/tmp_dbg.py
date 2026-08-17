import sys
sys.path.insert(0, "/root/venturelab/builds/agentsla")
from app.fake import MATHLIB_FIX, RESEARCH_PERFECT
from app.grader import grade_coding, grade_research
from pathlib import Path

print("--- MATHLIB patch ---")
for r in grade_coding(Path("/root/venturelab/builds/agentsla/tasks/coding_patch/mathlib"), MATHLIB_FIX):
    d = r.detail.get("message", "")[:140] if isinstance(r.detail, dict) else str(r.detail)
    print(r.evaluator, r.passed, "|", d)

print("--- RESEARCH ---")
for r in grade_research(RESEARCH_PERFECT, Path("/root/venturelab/builds/agentsla/tasks/research_answer/kb")):
    print(r.evaluator, r.passed, r.score, str(r.detail)[:120])