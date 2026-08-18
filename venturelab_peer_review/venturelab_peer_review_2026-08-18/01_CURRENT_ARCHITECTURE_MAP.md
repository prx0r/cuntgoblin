# Current Architecture Map

```text
agent/
  run.py              legacy venture orchestration
  watchdog.py
  audit/trace/verify helpers

factory/
  agenthub/            architecture descriptions + resolver
  builders/            template copying/customization
  certification/
  domain/
  global_os/           reviewed listing only contains go.py
  hotswap/             routing/quota/bandit/policy/failure
  ideas/
  intake/
  market/              opportunity/genesis/VOI algorithms
  research/
  scoring/
  tasks/
  vision/

templates/
  a2a-subject
  agent-system
  benchmark-suite
  data-oracle

api.py
mcp/server.py
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
```

## Four competing centers currently exist

1. `agent/run.py`
2. modular `factory/*`
3. `factory/global_os/go.py`
4. the missing `factory.system` expected by API/MCP/Docker

Pick one composition root.

## Proposed root

```text
factory/system.py
  ├── Store / migrations
  ├── JobQueue / events
  ├── ArtifactStore
  ├── EvidenceStore
  ├── HermesExecutor
  ├── HermesKanbanAdapter
  ├── HotSwapRouter
  ├── VerifierRegistry
  ├── FactoryRegistry
  └── PublisherRegistry
```

REST, MCP, CLI, Hermes Kanban and cron become surfaces over this same system.
