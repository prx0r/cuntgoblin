# Repo Hygiene

Remove tracked:
```text
.venv-agentsla/
**/__pycache__/
**/*.pyc
runtime DBs
temporary outputs
reproducible builds
```

Use `pyproject.toml` + `uv.lock`.

Consider accurate names:
- `MVPBuilder` → `TemplateInstantiator` until real build loop exists.
- `global_os` → `runtime`/`scheduler` until it is a genuine runtime.
- legacy `agent/run.py` → `legacy/venture_cli.py` after migration.

Docs should derive indexes from the actual registry/tree where possible.
