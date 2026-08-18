# External Research Sources

Checked 2026-08-18.

## Hermes

- NousResearch/hermes-agent
  - https://github.com/NousResearch/hermes-agent
  - current Kanban docs
  - current cron docs
  - skills docs
  - programmatic integration docs
  - CLI command docs

Relevant current primitives:
- SQLite-backed multi-profile Kanban,
- worker dispatcher,
- idempotency/retries/max runtime/workspaces,
- skills,
- cron,
- model/provider switching,
- ACP, TUI JSON-RPC and HTTP API integration surfaces.

## Similar projects

- LangGraph — https://github.com/langchain-ai/langgraph
  - durable execution/checkpointing/stateful graphs.
- OpenHands — https://github.com/OpenHands/OpenHands
  - isolated software-agent runtime/SDK patterns.
- LiteLLM — https://github.com/BerriAI/litellm
  - provider/gateway/routing/cost/fallback plumbing.
- Agent Lightning — https://github.com/microsoft/agent-lightning
  - trajectory/optimization separation for later learning.
- MCP Python SDK — https://github.com/modelcontextprotocol/python-sdk
  - v2 is current stable on review date; `MCPServer`.

## Selected research

### WISERouter
arXiv:2607.23765  
https://arxiv.org/abs/2607.23765  
Constrained contextual bandit routing with a workload budget.

### Learning to Route LLMs from Bandit Feedback (BaRP)
arXiv:2510.07429  
https://arxiv.org/abs/2510.07429  
Partial-feedback routing and tunable cost/performance preference.

### Verified Multi-Agent Orchestration
arXiv:2603.11445  
https://arxiv.org/abs/2603.11445  
DAG plan/execute/verify/replan with bounded stop conditions.

### Agent Lightning
arXiv:2508.03680  
https://arxiv.org/abs/2508.03680  
Relevant later after trustworthy trajectories/rewards exist.

### Managing Procedural Memory in LLM Agents
arXiv:2606.23127  
https://arxiv.org/abs/2606.23127  
Relevant to evaluated skill/procedural-memory evolution.

## Selection policy

Research was promoted into the roadmap only when it maps to a current VentureLab component and has a concrete acceptance metric.
