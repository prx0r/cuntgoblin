---
name: arch-spec
description: "Generate full technical architecture specs from venture reports."
version: 1.0.0
date: 2026-08-18
author: venturelab
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Architecture, Spec, Technical, Design]
    related_skills: [research, browser, venture-report]
---

# Architecture Spec Skill

You generate full technical architecture specifications from venture reports.

## How to generate an architecture spec

### Step 1: Read the report from reports/{product-name}/report.md

### Step 2: Research existing patterns on arxiv/github

### Step 3: Design using this template:

```markdown
# {PRODUCT_NAME} — Technical Architecture

## System Overview
{ASCII diagram}

## Core Components
### 1. {Component}
Purpose, Interface, Input, Output, Implementation

## Data Model
{schema}

## API Endpoints
| Endpoint | Method | Purpose |

## Deployment Architecture
{diagram}

## Integration Points
## Security Considerations
## Scalability Notes
## Implementation Phases
## Technology Stack
## Cost Estimates
## Risk Analysis
## Success Metrics
```

### Step 4: Save to specs/{product-name}/architecture.md

## Quality checklist
- [ ] System overview clear
- [ ] All components have interfaces
- [ ] Data models complete
- [ ] API endpoints specified
- [ ] Deployment clear
- [ ] Security addressed
- [ ] Implementation phases realistic
- [ ] Technology choices justified
- [ ] Cost estimates reasonable
- [ ] Risks identified
- [ ] Success metrics measurable
