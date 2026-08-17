# VentureLab Global Documentation

*The complete system documentation*

---

## System Overview

```text
┌─────────────────────────────────────────────────────────┐
│              VENTURELAB GLOBAL OPERATING SYSTEM          │
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   MARKET    │    │   FACTORY   │    │   AGENT     │ │
│  │ INTELLIGENCE│───▶│   SYSTEM    │───▶│   HUB       │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   HOTSWAP   │    │   GLOBAL    │    │   HERMES    │ │
│  │   ROUTING   │◀───│   MANAGER   │◀───│   AGENT     │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Market Intelligence (18 modules)
- Signals (velocity, burst, persistence)
- Topics (candidate generation)
- Opportunities (mining)
- Joins (cross-oracle)
- VOI (value of information)
- Solutions (hypothesis generation)

### 2. Factory System (14 modules)
- Domain models (idea, product, research, score)
- Scoring engine (deterministic, with evidence)
- Intake (idea ingestion)
- Research (packet generation)
- Builders (MVP generation)
- Certification (12-check suite)
- Tasks (taxonomy)

### 3. Agent Hub (14 modules)
- Resolver (REUSE/FORK/SYNTHESIZE)
- Benchmark lab (architecture-controlled)
- Agent Factory (roles, topology, state)
- Lineage tracking
- Failure harness

### 4. HotSwap (14 modules)
- Router (cost-quality optimization)
- Policy (hard gates)
- Quota (ledger management)
- Failure (classification)
- Bandit (thompson sampling)
- Accounts (opportunity scoring)

### 5. Global OS (9 modules)
- State machine
- Merkle ledger
- Graph validation
- Queue management
- Release saga
- Scheduler

### 6. MCP Server (3 tools)
- venturelab_list_ideas
- venturelab_route_task
- venturelab_get_status

---

## Commands

```bash
# Check system status
python3 factory/global_os/go.py --dry-run

# Run HotSwap
python3 factory/hotswap/integration.py

# Run MCP server
python3 mcp/server.py tools/list

# Run all tests
cd factory/hotswap && python3 -m pytest test_hotswap.py -v
cd factory/market && python3 -m pytest test_market_algorithms.py -v

# List ideas
python3 -c "import sqlite3; conn=sqlite3.connect('data/venturelab.db'); cur=conn.cursor(); cur.execute('SELECT COUNT(*) FROM ideas'); print(f'Total: {cur.fetchone()[0]}')"
```

---

## File Structure

```
venturelab/
├── factory/
│   ├── domain/           # Domain models
│   ├── scoring/          # Scoring engine
│   ├── intake/           # Idea ingestion
│   ├── research/         # Research generation
│   ├── builders/         # MVP building
│   ├── certification/    # Certification
│   ├── market/           # Market intelligence
│   ├── ideas/            # Idea generation
│   ├── vision/           # Vision boundaries
│   ├── hotswap/          # HotSwap routing
│   ├── agenthub/         # Agent Hub
│   ├── global_os/        # Global operating system
│   └── tasks/            # Task taxonomy
├── mcp/                  # MCP server
├── api.py                # FastAPI server
├── Dockerfile            # Docker config
├── docker-compose.yml    # Docker compose
├── requirements.txt      # Dependencies
├── schemas/              # JSON schemas
├── config/               # Configuration
├── sql/                  # SQL schemas
├── workflows/            # Workflow definitions
├── skills/               # Hermes skills
├── data/                 # Data and runs
├── research/             # Research repos
├── builds/               # Built MVPs
├── specs/                # Architecture specs
├── reports/              # Venture reports
├── reviews/              # Review logs
└── recipes/              # Step-by-step guides
```

---

## Tests

- HotSwap: 11/11 PASS
- Market: 11/11 PASS
- AgentHub: 13/13 PASS
- Global OS: 14/14 PASS
- venturelab go: READY

---

## Documentation

- GLOBAL-DOCS.md (this file)
- AGENTS.md (agent rules)
- CODING-AGENT.md (how to work)
- RECIPES.md (step-by-step guides)
- All factory READMEs

---

*Global documentation v1.0*
