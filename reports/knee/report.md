# KNEE — Cost-Quality Cliff API

*Report generated: 2026-08-18T03:45:00Z*

---

## Thesis

For every task, there is a sweet spot where you get 95% quality at 20% cost. Going cheaper drops quality dramatically. Knee finds that elbow.

The "quality cliff" is the product. Not another router — the thing that tells routers where the cliff is.

---

## Product Spec

### Core Endpoint

```http
POST /knee
```

Input:
```json
{
  "task": "repo_bugfix",
  "models": "auto",
  "minimum_success": 0.90
}
```

Response:
```json
{
  "recommended": "cheap-model-x",
  "success_rate": 0.923,
  "cost_per_task": 0.017,
  "next_cheaper": {
    "model": "tiny-model-y",
    "success_rate": 0.694
  },
  "cliff": 0.229
}
```

### Additional Endpoints

```http
GET /knee/{task_type}
GET /knee/compare?models=a,b,c&task=x
GET /knee/history/{task_type}
POST /knee/batch
```

---

## Current Competitors

| Competitor | What They Do | Gap |
|------------|--------------|-----|
| LiteLLM | Routing, load-balancing | No quality cliff analysis |
| RouteLLM | Cost-aware routing | No knee identification |
| Artificial Analysis | Model benchmarks | No task-specific cliffs |
| OpenRouter | Unified API | No optimization layer |

---

## arXiv Research

1. **Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey** (2026)
   - Comprehensive survey of routing approaches
   - Validates the routing space is active

2. **Towards Cost-effective LLMs Routing with Batch Prompting** (2026)
   - SeqRoute optimizes global budgets
   - Shows cost/quality tradeoffs are real

3. **The Capability Frontier: Benchmarks Miss 82% of Model** (2026)
   - At matched cost, substantially lower error than conventional evaluation
   - State-of-the-art accuracy can be reproduced more cheaply

---

## GitHub Projects

| Project | Stars | What It Does |
|---------|-------|--------------|
| BerriAI/litellm | 15000 | LLM gateway with routing |
| lm-sys/RouteLLM | 3000 | LLM router framework |
| lemony-ai/cascadeflow | 4000 | Cascading runtime for agents |
| NVIDIA-NeMo/Switchyard | 1800 | Model routing |

---

## Why It's Cool

1. **Not another router** — it's the intelligence layer routers consume
2. **Empirical measurements** — not just benchmarks, real task performance
3. **Universal** — works for any model, any provider, any task
4. **Compounding data** — every measurement makes future recommendations better

---

## Monetization

1. **API pricing** — $0.001 per knee query
2. **Enterprise subscriptions** — $99/month for unlimited queries
3. **Data licensing** — sell historical cliff data to routers
4. **Integration fees** — charge for LiteLLM/OpenRouter integrations

---

## Path to Market

1. **Week 1-2**: Build MVP with 10 tasks, 20 models
2. **Week 3-4**: Add LiteLLM integration
3. **Month 2**: Launch public API
4. **Month 3**: Enterprise pilots
5. **Month 6**: Data licensing deals

---

## Final Rating

**Score: 10/10**

**Why:**
- Huge market gap (no one does this well)
- Strong research backing
- High feasibility (can build quickly)
- Excellent timing (routing market exploding)
- Natural flywheel (more data = better recommendations)
- Complementary to LiteLLM (not competitive)

---

*End of report*
