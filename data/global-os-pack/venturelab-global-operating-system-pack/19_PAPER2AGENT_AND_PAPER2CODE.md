# Paper2Agent / Paper2Code Integration

## Paper2Agent

Use as an isolated lab adapter for papers that have associated repositories/tutorials.

Expected adapter output:
- extracted runnable methods/tools
- MCP server
- tests
- coverage
- benchmark questions/results
- environment metadata
- discrepancies/failures

Run cloned research repos in sandboxed containers.

## Paper2Code-style reconstruction

When code is missing/incomplete, use paper-to-code systems as proposal generators.

Verification hierarchy:
1. repository runs;
2. described interfaces exist;
3. reproduced tables/figures/metrics where feasible;
4. compare author implementation if later available;
5. perturbation/adversarial checks.

Generated code remains `MACHINE_RECONSTRUCTION` until empirical reproduction justifies
a stronger state.

## AgentHub

A reproduced paper can become:
- tool component
- MCP server
- agent architecture component
- complete Paper Agent
- benchmark target
