"""OpenAlex adapter - fetches research paper data."""

import json
import urllib.request
from typing import List, Dict

from .base import BaseAdapter


class OpenAlexAdapter(BaseAdapter):
    """Adapter for OpenAlex API."""
    
    def __init__(self):
        super().__init__("openalex", "OpenAlex")
        self.base_url = "https://api.openalex.org"
    
    async def fetch_observations(self) -> List[Dict]:
        """Fetch observations from OpenAlex."""
        observations = []
        
        # Fetch recent works
        try:
            url = f"{self.base_url}/works?sort=created_date:desc&per_page=10"
            req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            
            for work in data.get("results", []):
                content = {
                    "work_id": work.get("id"),
                    "title": work.get("title"),
                    "publication_date": work.get("publication_date"),
                    "cited_by_count": work.get("cited_by_count"),
                }
                observations.append(self.create_observation(content, url))
        except Exception as e:
            observations.append({
                "observation_id": f"obs_error_{hashlib.sha256(str(e).encode()).hexdigest()[:12]}",
                "error": str(e),
                "observed_at": datetime.now(timezone.utc).isoformat(),
            })
        
        return observations
