# Recipes

*Step-by-step guides for common tasks*

---

## Recipe 1: Research an Idea

```bash
# 1. Load idea from database
python3 -c "
import sqlite3
conn = sqlite3.connect('data/venturelab.db')
cur = conn.cursor()
cur.execute('SELECT * FROM ideas WHERE idea_id = ?', ('VENT_XXX',))
idea = dict(cur.fetchone())
print(json.dumps(idea, indent=2))
"

# 2. Search GitHub
# Use browser: https://github.com/search?q={query}

# 3. Search arxiv
# Use browser: https://arxiv.org/search/?query={query}

# 4. Write report
# Save to reports/{product}/report.md
```

## Recipe 2: Build MVP

```bash
# 1. Read spec
cat specs/{product}/architecture.md

# 2. Create build directory
mkdir -p builds/{product}

# 3. Initialize project
cd builds/{product}
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 4. Write code
# Follow architecture spec

# 5. Run tests
.venv/bin/python -m pytest tests/ -v

# 6. Generate certificate
.venv/bin/python -m app.certify
```

## Recipe 3: Run HotSwap

```bash
# 1. Import integration
python3 factory/hotswap/integration.py

# 2. Create task
python3 -c "
from factory.hotswap.integration import FactoryHotSwap
factory = FactoryHotSwap()
task = factory.create_task_spec('coding_patch', 'medium')
print(f'Task: {task.task_id}')
"

# 3. Route task
python3 -c "
from factory.hotswap.integration import FactoryHotSwap
from factory.hotswap.types import Route
factory = FactoryHotSwap()
task = factory.create_task_spec('coding_patch', 'medium')
routes = [Route(route_id='free', model_id='deepseek-v3', provider_id='deepseek', free=True, prior_success=0.95)]
result = factory.route_task(task, routes)
print(f'Routed to: {result[\"primary_route\"]}')
"
```

## Recipe 4: Check System Status

```bash
# Check all systems
python3 factory/global_os/go.py --dry-run

# Run all tests
cd factory/hotswap && python3 -m pytest test_hotswap.py -v
cd factory/market && python3 -m pytest test_market_algorithms.py -v

# List ideas
python3 -c "import sqlite3; conn=sqlite3.connect('data/venturelab.db'); cur=conn.cursor(); cur.execute('SELECT COUNT(*) FROM ideas'); print(f'Total: {cur.fetchone()[0]}')"
```

## Recipe 5: Generate Report

```bash
# Load idea
python3 -c "
import sqlite3
conn = sqlite3.connect('data/venturelab.db')
cur = conn.cursor()
cur.execute('SELECT * FROM ideas WHERE idea_id = ?', ('VENT_XXX',))
idea = dict(cur.fetchone())
"

# Search GitHub
# Use browser: https://github.com/search?q={query}

# Search arxiv
# Use browser: https://arxiv.org/search/?query={query}

# Write report to reports/{product}/report.md
```

---

*Recipes v1.0*
