# TOOLLOADER — Dynamic MCP/API Tool Loader

*Report generated: 2026-08-18T03:45:00Z*

---

## Thesis

Agent receives 1,900 available tools but context receives search_tools + invoke_tool. At runtime: intent → server retrieval → tool retrieval → reranking → load 3 tools → execute.

Don't make another vector search wrapper. Make the scoring function that considers semantic relevance, historical success, schema-token cost, latency, health, permissions, auth friction, reliability, and price.

---

## Product Spec

### Core Endpoint

```http
POST /toolloader/select
```

Input:
```json
{
  "task": "create_github_issue",
  "context": "repo: foo/bar",
  "max_tools": 5,
  "constraints": {
    "max_tokens": 10000,
    "require_auth": false
  }
}
```

Response:
```json
{
  "selected": [
    {
      "tool": "github/create_issue",
      "score": 0.94,
      "context_cost": 847,
      "latency_ms": 120,
      "success_rate": 0.99
    }
  ],
  "total_context_tokens": 847,
  "estimated_cost": 0.002
}
```

---

## Current Competitors

| Competitor | What They Do | Gap |
|------------|--------------|-----|
| MCP-Zero | Active tool discovery | No scoring optimization |
| SING | Hierarchical retrieval | No cost/quality optimization |
| mcp-gateway | Tool gateway | No intelligent selection |
| Context7 | Code documentation | Not tool-focused |

---

## arXiv Research

1. **SING: Synthetic Intention Graph for Scalable Active Tool** (2026)
   - Hierarchical MCP-server-then-tool retrieval
   - Shows tool retrieval is a real problem

2. **Dynamic Tool Gating and Lazy Schema Loading** (2026)
   - Studies lazy schema loading for MCP
   - Validates the approach

3. **Scalable LLM Agent Tool Access in the Cloud** (2026)
   - Handles 3,000+ tools
   - Reduces tool-selection token consumption by 23.8x

---

## GitHub Projects

| Project | Stars | What It Does |
|---------|-------|--------------|
| MikkoParkkola/mcp-gateway | 500 | MCP tool gateway |
| punkpeye/awesome-mcp-servers | 5000 | MCP server directory |

---

## Why It's Cool

1. **Solves real problem** — agents waste tokens on irrelevant tools
2. **Measurable savings** — 23.8x reduction in token consumption
3. **Composable** — works with any MCP server
4. **Oracle-powered** — uses Knee for quality/cost optimization

---

## Monetization

1. **API pricing** — $0.0001 per tool selection
2. **Gateway fees** — charge for managed tool loading
3. **Enterprise** — custom scoring functions
4. **Data licensing** — tool success/failure data

---

## Path to Market

1. **Week 1-2**: Build MVP with 50 tools
2. **Week 3-4**: Add MCP gateway integration
3. **Month 2**: Launch public API
4. **Month 3**: Coding agent integrations
5. **Month 6**: Enterprise deals

---

## Final Rating

**Score: 10/10**

**Why:**
- Huge market gap (no one scores tools intelligently)
- Direct cost savings for agents
- Natural extension of Knee
- Works with existing MCP ecosystem
- High feasibility

---

*End of report*
