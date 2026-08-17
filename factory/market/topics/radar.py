"""Topic Radar - candidate generation from market observations."""

from typing import List, Dict, Any
from datetime import datetime, timezone


class TopicRadar:
    """Radar for detecting emerging market topics."""
    
    def __init__(self):
        self.topics = {}
    
    def extract_topics(self, observations: List[Dict]) -> List[Dict]:
        """Extract topics from observations."""
        topics = {}
        
        for obs in observations:
            # Extract keywords from content
            content = obs.get("content", {})
            keywords = self._extract_keywords(content)
            
            for keyword in keywords:
                if keyword not in topics:
                    topics[keyword] = {
                        "keyword": keyword,
                        "count": 0,
                        "sources": set(),
                        "first_seen": obs.get("observed_at"),
                        "last_seen": obs.get("observed_at"),
                    }
                
                topics[keyword]["count"] += 1
                topics[keyword]["sources"].add(obs.get("source", {}).get("type", "unknown"))
                topics[keyword]["last_seen"] = obs.get("observed_at")
        
        # Convert sets to lists for JSON
        result = []
        for topic in topics.values():
            topic["sources"] = list(topic["sources"])
            result.append(topic)
        
        return sorted(result, key=lambda x: x["count"], reverse=True)
    
    def _extract_keywords(self, content: Dict) -> List[str]:
        """Extract keywords from content."""
        keywords = []
        
        # Extract from string values
        for key, value in content.items():
            if isinstance(value, str) and len(value) > 3:
                keywords.append(value.lower())
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and len(item) > 3:
                        keywords.append(item.lower())
        
        return keywords
    
    def score_topic(self, topic: Dict) -> float:
        """Score a topic based on signals."""
        score = 0.0
        
        # Count signal
        score += min(topic["count"] / 10, 1.0) * 0.3
        
        # Source breadth signal
        source_breadth = len(topic["sources"]) / 5
        score += min(source_breadth, 1.0) * 0.3
        
        # Recency signal
        if topic["last_seen"]:
            try:
                last_seen = datetime.fromisoformat(topic["last_seen"].replace("Z", "+00:00"))
                days_ago = (datetime.now(timezone.utc) - last_seen).days
                recency = max(0, 1 - days_ago / 30)
                score += recency * 0.4
            except:
                pass
        
        return min(score, 1.0)
