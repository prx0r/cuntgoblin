"""Unignorant adapter - global reality/data graph."""

import json
import urllib.request
from typing import List, Dict

from .base import BaseAdapter


class UnignorantAdapter(BaseAdapter):
    """Adapter for Unignorant API."""
    
    def __init__(self):
        super().__init__("unignorant", "Unignorant")
        self.base_url = "https://unignorant.org/api/v1"
    
    async def fetch_observations(self) -> List[Dict]:
        """Fetch observations from Unignorant."""
        observations = []
        
        # Fetch country data
        try:
            url = f"{self.base_url}/countries?per_page=5"
            req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            
            for country in data.get("data", []):
                content = {
                    "country_code": country.get("code"),
                    "country_name": country.get("name"),
                    "indicators": country.get("indicators", {}),
                }
                observations.append(self.create_observation(content, url))
        except Exception as e:
            observations.append({
                "observation_id": f"obs_error_{hashlib.sha256(str(e).encode()).hexdigest()[:12]}",
                "error": str(e),
                "observed_at": datetime.now(timezone.utc).isoformat(),
            })
        
        return observations
