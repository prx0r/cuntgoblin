"""Research packet generation."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.research import ResearchPacket, Competitor, ResearchPaper
from scoring.engine import search_github, search_arxiv


class ResearchGenerator:
    """Generate research packets for ideas."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, idea_id: str, idea_text: str) -> ResearchPacket:
        """Generate a research packet for an idea."""
        # Search GitHub for competitors
        github = search_github(idea_text)
        competitors = [
            Competitor(
                name=r.get("name", ""),
                description=r.get("description", ""),
                stars=r.get("stars", 0),
            )
            for r in github if "error" not in r
        ]
        
        # Search arxiv for papers
        arxiv = search_arxiv(idea_text)
        papers = [
            ResearchPaper(
                title=r.get("title", ""),
            )
            for r in arxiv if "error" not in r
        ]
        
        # Create research packet
        packet = ResearchPacket(
            idea_id=idea_id,
            customer="To be determined",
            pain="To be determined",
            wedge="To be determined",
            competitors=competitors,
            papers=papers,
            feasibility_notes=f"Found {len(competitors)} similar projects, {len(papers)} papers",
            similar_projects=[c.name for c in competitors],
            sources=["github", "arxiv"],
        )
        
        return packet
    
    def save(self, packet: ResearchPacket):
        """Save research packet to file."""
        filepath = self.output_dir / f"{packet.idea_id}.json"
        with open(filepath, "w") as f:
            json.dump(packet.to_dict(), f, indent=2)
        
        return filepath
