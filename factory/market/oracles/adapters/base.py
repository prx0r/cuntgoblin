"""Base adapter for oracle providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import hashlib
import json


class BaseAdapter(ABC):
    """Base class for oracle adapters."""
    
    def __init__(self, oracle_id: str, name: str):
        self.oracle_id = oracle_id
        self.name = name
    
    @abstractmethod
    async def fetch_observations(self) -> List[Dict]:
        """Fetch observations from the source."""
        pass
    
    def compute_hash(self, data: Dict) -> str:
        """Compute content hash for observation."""
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def create_observation(self, content: Dict, source_url: str) -> Dict:
        """Create a standardized observation."""
        return {
            "observation_id": f"obs_{self.compute_hash(content)[:12]}",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "source": {
                "type": self.oracle_id,
                "url": source_url,
                "authority": "primary",
            },
            "artifact_sha256": self.compute_hash(content),
            "extractor_version": f"{self.oracle_id}-v1",
        }
