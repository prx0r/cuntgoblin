# Factory Module

*The autonomous venture factory implementation*

---

## Structure

```text
factory/
├── domain/           # Domain models (idea, product, research, score)
├── scoring/          # Deterministic scoring engine
├── intake/           # Idea ingestion
├── research/         # Research packet generation
├── builders/         # MVP building from templates
├── certification/    # 12-check certification
├── market/           # Market intelligence layer
├── ideas/            # Idea generation
├── vision/           # Vision boundaries
├── planning/         # Portfolio planning
├── reviewers/        # Independent review
├── github/           # GitHub publication
├── deploy/           # Deployment
├── telemetry/        # Metrics collection
└── portfolio/        # Portfolio management
```

## Modules

### domain/
Core domain models: Idea, Product, Research, Score

### scoring/
Deterministic scoring with evidence (GitHub, arxiv, market context)

### intake/
Idea ingestion from text/JSON with deduplication

### research/
Research packet generation with competitors and papers

### builders/
MVP generation from canonical templates

### certification/
12-check certification suite

### market/
Market intelligence layer (observations, claims, knowledge graph)

### ideas/
Idea generation with multiple generators (gap, arbitrage, research-transfer)

### vision/
Hardcoded vision boundaries for each factory

---

*Factory module v1.0*
