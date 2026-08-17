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

### 1. Market Intelligence
- Signals (velocity, burst, persistence)
- Topics (candidate generation)
- Opportunities (mining)
- Joins (cross-oracle)
- VOI (value of information)
- Solutions (hypothesis generation)

### 2. Factory System
- Domain models (idea, product, research, score)
- Scoring engine (deterministic, with evidence)
- Intake (idea ingestion)
- Research (packet generation)
- Builders (MVP generation)
- Certification (12-check suite)
- Tasks (taxonomy)

### 3. Agent Hub
- Resolver (REUSE/FORK/SYNTHESIZE)
- Benchmark lab (architecture-controlled)
- Agent Factory (roles, topology, state)
- Lineage tracking
- Failure harness

### 4. HotSwap
- Router (cost-quality optimization)
- Policy (hard gates)
- Quota (ledger management)
- Failure (classification)
- Bandit (thompson sampling)
- Accounts (opportunity scoring)

### 5. Global OS
- State machine
- Merkle ledger
- Graph validation
- Queue management
- Release saga
- Scheduler

### 6. Hermes Integration
- Kanban (task management)
- Cron (scheduling)
- Skills (reusable capabilities)

---

## Commands

```bash
# Check system status
python3 factory/global_os/go.py --dry-run

# Run HotSwap
python3 factory/hotswap/integration.py

# Run market algorithms
cd factory/market && python3 -m pytest test_market_algorithms.py

# Run HotSwap tests
cd factory/hotswap && python3 -m pytest test_hotswap.py

# Run AgentHub tests
cd data/agenthub-pack/.../reference && python3 -m pytest test_agenthub.py
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
└── reviews/              # Review logs
```

---

*Global documentation v1.0*
