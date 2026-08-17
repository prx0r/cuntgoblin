"""mcp/server.py — MCP (Model Context Protocol) stdio server for AgentSLA.

Spec Product 2 MCP tools:
    architecture_profile   SLA summary for one architecture (+ optional task class)
    architecture_compare   side-by-side SLA comparison of architectures
    task_economics         cost/success frontier for a task class

Implements the MCP JSON-RPC 2.0 stdio protocol by hand (no framework): newline-
delimited JSON-RPC requests with initialize / notifications/initialized /
tools/list / tools/call. Reads the same SQLite SLA database as the API.

Run:  python mcp/server.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.db import connect  # noqa: E402
from app.metrics import RunRow, knee_from_runs, sla_summary  # noqa: E402

DB_PATH = BASE_DIR / "data" / "agentsla.db"

TOOLS = [
    {
        "name": "architecture_profile",
        "description": "SLA summary (success rate, cost per success, duration, efficiency) for an architecture.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "architecture_id": {"type": "string"},
                "task_class": {"type": "string", "enum": ["coding.patch", "coding.debug", "research.answer"]},
            },
            "required": ["architecture_id"],
        },
    },
    {
        "name": "architecture_compare",
        "description": "Compare SLA metrics across architectures for one task class.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_class": {"type": "string", "enum": ["coding.patch", "coding.debug", "research.answer"]},
                "architecture_ids": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["task_class"],
        },
    },
    {
        "name": "task_economics",
        "description": "Cost/success frontier for a task class with Wilson confidence bounds.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_class": {"type": "string", "enum": ["coding.patch", "coding.debug", "research.answer"]},
                "min_success": {"type": "number", "default": 0.8},
            },
            "required": ["task_class"],
        },
    },
]


class Server:
    def __init__(self):
        self.conn = connect(DB_PATH)

    def _rows_for(self, architecture_id: str, task_class: str | None):
        query = """SELECT r.* FROM runs r
                   JOIN architecture_versions av ON av.architecture_version_id = r.architecture_version_id
                   JOIN task_versions tv ON tv.task_version_id = r.task_version_id
                   JOIN tasks t ON t.task_id = tv.task_id
                   WHERE av.architecture_id = ? AND r.status != 'running'"""
        params = [architecture_id]
        if task_class:
            query += " AND t.task_class = ?"
            params.append(task_class)
        return self.conn.execute(query, params).fetchall()

    def _run_rows(self, db_rows) -> list[RunRow]:
        return [
            RunRow(
                success=bool(r["success"]) if r["success"] is not None else False,
                cost_usd=float(r["cost_usd"] or 0.0),
                duration_seconds=float(r["duration_seconds"] or 0.0),
                input_tokens=int(r["input_tokens"] or 0),
                output_tokens=int(r["output_tokens"] or 0),
                tool_calls=int(r["tool_calls"] or 0),
                retries=int(r["retries"] or 0),
            )
            for r in db_rows
        ]

    def _summarize(self, architecture_id: str, task_class: str | None) -> dict:
        s = sla_summary(self._run_rows(self._rows_for(architecture_id, task_class)))
        return {
            "architecture_id": architecture_id,
            "task_class": task_class,
            "n": s.n, "successes": s.successes, "success_rate": s.success_rate,
            "wilson_lb": s.success_rate_ci[0], "wilson_ub": s.success_rate_ci[1],
            "cost_per_attempt_usd": s.cost_per_attempt, "cost_per_success_usd": s.cost_per_success,
            "duration_per_success_seconds": s.duration_per_success,
            "tokens_per_success": s.tokens_per_success,
            "tool_calls_per_success": s.tool_calls_per_success, "retry_rate": s.retry_rate,
            "efficiency": s.efficiency, "insufficient_evidence": s.insufficient_evidence,
        }

    def handle(self, req: dict) -> dict | None:
        method = req.get("method")
        rid = req.get("id")
        params = req.get("params") or {}
        if method == "initialize":
            return {
                "jsonrpc": "2.0", "id": rid,
                "result": {
                    "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "agentsla-mcp", "version": "0.1.0"},
                },
            }
        if method == "notifications/initialized":
            return None
        if method == "ping":
            return {"jsonrpc": "2.0", "id": rid, "result": {}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
        if method == "tools/call":
            tool = (params.get("name") or "").replace("mcp__agentsla__", "")
            args = params.get("arguments") or {}
            try:
                result = self._call_tool(tool, args)
                return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(result, default=str)}]}}
            except Exception as exc:  # noqa: BLE001
                return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32000, "message": str(exc)}}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"unknown method {method}"}}

    def _call_tool(self, tool: str, args: dict):
        if tool == "architecture_profile":
            return self._summarize(args["architecture_id"], args.get("task_class"))
        if tool == "architecture_compare":
            task_class = args["task_class"]
            ids = args.get("architecture_ids") or [
                r["architecture_id"] for r in self.conn.execute("SELECT DISTINCT architecture_id FROM architectures").fetchall()
            ]
            return {"task_class": task_class, "compare": {aid: self._summarize(aid, task_class) for aid in ids}}
        if tool == "task_economics":
            task_class = args["task_class"]
            min_success = float(args.get("min_success", 0.8))
            grouped = []
            for row in self.conn.execute("SELECT DISTINCT architecture_id FROM architectures").fetchall():
                aid = row["architecture_id"]
                s = sla_summary(self._run_rows(self._rows_for(aid, task_class)))
                if s.n:
                    grouped.append((aid, s))
            if not grouped:
                return {"task_class": task_class, "status": "INSUFFICIENT_EVIDENCE", "candidates": []}
            return {"task_class": task_class, "min_success": min_success, **knee_from_runs(grouped, min_success)}
        raise ValueError(f"unknown tool {tool}")

    def loop(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except json.JSONDecodeError:
                continue
            resp = self.handle(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    Server().loop()