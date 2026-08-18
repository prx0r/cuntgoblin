# Paper Intake Factory

Make research-to-agent/product a first-class workflow.

```text
OpenAlex/arXiv discovery
  -> relevance / novelty / market link
  -> paper + linked repo resolution
  -> method/claim extraction
  -> reproduction classification
  -> repo exists? ------------------------+
       | yes                               | no/incomplete
       v                                   v
  Paper2Agent-style                  Paper2Code-style
  tutorial/tool extraction           code reconstruction
       |                                   |
       +----------------+------------------+
                        v
                 verified runnable method
                        |
                 MCP / library / agent
                        |
                     benchmark
                        |
                    AgentHub
                        |
              research-to-market transfer
```

Possible terminal outcomes:
- REPRODUCED_METHOD
- PAPER_AGENT
- MCP_SERVER
- REFERENCE_LIBRARY
- BENCHMARK
- RESEARCH_ONLY
- NO_REPRODUCTION

Never turn a paper title directly into a product.
