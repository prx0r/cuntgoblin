"""Hacker News adapter - fetches developer community activity."""

import json
import urllib.request
from typing import List, Dict

from .base import BaseAdapter


class HackerNewsAdapter(BaseAdapter):
    """Adapter for Hacker News API."""
    
    def __init__(self):
        super().__init__("hackernews", "Hacker News")
        self.base_url = "https://hacker-news.firebaseio.com/v0"
    
    async def fetch_observations(self) -> List[Dict]:
        """Fetch observations from Hacker News."""
        observations = []
        
        # Fetch top stories
        try:
            url = f"{self.base_url}/topstories.json"
            req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            story_ids = json.loads(resp.read())[:10]
            
            for story_id in story_ids:
                story_url = f"{self.base_url}/item/{story_id}.json"
                req = urllib.request.Request(story_url, headers={"User-Agent": "venturelab/1.0"})
                resp = urllib.request.urlopen(req, timeout=30)
                story = json.loads(resp.read())
                
                content = {
                    "story_id": story_id,
                    "title": story.get("title"),
                    "score": story.get("score"),
                    "url": story.get("url"),
                    "by": story.get("by"),
                }
                observations.append(self.create_observation(content, story_url))
        except Exception as e:
            observations.append({
                "observation_id": f"obs_error_{hashlib.sha256(str(e).encode()).hexdigest()[:12]}",
                "error": str(e),
                "observed_at": datetime.now(timezone.utc).isoformat(),
            })
        
        return observations
