"""Temporary patcher for run_benchmark.py demo-isolation cleanup. Delete after use."""
import pathlib

p = pathlib.Path("/root/venturelab/builds/agentsla/run_benchmark.py")
s = p.read_text()

def sub(old, new, tag):
    global s
    assert old in s, f"MISS {tag}"
    s = s.replace(old, new, 1)
    print("ok", tag)

# 1. rename helper
sub(
    "def ensure_demo_isolated(stub: bool) -> None:",
    "def _point_at(db_path_: str, runs_dir: str) -> None:",
    "helper-name",
)
# fix its body to the clean version
sub(
    '''    if not stub:
        return
    import os as _os

    demo_db = "/tmp/agentsla-demo/agentsla-demo.db"
    demo_runs = "/tmp/agentsla-demo/runs"
    _os.environ.setdefault("AGENTSLA_DB", demo_db)
    _os.environ.setdefault("AGENTSLA_RUNS_DIR", demo_runs)
    import app.db
    import app.evidence
    import app.runner

    app.db_path.cache_clear() if hasattr(app.db_path, "cache_clear") else None
    app.runner.DB_PATH = Path(demo_db)
    app.evidence.RUNS_ROOT = Path(demo_runs)''',
    '''    os.environ["AGENTSLA_DB"] = db_path_
    os.environ["AGENTSLA_RUNS_DIR"] = runs_dir
    import app.evidence
    import app.runner

    app.runner.DB_PATH = Path(db_path_)
    app.evidence.RUNS_ROOT = Path(runs_dir)''',
    "helper-body",
)

# 2. run_benchmark stub block
sub(
    '''def run_benchmark(bench: dict, stub: bool = False, limit_classes: list[str] | None = None):
    if stub:
        import app.db
        import app.runner

        demo_db = "/tmp/agentsla-demo/agentsla-demo.db"
        demo_runs = "/tmp/agentsla-demo/runs"
        os.environ.setdefault("AGENTSLA_DB", demo_db)
        os.environ.setdefault("AGENTSLA_RUNS_DIR", demo_runs)
        app.runner.DB_PATH = Path(demo_db)
        import app.evidence

        app.evidence.RUNS_ROOT = Path(demo_runs)
    conn = connect(DB_PATH)''',
    '''def run_benchmark(bench: dict, stub: bool = False, limit_classes: list[str] | None = None):
    db_file = Path(DB_PATH)
    if stub:
        _point_at("/tmp/agentsla-demo/agentsla-demo.db", "/tmp/agentsla-demo/runs")
        db_file = Path("/tmp/agentsla-demo/agentsla-demo.db")
    conn = connect(db_file)''',
    "run_benchmark-db",
)

# 3. print_summary conn
sub(
    "def print_summary(task_class: str | None = None):\n    conn = connect(DB_PATH)",
    "def print_summary(task_class: str | None = None, conn=None):\n    if conn is None:\n        conn = connect(Path(DB_PATH))",
    "print_summary",
)

# 4. main unified pointing
sub(
    '''    conn = connect(DB_PATH)

    if args.summary:
        print_summary(args.task)
        return 0

    if args.demo or args.demo_everything:
        os.environ.setdefault("AGENTSLA_DB", "/tmp/agentsla-demo/agentsla-demo.db")
        os.environ.setdefault("AGENTSLA_RUNS_DIR", "/tmp/agentsla-demo/runs")
        from app.db import connect as _c2
        import app.db as _adb
        import app.evidence as _aev
        import app.runner as _ar

        _ar.DB_PATH = Path("/tmp/agentsla-demo/agentsla-demo.db")
        _aev.RUNS_ROOT = Path("/tmp/agentsla-demo/runs")
        conn = _c2("/tmp/agentsla-demo/agentsla-demo.db")

    if args.demo:''',
    '''    db_file = Path(DB_PATH)
    if args.demo or args.demo_everything or (args.bench and not args.live):
        db_file = Path("/tmp/agentsla-demo/agentsla-demo.db")
        _point_at(str(db_file), "/tmp/agentsla-demo/runs")
    conn = connect(db_file)

    if args.summary:
        print_summary(args.task, conn)
        return 0

    if args.demo:''',
    "main-demo",
)

# 5. bench summary pass conn
sub(
    "        run_benchmark(bench, stub=stub)\n        print_summary()\n        return 0",
    "        run_benchmark(bench, stub=stub)\n        print_summary(None, conn)\n        return 0",
    "bench-summary",
)

p.write_text(s)
print("run_benchmark.py patched cleanly")