# Repository Evidence Ledger

Reviewed `master` head `a56716251f4c60a2593e71efc6c88c5c61beb5bf`.

| Path | Blob SHA | Finding |
|---|---|---|
| `README.md` | `054ce8892599c9b06d6c174052864bbbf86d0f3a` | legacy venture pipeline |
| `agent/run.py` | `569545d56faad9c71ebee9b403b9c0a880414ac1` | brittle count-based research/stub |
| `api.py` | `8ad241cd31c633cb457437d03ac72577af7b340d` | imports missing core |
| `Dockerfile` | `6562939a768b2d596875b231fd3ac619c5fdc073` | starts missing core |
| `.github/workflows/ci.yml` | `c835f4c813e172b467b24351d1dd622d1f1d2f15` | fragmented/reference-pack tests |
| `factory/global_os/go.py` | `c3767cff30cef95bb933649f88d954f345ce3d0b` | imports absent siblings |
| `factory/scoring/engine.py` | `e96adcfbe9fe7e1b3b4cb00ede72ac099643fd03` | hardcoded defaults; no search helpers |
| `factory/research/packet.py` | `baf1bd140cd810f49bf030ffb68d3166c82b5640` | imports absent search helpers |
| `factory/hotswap/router.py` | `64c0ac7d0b9af5ef0fe2103a1325f678c960caf5` | strongest subsystem |
| `factory/hotswap/integration.py` | `ab87c7bedc4eb073286be150db4d1c4a61cb0171` | planning only/disconnected stores |
| `factory/hotswap/types.py` | `1b7bdd77d38ec8bf6a917878f2dd4f7fddf4a694` | good contracts |
| `factory/market/market_algorithms.py` | `312c82110bc8cd767476d682351d058adf9f8b97` | strong genesis/VOI policies |
| `mcp/server.py` | `59ac20fd896078ded0f86f596c92910fcbb5fe6a` | handwritten MCP dispatcher |

## Verification limit

This was a GitHub-connected static source review. The artifact runtime did not establish a local network clone, so this dossier does not claim local execution. The missing-import/module failures above are nevertheless directly established by the inspected tree/source.

GitHub returned no status checks/workflow runs attached to the reviewed head during inspection.
