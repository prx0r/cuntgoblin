# KNEE — Technical Architecture

*Generated: 2026-08-18T04:30:00Z*

---

## System Overview

```text
┌─────────────────────────────────────────────┐
│              KNEE API                       │
│                                             │
│  ┌─────────────┐  ┌─────────────┐          │
│  │   Task      │  │   Model     │          │
│  │ Classifier  │  │  Registry   │          │
│  └──────┬──────┘  └──────┬──────┘         │
│         │                │                 │
│         └────────┬───────┘                 │
│                  ▼                         │
│         ┌─────────────┐                   │
│         │    Knee     │                   │
│         │  Algorithm  │                   │
│         └──────┬──────┘                   │
│                │                          │
│         ┌──────┴──────┐                   │
│         ▼             ▼                   │
│  ┌─────────────┐ ┌─────────────┐         │
│  │  Endpoint   │ │  AgentSLA   │         │
│  │   Truth     │ │   Data      │         │
│  └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────┘
```

---

## Core Components

### 1. Task Classifier

**Purpose:** Classify incoming tasks by type and complexity

**Interface:**
```http
POST /classify
```

**Input:**
```json
{
  "task_description": "...",
  "task_type": "optional",
  "context": {}
}
```

**Output:**
```json
{
  "task_type": "coding",
  "complexity": "medium",
  "required_capabilities": ["code_generation", "testing"],
  "estimated_difficulty": 0.65
}
```

**Implementation:**
- Embedding-based classification
- Historical task database
- Capability requirement extraction

---

### 2. Model Registry

**Purpose:** Maintain registry of all available models/endpoints

**Interface:**
```http
GET /models
GET /models/{id}
```

**Implementation:**
- SQLite database
- Synced from Dell/EndpointTruth
- Includes pricing, capabilities, health

---

### 3. Knee Algorithm

**Purpose:** Find the quality cliff for a task

**Interface:**
```http
POST /knee
```

**Input:**
```json
{
  "task_type": "coding",
  "minimum_success": 0.90,
  "constraints": {
    "max_cost": 1.00,
    "max_latency": 30
  }
}
```

**Output:**
```json
{
  "recommended": {
    "model": "deepseek-v3",
    "provider": "provider-x",
    "estimated_success": 0.923,
    "cost_per_task": 0.017
  },
  "next_cheaper": {
    "model": "tiny-model-y",
    "estimated_success": 0.694,
    "cost_per_task": 0.009
  },
  "cliff": 0.229,
  "confidence": 0.87
}
```

**Implementation:**
- Query AgentSLA database for task/model performance
- Sort by cost
- Find knee point where success drops below threshold
- Return recommendation with cliff analysis

---

## Data Model

```sql
-- Task performance observations
CREATE TABLE task_observations (
    id INTEGER PRIMARY KEY,
    task_type TEXT,
    model_id TEXT,
    provider TEXT,
    success BOOLEAN,
    cost REAL,
    latency_ms INTEGER,
    tokens_used INTEGER,
    observed_at TIMESTAMP
);

-- Knee calculations
CREATE TABLE knee_calculations (
    id INTEGER PRIMARY KEY,
    task_type TEXT,
    minimum_success REAL,
    recommended_model TEXT,
    recommended_cost REAL,
    cliff_point REAL,
    calculated_at TIMESTAMP
);
```

---

## API Endpoints

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| /knee | POST | Find quality cliff | task + constraints | recommendation |
| /knee/{task_type} | GET | Get cached knee | - | knee data |
| /classify | POST | Classify task | task description | classification |
| /models | GET | List models | filter | model list |

---

## Deployment Architecture

```text
┌─────────────────────────────────────┐
│           Kubernetes                │
│  ┌─────────────┐  ┌─────────────┐  │
│  │  Knee API   │  │  Postgres   │  │
│  │  (3 pods)   │  │  (primary)  │  │
│  └─────────────┘  └─────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  │
│  │   Redis     │  │  Worker     │  │
│  │  (cache)    │  │ (observations)│ │
│  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────┘
```

---

## Integration Points

- **Dell/LLMDeals**: Model pricing and availability
- **EndpointTruth**: Runtime measurements
- **AgentSLA**: Task performance data
- **LiteLLM**: Execute recommendations

---

## Technology Stack

| Layer | Technology | Why |
|-------|------------|-----|
| API | FastAPI | Async, fast, good docs |
| Database | PostgreSQL | Reliable, JSON support |
| Cache | Redis | Fast reads |
| Queue | Celery | Background tasks |
| Hosting | Railway/Fly | Easy deployment |

---

## Cost Estimates

| Component | Monthly Cost | Notes |
|-----------|--------------|-------|
| Compute | $50 | 3 API pods |
| Database | $25 | Managed Postgres |
| Cache | $15 | Managed Redis |
| Storage | $5 | Logs and data |
| **Total** | **$95** | |

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Insufficient data | Medium | High | Start with synthetic, collect real |
| Model pricing changes | High | Medium | Sync from Dell hourly |
| Cold start | High | High | Free tier + content marketing |

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| API latency | <100ms p95 | Monitoring |
| Recommendation accuracy | >85% | A/B testing |
| Cost savings | >30% vs naive | Customer reports |
| API usage | 10k calls/day | Analytics |

---

*Architecture spec generated by VentureLab*
