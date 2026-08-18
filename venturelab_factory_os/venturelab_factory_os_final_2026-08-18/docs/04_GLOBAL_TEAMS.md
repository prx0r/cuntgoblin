# Global teams

Teams are reusable formulas/modules, not necessarily resident agents.

Each TeamDefinition declares:
- trigger
- inputs
- work template
- executor preference
- output contract
- gates
- budget
- timeout
- risk classes where mandatory

Default teams:

- Research & Evidence
- Architecture
- Builder
- QA/Test
- Red Team
- Security/Privacy
- Provenance/Certifier
- Cost/FinOps
- Docs/Publisher
- Release/Deploy
- Observability
- Post-release Audit
- Maintenance/Refactor
- Portfolio Review

A factory manifest declares mandatory and conditional teams. The OS expands them into WorkGraph
nodes. A docs or builder team cannot certify itself.
