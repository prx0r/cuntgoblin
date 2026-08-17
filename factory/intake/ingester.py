"""Idea ingestion from multiple sources."""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.idea import Idea, Score


class IdeaIngester:
    """Ingest ideas from multiple sources."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def ingest_from_text(self, text: str, source: str = "manual") -> Idea:
        """Ingest an idea from text."""
        # Generate ID from content
        idea_id = f"idea_{hashlib.md5(text.encode()).hexdigest()[:8]}"
        
        # Parse idea from text
        lines = text.strip().split("\n")
        title = lines[0] if lines else "Untitled"
        description = "\n".join(lines[1:]) if len(lines) > 1 else ""
        
        idea = Idea(
            id=idea_id,
            title=title,
            description=description,
            source=source,
            status="inbox",
        )
        
        return idea
    
    def ingest_from_json(self, data: Dict) -> Idea:
        """Ingest an idea from JSON."""
        return Idea.from_dict(data)
    
    def ingest_batch(self, ideas: List[Dict]) -> List[Idea]:
        """Ingest multiple ideas."""
        return [self.ingest_from_json(idea) for idea in ideas]
    
    def deduplicate(self, ideas: List[Idea]) -> List[Idea]:
        """Remove duplicate ideas based on title similarity."""
        seen = set()
        unique = []
        
        for idea in ideas:
            # Normalize title for comparison
            normalized = idea.title.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                unique.append(idea)
        
        return unique
    
    def cluster_ideas(self, ideas: List[Idea]) -> Dict[str, List[Idea]]:
        """Cluster ideas by similarity."""
        clusters = {}
        
        for idea in ideas:
            # Simple clustering based on keywords
            keywords = set(idea.title.lower().split())
            
            # Find matching cluster
            matched = False
            for cluster_key, cluster_ideas in clusters.items():
                cluster_keywords = set(cluster_key.split())
                overlap = len(keywords & cluster_keywords)
                if overlap >= 2:  # At least 2 keywords in common
                    cluster_ideas.append(idea)
                    matched = True
                    break
            
            if not matched:
                # Create new cluster
                clusters[idea.title.lower()] = [idea]
        
        return clusters
