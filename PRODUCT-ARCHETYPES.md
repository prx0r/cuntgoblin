# Product Archetypes

*Standardized templates for different product types*

---

## 1. data-oracle

For Dell, MCPTruth, EndpointTruth.

Includes:
```text
collector
artifact store
observations
assertions
freshness
reconciliation
REST
MCP
scheduler
coverage
```

Template: `templates/data-oracle/`

---

## 2. agent-tool

For Toolloader, Knee.

Includes:
```text
MCP server
REST API
resolver
telemetry
evals
```

Template: `templates/agent-tool/`

---

## 3. registry

For ArchOracle, Agentpacks.

Includes:
```text
registry database
versions
search
ranking
submission
moderation
API
MCP
website
```

Template: `templates/registry/`

---

## 4. benchmark

For AgentSLA.

Includes:
```text
task corpus
runner
sandbox
grader
results
leaderboards
```

Template: `templates/benchmark/`

---

## 5. saas

Includes:
```text
auth
billing
dashboard
API
webhooks
```

Template: `templates/saas/`

---

## 6. library

Includes:
```text
package
CLI
docs
tests
release automation
```

Template: `templates/library/`

---

## Choosing an Archetype

The factory chooses based on:
- Product type
- Target customers
- Revenue model
- Technical requirements

---

*Product archetypes v1.0*
