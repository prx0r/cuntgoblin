---
name: factory-spec
description: "Generate architecture specs from venture reports. Research patterns, design systems."
version: 1.0.0
date: 2026-08-18
author: venturelab
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Spec, Architecture, Design]
    related_skills: [venture-report, research, browser]
---

# Factory Spec Skill

You generate architecture specs from venture reports.

## When to use

When a kanban task says "Generate [product] Architecture Spec"

## What to research

1. **arxiv papers** on the approach
2. **GitHub repos** with similar implementations
3. **Existing products** in the space
4. **Architecture patterns** that work

## What to produce

Save to specs/{product}/architecture.md:

1. System Overview (ASCII diagram)
2. Core Components (purpose, interface, input/output)
3. Data Model (SQL/JSON schema)
4. API Endpoints (table)
5. Deployment Architecture
6. Integration Points
7. Technology Stack
8. Cost Estimates
9. Risk Analysis
10. Success Metrics
11. Implementation Phases

## Browser searches

- arxiv: `https://arxiv.org/search/?query={q}+architecture`
- github: `https://github.com/search?q={q}&type=repositories`
- web: `https://www.google.com/search?q={q}+pattern+implementation`

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
