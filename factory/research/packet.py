"""Research packet generation."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from factory.domain.research import ResearchPacket, Competitor, ResearchPaper
from factory.sources.github import search_github
from factory.sources.arxiv import search_arxiv
from factory.sources import SourceUnavailable


class ResearchGenerator:
    """Generate research packets for ideas."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, idea_id: str, idea_text: str) -> ResearchPacket:
        """Generate a research packet for an idea."""
        # Search GitHub for competitors (source failure != zero results)
        try:
            github = search_github(idea_text)
        except SourceUnavailable:
            github = None

        competitors = [
            Competitor(
                name=r.get("name", ""),
                description=r.get("description", ""),
                stars=r.get("stars", 0),
            )
            for r in (github.items if github else [])
        ]

        # Search arxiv for papers
        try:
            arxiv = search_arxiv(idea_text)
        except SourceUnavailable:
            arxiv = None

        papers = [
            ResearchPaper(
                title=r.get("title", ""),
            )
            for r in (arxiv.items if arxiv else [])
        ]

        # Track which sources actually responded
        source_status = []
        if github is not None:
            source_status.append(f"github={'ok' if github.ok else github.error}")
        else:
            source_status.append("github=unavailable")
        if arxiv is not None:
            source_status.append(f"arxiv={'ok' if arxiv.ok else arxiv.error}")
        else:
            source_status.append("arxiv=unavailable")

        packet = ResearchPacket(
            idea_id=idea_id,
            customer="To be determined",
            pain="To be determined",
            wedge="To be determined",
            competitors=competitors,
            papers=papers,
            feasibility_notes=f"Found {len(competitors)} similar projects, {len(papers)} papers. Sources: {', '.join(source_status)}",
            similar_projects=[c.name for c in competitors],
            sources=source_status,
        )

        return packet
    
    def save(self, packet: ResearchPacket):
        """Save research packet to file."""
        filepath = self.output_dir / f"{packet.idea_id}.json"
        with open(filepath, "w") as f:
            json.dump(packet.to_dict(), f, indent=2)
        
        return filepath
