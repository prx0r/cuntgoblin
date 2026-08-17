"""ecosyste.ms adapter - fetches package ecosystem data."""

import json
import urllib.request
from typing import List, Dict

from .base import BaseAdapter


class EcosystemsAdapter(BaseAdapter):
    """Adapter for ecosyste.ms API."""
    
    def __init__(self):
        super().__init__("ecosystems", "ecosyste.ms")
        self.base_url = "https://ecosyste.ms/api/v1"
    
    async def fetch_observations(self) -> List[Dict]:
        """Fetch observations from ecosyste.ms."""
        observations = []
        
        # Fetch trending packages
        try:
            url = f"{self.base_url}/packages?sort=downloads&order=desc&per_page=10"
            req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            
            for package in data:
                content = {
                    "package_name": package.get("name"),
                    "ecosystem": package.get("ecosystem"),
                    "downloads": package.get("downloads"),
                    "stars": package.get("stars"),
                }
                observations.append(self.create_observation(content, url))
        except Exception as e:
            observations.append({
                "observation_id": f"obs_error_{hashlib.sha256(str(e).encode()).hexdigest()[:12]}",
                "error": str(e),
                "observed_at": datetime.now(timezone.utc).isoformat(),
            })
        
        return observations
