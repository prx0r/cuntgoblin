# Deterministic Orchestration Simulator

Purpose:

Cheaply compare coordination plans before spending inference.

Inspired by OrchBench's principle of isolating orchestration quality from worker quality.

## Input

A DAG where every node has:
- duration units
- token cost
- critical information requirement

Edges specify:
- information transfer
- retention ratio

Planner output specifies:
- worker assignment
- ordering
- transfer policy

## Metrics

- makespan
- total token cost
- information survival
- coordination load
- worker utilization

## Important limitation

This simulator is a structural proxy.

It cannot prove that a real LLM worker will perform correctly.

Use:
`simulation → candidate pruning → real benchmark`.

Never publish simulation score as real task success.
