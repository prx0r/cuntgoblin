# Evolutionary Mechanics for VentureLab

*Ideas evolve, system learns, visions switch based on performance*

---

## Core Insight

Ideas are like organisms in an ecosystem:
- They compete for resources (attention, funding)
- They reproduce (similar ideas spawn)
- They mutate (variations appear)
- They die (bad ideas get pruned)
- They evolve (good patterns spread)

The system needs **reinforcement mechanisms** that drive good behavior and punish bad behavior.

---

## The Idea Lifecycle

```text
SEED (new idea)
    ↓
GROW (research, score)
    ↓
MATURE (build MVP)
    ↓
REPRODUCE (spawn similar ideas)
    ↓
DIE (if scores low) or SCALE (if scores high)
```

---

## Reinforcement Mechanisms

### 1. Reward: Revenue Signal

When an idea generates revenue:
- Increase its score
- Boost similar ideas
- Spawn variations

When an idea loses money:
- Decrease its score
- Penalize similar ideas
- Prune variations

### 2. Reward: User Adoption

When users adopt an idea:
- Increase its score
- Boost similar ideas
- Spawn variations

When users abandon an idea:
- Decrease its score
- Penalize similar ideas
- Prune variations

### 3. Reward: Data Accumulation

When an idea accumulates data:
- Increase its score (data moat)
- Boost similar ideas
- Spawn variations

When an idea has no data:
- Decrease its score
- Penalize similar ideas
- Prune variations

### 4. Penalty: Failed Experiments

When an experiment fails:
- Decrease its score
- Penalize similar ideas
- Learn from failure

### 5. Penalty: Market Rejection

When market rejects an idea:
- Decrease its score
- Penalize similar ideas
- Pivot or kill

---

## Vision Switching

When to switch visions:

### Trigger 1: Performance Plateau
If sub-factory performance plateaus for 3 months:
- Analyze why
- Consider switching vision
- Or pivot within vision

### Trigger 2: Market Shift
If market shifts significantly:
- Re-evaluate vision viability
- Consider switching vision
- Or adapt to new market

### Trigger 3: Opportunity Cost
If another vision has higher expected value:
- Compare ROI
- Consider switching vision
- Or allocate more resources

### Trigger 4: Resource Constraint
If resources are constrained:
- Focus on highest-performing vision
- Kill lowest-performing vision
- Or merge visions

---

## Evolutionary Algorithms

### 1. Genetic Algorithm for Ideas

```text
POPULATION (ideas)
    ↓
FITNESS (scores)
    ↓
SELECTION (top performers)
    ↓
CROSSOVER (combine ideas)
    ↓
MUTATION (random changes)
    ↓
NEXT GENERATION
```

### 2. Novelty Search

Search for ideas that are different from what exists:
- Measure distance from existing ideas
- Reward novelty
- Explore new regions of idea space

### 3. Quality-Diversity

Maintain a population of diverse, high-quality solutions:
- Measure quality (scores)
- Measure diversity (distance from other ideas)
- Reward both

### 4. Curiosity-Driven Exploration

Explore ideas that reduce uncertainty:
- Measure information gain
- Reward exploration
- Balance exploration vs exploitation

---

## Idea Queue Management

### Queue States

```text
SEED → GROW → MATURE → REPRODUCE → DIE/SCALE
```

### Queue Priority

Ideas are prioritized by:
1. Score (higher = higher priority)
2. Age (older = lower priority)
3. Dependencies (blocking = higher priority)
4. Market timing (urgent = higher priority)

### Queue Actions

- **Promote**: Move idea to next state
- **Demote**: Move idea to previous state
- **Kill**: Remove idea from queue
- **Spawn**: Create new idea from existing
- **Merge**: Combine two ideas

---

## Behavioral Reinforcement

### Good Behavior (Reward)

| Behavior | Reward |
|----------|--------|
| Idea generates revenue | +10 score |
| Idea gets users | +5 score |
| Idea accumulates data | +3 score |
| Experiment succeeds | +2 score |
| Market validates | +5 score |

### Bad Behavior (Penalty)

| Behavior | Penalty |
|----------|---------|
| Idea loses money | -10 score |
| Users abandon | -5 score |
| No data accumulation | -3 score |
| Experiment fails | -2 score |
| Market rejects | -5 score |

### Neutral Behavior (No Change)

| Behavior | Effect |
|----------|--------|
| Idea exists but inactive | No change |
| Experiment pending | No change |
| Market uncertain | No change |

---

## Vision Switching Algorithm

```python
def should_switch_vision(current_vision, alternative_vision):
    """Determine if we should switch visions."""
    
    # Calculate ROI for each
    current_roi = calculate_roi(current_vision)
    alternative_roi = calculate_roi(alternative_vision)
    
    # Check performance plateau
    plateau = check_plateau(current_vision, months=3)
    
    # Check market shift
    market_shift = check_market_shift(current_vision)
    
    # Decision matrix
    if plateau and alternative_roi > current_roi * 1.5:
        return True, "Performance plateau + higher ROI elsewhere"
    
    if market_shift and alternative_roi > current_roi * 1.2:
        return True, "Market shift + higher ROI elsewhere"
    
    if current_roi < 0 and alternative_roi > 0:
        return True, "Current negative ROI, alternative positive"
    
    return False, "Current vision still viable"
```

---

## Comparison to Agentic Repos

### What They Have

| Repo | Mechanism | What It Does |
|------|-----------|--------------|
| sanskritbenchy | Hypothesis Lab | Open-ended exploration |
| agentic-infra | Objective Function | Weighted scoring |
| dell | Certification | Quality gates |
| moltwork | Receipts | Verification |

### What We're Adding

| Mechanism | What It Does |
|-----------|--------------|
| Idea Evolution | Ideas mutate and reproduce |
| Reinforcement Learning | Good behavior rewarded, bad punished |
| Vision Switching | Switch based on performance |
| Cross-Pollination | Ideas from one sector inspire another |
| Fitness Landscape | Explore space of possible products |

---

## The Evolutionary Loop

```text
IDEA POPULATION
    ↓
EVALUATE (scores)
    ↓
SELECT (top performers)
    ↓
REPRODUCE (spawn variations)
    ↓
MUTATE (random changes)
    ↓
EVALUATE (scores)
    ↓
PRUNE (kill low performers)
    ↓
REPEAT
```

---

## Key Insight

The system isn't just building products. It's **evolving a population of ideas** that compete for resources, reproduce, and adapt to the market.

The reinforcement mechanisms ensure:
- Good ideas get more resources
- Bad ideas get pruned
- The system learns what works
- Visions switch when performance plateaus

---

*Evolutionary mechanics v1.0*
