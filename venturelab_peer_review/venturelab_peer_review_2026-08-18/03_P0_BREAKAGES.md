# P0 Breakages

## 1. Missing `factory.system`

`api.py`, MCP and Docker depend on it. Add a real composition root.

**Acceptance**
```bash
python -c "from factory.system import VentureLabSystem"
python -c "from api import app"
```

## 2. Docker target cannot start

Current target references `factory.system:app`.

Either:
- expose `app` deliberately from the composition module, or
- run `uvicorn api:app`.

Then container-smoke `/health`.

## 3. `global_os/go.py` imports absent siblings

Reviewed `factory/global_os/` contained only `go.py`, while imports expect `state`, `merkle`, `graph`, `queue`, `scheduler`, `release`.

Restore canonical production modules or remove that CI gate. Do not “pass” by testing a copy under `data/*/reference`.

## 4. Research import failure

`factory/research/packet.py` imports `search_github` / `search_arxiv` from a scoring module where they do not exist.

Create typed source adapters under `factory/sources/`.

## 5. Hermes Kanban wrapper is wrong for current CLI shape

Current Hermes uses board-scoped commands such as:

```bash
hermes kanban --board venturelab create "Research ..."
hermes kanban --board venturelab comment <task-id> "..."
```

The current wrapper passes positional board/command arguments and does not persist the created task ID for lifecycle operations.

Use `--json`, capture exact task IDs, inspect exit code.

## 6. CI has not independently proved the head

GitHub returned no statuses and no workflow runs for the inspected head.

One root command must prove production:
```bash
pytest -q
```

## 7. Venv/cache committed

Remove tracked:
- `.venv-agentsla/`
- `__pycache__/`
- `*.pyc`
- reproducible/generated outputs.

## 8. DB startup assumes prior state

The API directly opens SQLite and expects an `ideas` table.

Add explicit migrations and schema version checks.

## 9. Existing-product search is a stub

`check_existing_products()` returning `[]` makes “no competition” indistinguishable from “not implemented.”

Unknown must remain UNKNOWN.

## 10. Shell errors are swallowed

External execution must record:
```json
{"ok":false,"exit_code":2,"stdout":"...","stderr":"..."}
```
and drive retry/fail policy.
