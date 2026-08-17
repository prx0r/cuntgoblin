# VentureLab Coordinator Pattern

*Higher-order coordination for multiple sub-factories*

---

## The Pattern (from nyah)

Nyah is a higher-order coordinator that:
1. Scans gaps in state
2. Generates tasks from gaps
3. Prioritizes by objective function
4. Dispatches to workers
5. Handles failures

```text
NYAH COORDINATOR
    │
    ├── reads state (openpatala_bridge.py)
    ├── identifies gaps (gap_analyzer.py)
    ├── generates tasks (task_generator.py)
    ├── prioritizes (objective function)
    ├── dispatches (scheduler.py)
    ├── executes via mimo-v2.5
    └── logs results
```

---

## How to Apply to VentureLab

### 1. Coordinator Layer

```text
VENTURELAB COORDINATOR
    │
    ├── reads venture state (venturelab_bridge.py)
    ├── identifies gaps (gap_analyzer.py)
    ├── generates tasks (task_generator.py)
    ├── prioritizes by score (objective function)
    ├── dispatches to sub-factories
    ├── executes via mimo-v2.5
    └── logs results
```

### 2. Sub-Factory Pattern

Each sub-factory is a contained unit:

```text
VENTURELAB (coordinator)
    │
    ├── venturelab-agent-infra/
    │   ├── Vision: Agent infrastructure
    │   ├── Ideas: 153 ideas
    │   └── Builds: 3 MVPs
    │
    ├── venturelab-braintech/
    │   ├── Vision: Brainwave entrainment
    │   ├── Ideas: 14 ideas
    │   └── Builds: (pending)
    │
    ├── venturelab-biotech/
    │   ├── Vision: Biotech research
    │   ├── Ideas: (pending)
    │   └── Builds: (pending)
    │
    └── venturelab-climate/
        ├── Vision: Climate tech
        ├── Ideas: (pending)
        └── Builds: (pending)
```

### 3. Coordinator Commands

```bash
# Scan all sub-factories for gaps
python3 coordinator.py --step scan

# Generate tasks from gaps
python3 coordinator.py --step generate

# Prioritize by objective function
python3 coordinator.py --step prioritize

# Dispatch to sub-factories
python3 coordinator.py --step dispatch

# Run full cycle
python3 coordinator.py --step cycle
```

---

## Objective Function (from sanskritbenchy)

```python
def objective(idea):
    """Score an idea by multiple axes."""
    novelty = idea.novelty_score
    research = idea.research_score
    feasibility = idea.feasibility_score
    market_timing = idea.market_timing_score
    
    # Weighted combination
    score = (
        0.3 * novelty +
        0.25 * research +
        0.25 * feasibility +
        0.2 * market_timing
    )
    
    return score
```

---

## Gap Analysis (from nyah)

```python
def analyze_gaps(sub_factory):
    """Identify gaps in a sub-factory."""
    gaps = []
    
    # Check ideas without reports
    for idea in sub_factory.ideas:
        if not idea.has_report:
            gaps.append({
                'type': 'missing_report',
                'idea': idea,
                'priority': idea.score,
            })
    
    # Check reports without specs
    for report in sub_factory.reports:
        if not report.has_spec:
            gaps.append({
                'type': 'missing_spec',
                'report': report,
                'priority': report.score,
            })
    
    # Check specs without builds
    for spec in sub_factory.specs:
        if not spec.has_build:
            gaps.append({
                'type': 'missing_build',
                'spec': spec,
                'priority': spec.score,
            })
    
    return gaps
```

---

## Task Generation (from nyah)

```python
def generate_tasks(gaps):
    """Generate tasks from gaps."""
    tasks = []
    
    for gap in gaps:
        if gap.type == 'missing_report':
            tasks.append({
                'title': f"Generate report for {gap.idea.name}",
                'description': f"Research and write report for {gap.idea.name}",
                'priority': gap.priority,
                'assignee': 'researcher',
            })
        
        elif gap.type == 'missing_spec':
            tasks.append({
                'title': f"Generate spec for {gap.report.product}",
                'description': f"Write architecture spec for {gap.report.product}",
                'priority': gap.priority,
                'assignee': 'architect',
            })
        
        elif gap.type == 'missing_build':
            tasks.append({
                'title': f"Build MVP for {gap.spec.product}",
                'description': f"Implement MVP from {gap.spec.product} spec",
                'priority': gap.priority,
                'assignee': 'builder',
            })
    
    return tasks
```

---

## Dispatch (from nyah)

```python
def dispatch(tasks, sub_factories):
    """Dispatch tasks to sub-factories."""
    for task in tasks:
        # Find best sub-factory for this task
        best_factory = find_best_factory(task, sub_factories)
        
        # Create kanban task
        create_kanban_task(
            title=task.title,
            description=task.description,
            assignee=task.assignee,
            factory=best_factory,
        )
        
        # Dispatch worker
        dispatch_worker(task)
```

---

## The Higher-Order Coordinator

```text
┌─────────────────────────────────────────────────────────┐
│              VENTURELAB COORDINATOR                      │
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   SCAN      │    │  GENERATE   │    │ PRIORITIZE  │ │
│  │   gaps      │───▶│   tasks     │───▶│   by score  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │  DISPATCH   │    │  EXECUTE    │    │    LOG      │ │
│  │  to factories│───▶│  via mimo   │───▶│   results   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ venturelab- │    │ venturelab- │    │ venturelab- │ │
│  │ agent-infra │    │ braintech   │    │ biotech     │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Key Insight

The coordinator doesn't build anything itself. It:
1. Scans sub-factories for gaps
2. Generates tasks to fill gaps
3. Prioritizes by objective function
4. Dispatches to sub-factories
5. Logs results

Each sub-factory builds its own MVPs.

The coordinator learns what works across all sub-factories and applies those patterns to new ones.

---

*Coordinator pattern v1.0*
