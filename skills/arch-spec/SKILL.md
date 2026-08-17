---
name: arch-spec
description: "Generate full technical architecture specifications from venture reports."
version: 1.0.0
date: 2026-08-18
author: venturelab
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Architecture, Spec, Technical]
    related_skills: [research, browser, venture-report]
---

# Architecture Spec Skill

You generate technical architecture specs. Read report, research patterns, design system, write spec.

## Workflow

1. Read report from `reports/{product}/report.md`
2. Search arxiv/github for architecture patterns
3. Design system components
4. Write spec to `specs/{product}/architecture.md`

## Spec Template

```markdown
# {NAME} — Technical Architecture

## System Overview
```text
ASCII diagram
```

## Core Components
### 1. {Component}
Purpose, Interface (HTTP endpoint), Input/Output JSON, Implementation details

## Data Model
```sql
CREATE TABLE ...
```

## API Endpoints
| Endpoint | Method | Purpose |

## Deployment
```text
Kubernetes/diagram
```

## Integration Points
- System: how

## Tech Stack
| Layer | Tech | Why |

## Costs
| Component | Monthly |

## Risks
| Risk | Prob | Impact | Mitigation |

## Metrics
| Metric | Target | Measure |

## Implementation Phases
Phase 1 (Week 1-2): MVP
Phase 2 (Week 3-4): Core
Phase 3 (Month 2): Production
```

## Browser Searches
- patterns: `https://arxiv.org/search/?query={q}+architecture`
- implementations: `https://github.com/search?q={q}&type=repositories`
