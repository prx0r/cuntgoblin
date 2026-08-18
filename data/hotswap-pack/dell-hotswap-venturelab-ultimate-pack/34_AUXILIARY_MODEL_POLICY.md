# Hermes Auxiliary Model Routing

HotSwap should exploit auxiliary slots aggressively.

## Compression
Task kind: compress
Usually cheap/free.
Hard constraint: enough context.
Evaluator: information retention / downstream sanity checks.

## Web extraction
Task kind: source_extract
Free-first.
No need for premium coding model.

## Skill search / MCP routing
Classification/ranking cell.
Cheap low-latency route.

## Vision
Separate visual capability hard constraint.
Do not assume main model supports vision.

## Approval/scoring
If decision high impact, set higher quality floor than routine classification.

This can remove large amounts of expensive main-model usage without touching main
agent reasoning quality.
