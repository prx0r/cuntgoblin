"""Oracle Registry - manages oracle providers and their connectors."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional


class OracleManifest:
    """Manifest for an oracle provider."""
    
    def __init__(self, oracle_id: str, name: str, source_families: List[str]):
        self.oracle_id = oracle_id
        self.name = name
        self.source_families = source_families
        self.status = "active"
        self.created_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "oracle_id": self.oracle_id,
            "name": self.name,
            "source_families": self.source_families,
            "status": self.status,
            "created_at": self.created_at,
        }


class OracleRegistry:
    """Registry for oracle providers."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.oracles: Dict[str, OracleManifest] = {}
        self.load()
    
    def register(self, oracle: OracleManifest):
        """Register an oracle."""
        self.oracles[oracle.oracle_id] = oracle
        self.save()
    
    def get(self, oracle_id: str) -> Optional[OracleManifest]:
        """Get an oracle by ID."""
        return self.oracles.get(oracle_id)
    
    def list_all(self) -> List[OracleManifest]:
        """List all oracles."""
        return list(self.oracles.values())
    
    def query_by_source_family(self, source_family: str) -> List[OracleManifest]:
        """Query oracles by source family."""
        return [o for o in self.oracles.values() if source_family in o.source_families]
    
    def save(self):
        """Save to disk."""
        data = {oid: o.to_dict() for oid, o in self.oracles.items()}
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load from disk."""
        if self.db_path.exists():
            with open(self.db_path, encoding="utf-8") as f:
                data = json.load(f)
            for oid, odata in data.items():
                self.oracles[oid] = OracleManifest(
                    oracle_id=odata["oracle_id"],
                    name=odata["name"],
                    source_families=odata["source_families"],
                )
                self.oracles[oid].status = odata.get("status", "active")
