"""Idea domain model."""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timezone
import json


@dataclass
class Score:
    """A scored dimension with evidence."""
    factor: str
    score: float  # 0-1
    confidence: float  # 0-1
    evidence: List[str] = field(default_factory=list)
    checked_at: Optional[str] = None


@dataclass
class Idea:
    """A venture idea."""
    id: str
    title: str
    description: str
    source: str
    status: str = "inbox"  # inbox, researching, scored, building, experiment, mvp, published, killed
    
    # Scores
    scores: List[Score] = field(default_factory=list)
    
    # Evidence
    evidence_files: List[str] = field(default_factory=list)
    
    # Decision
    recommendation: Optional[str] = None  # BUILD, WATCH, REJECT
    confidence: Optional[float] = None
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def overall_score(self) -> float:
        """Calculate overall score from dimensions."""
        if not self.scores:
            return 0.0
        return sum(s.score for s in self.scores) / len(self.scores)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "status": self.status,
            "scores": [{"factor": s.factor, "score": s.score, "confidence": s.confidence, "evidence": s.evidence} for s in self.scores],
            "overall_score": self.overall_score(),
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Idea":
        """Create from dictionary."""
        scores = [Score(**s) for s in data.get("scores", [])]
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            source=data.get("source", ""),
            status=data.get("status", "inbox"),
            scores=scores,
            recommendation=data.get("recommendation"),
            confidence=data.get("confidence"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
        )
