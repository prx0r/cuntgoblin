"""Market Intelligence Layer.

Append-only evidence system for market observations.
Similar to Dell's canonical_db but for markets.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional


class MarketIntelligence:
    """Market intelligence layer."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.observations = []
        self.claims = []
    
    def add_observation(self, source_type: str, source_url: str, content: Dict) -> str:
        """Add a market observation."""
        observation_id = f"obs_{hashlib.sha256(json.dumps(content).encode()).hexdigest()[:12]}"
        
        observation = {
            "observation_id": observation_id,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "source": {
                "type": source_type,
                "url": source_url,
                "authority": "primary",
            },
            "artifact_sha256": hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest(),
            "extractor_version": f"{source_type}-v1",
        }
        
        self.observations.append(observation)
        return observation_id
    
    def add_claim(self, subject: str, predicate: str, obj: Any, observation_id: str, confidence: float = 0.9) -> str:
        """Add a claim extracted from observation."""
        claim_id = f"claim_{hashlib.sha256(f'{subject}{predicate}{obj}'.encode()).hexdigest()[:12]}"
        
        claim = {
            "claim_id": claim_id,
            "subject": subject,
            "predicate": predicate,
            "object": obj,
            "state": "KNOWN",
            "evidence": [observation_id],
            "confidence": confidence,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        self.claims.append(claim)
        return claim_id
    
    def query_claims(self, subject: Optional[str] = None, predicate: Optional[str] = None) -> List[Dict]:
        """Query claims by subject and/or predicate."""
        results = self.claims
        
        if subject:
            results = [c for c in results if c["subject"] == subject]
        if predicate:
            results = [c for c in results if c["predicate"] == predicate]
        
        return results
    
    def get_knowledge_graph(self) -> Dict:
        """Get the knowledge graph."""
        return {
            "observations": self.observations,
            "claims": self.claims,
            "stats": {
                "total_observations": len(self.observations),
                "total_claims": len(self.claims),
            },
        }
    
    def save(self):
        """Save to disk."""
        data = self.get_knowledge_graph()
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load from disk."""
        if self.db_path.exists():
            with open(self.db_path, encoding="utf-8") as f:
                data = json.load(f)
            self.observations = data.get("observations", [])
            self.claims = data.get("claims", [])
