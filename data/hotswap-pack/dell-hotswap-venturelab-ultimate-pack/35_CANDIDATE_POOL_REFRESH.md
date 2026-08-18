# Candidate Pool Refresh

HotSwap pools are dynamic because Dell changes.

Refresh on:
- new model
- new offer
- price change
- free tier change
- promo start/end
- quota change
- endpoint health change
- task-quality evidence change

## Pool generation

For each task cell:
1. hard-filter Dell routes;
2. include cheapest free sufficient routes;
3. include cheapest paid sufficient;
4. include reliable strong escalation;
5. include one high-information experimental candidate;
6. Pareto prune;
7. cap at configured size.

## Do not pin names forever

Factory policy says:
`coding_patch quality>=.76`

not:
`always use model X`.

Dell + local outcomes decide the actual model.
