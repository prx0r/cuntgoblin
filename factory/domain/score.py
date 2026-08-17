"""Score domain model with deterministic scoring."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timezone
import json


@dataclass
class ScoreDimension:
    """A single scoring dimension with evidence."""
    name: str
    weight: float
    score: float  # 0-1
    confidence: float  # 0-1
    evidence: List[str] = field(default_factory=list)
    method: str = ""
    checked_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "weight": self.weight,
            "score": self.score,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "method": self.method,
            "checked_at": self.checked_at,
        }


@dataclass
class Scorecard:
    """Complete scorecard for an idea."""
    idea_id: str
    dimensions: List[ScoreDimension] = field(default_factory=list)
    overall_score: float = 0.0
    overall_confidence: float = 0.0
    scored_at: Optional[str] = None
    
    def calculate_overall(self):
        """Calculate weighted overall score."""
        if not self.dimensions:
            self.overall_score = 0.0
            self.overall_confidence = 0.0
            return
        
        total_weight = sum(d.weight for d in self.dimensions)
        if total_weight == 0:
            self.overall_score = 0.0
            self.overall_confidence = 0.0
            return
        
        weighted_sum = sum(d.score * d.weight for d in self.dimensions)
        confidence_sum = sum(d.confidence * d.weight for d in self.dimensions)
        
        self.overall_score = weighted_sum / total_weight
        self.overall_confidence = confidence_sum / total_weight
        self.scored_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> dict:
        return {
            "idea_id": self.idea_id,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "overall_score": self.overall_score,
            "overall_confidence": self.overall_confidence,
            "scored_at": self.scored_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Scorecard":
        dimensions = [ScoreDimension(**d) for d in data.get("dimensions", [])]
        return cls(
            idea_id=data["idea_id"],
            dimensions=dimensions,
            overall_score=data.get("overall_score", 0.0),
            overall_confidence=data.get("overall_confidence", 0.0),
            scored_at=data.get("scored_at"),
        )
