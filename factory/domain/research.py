"""Research packet domain model."""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timezone
import json


@dataclass
class Competitor:
    """A competitor."""
    name: str
    description: str
    url: Optional[str] = None
    stars: Optional[int] = None
    gap: Optional[str] = None


@dataclass
class ResearchPaper:
    """A research paper."""
    title: str
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    url: Optional[str] = None
    key_finding: Optional[str] = None


@dataclass
class ResearchPacket:
    """Complete research packet for an idea."""
    idea_id: str
    
    # Thesis
    customer: str = ""
    pain: str = ""
    wedge: str = ""
    
    # Market
    market_size: Optional[float] = None
    market_growth: Optional[float] = None
    
    # Competitors
    competitors: List[Competitor] = field(default_factory=list)
    
    # Research papers
    papers: List[ResearchPaper] = field(default_factory=list)
    
    # Technical feasibility
    feasibility_notes: str = ""
    similar_projects: List[str] = field(default_factory=list)
    
    # Monetization
    monetization_model: str = ""
    pricing: str = ""
    buyers: List[str] = field(default_factory=list)
    
    # Risks
    risks: List[str] = field(default_factory=list)
    
    # Sources
    sources: List[str] = field(default_factory=list)
    
    # Timestamp
    researched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "idea_id": self.idea_id,
            "customer": self.customer,
            "pain": self.pain,
            "wedge": self.wedge,
            "market_size": self.market_size,
            "market_growth": self.market_growth,
            "competitors": [{"name": c.name, "description": c.description, "gap": c.gap} for c in self.competitors],
            "papers": [{"title": p.title, "year": p.year, "key_finding": p.key_finding} for p in self.papers],
            "feasibility_notes": self.feasibility_notes,
            "similar_projects": self.similar_projects,
            "monetization_model": self.monetization_model,
            "pricing": self.pricing,
            "buyers": self.buyers,
            "risks": self.risks,
            "sources": self.sources,
            "researched_at": self.researched_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ResearchPacket":
        """Create from dictionary."""
        competitors = [Competitor(**c) for c in data.get("competitors", [])]
        papers = [ResearchPaper(**p) for p in data.get("papers", [])]
        return cls(
            idea_id=data["idea_id"],
            customer=data.get("customer", ""),
            pain=data.get("pain", ""),
            wedge=data.get("wedge", ""),
            market_size=data.get("market_size"),
            market_growth=data.get("market_growth"),
            competitors=competitors,
            papers=papers,
            feasibility_notes=data.get("feasibility_notes", ""),
            similar_projects=data.get("similar_projects", []),
            monetization_model=data.get("monetization_model", ""),
            pricing=data.get("pricing", ""),
            buyers=data.get("buyers", []),
            risks=data.get("risks", []),
            sources=data.get("sources", []),
            researched_at=data.get("researched_at", datetime.now(timezone.utc).isoformat()),
        )
