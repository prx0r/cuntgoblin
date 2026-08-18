from __future__ import annotations


def agent_card(system_id: str, name: str, endpoint: str, skills: list[dict]) -> dict:
    return {
        "name":name,
        "description":f"AgentHub build for {system_id}",
        "url":endpoint,
        "version":"1.0.0",
        "capabilities":{"streaming":True},
        "skills":skills,
    }


def assessment_request(participants: dict[str,str], config: dict | None = None) -> dict:
    return {
        "participants":participants,
        "config":config or {},
    }
