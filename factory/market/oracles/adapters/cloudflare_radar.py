"""Cloudflare Radar adapter - fetches domain popularity data."""

import json
import urllib.request
from typing import List, Dict

from .base import BaseAdapter


class CloudflareRadarAdapter(BaseAdapter):
    """Adapter for Cloudflare Radar API."""
    
    def __init__(self):
        super().__init__("cloudflare_radar", "Cloudflare Radar")
        self.base_url = "https://api.cloudflare.com/client/v4/radar"
    
    async def fetch_observations(self) -> List[Dict]:
        """Fetch observations from Cloudflare Radar."""
        observations = []
        
        # Fetch top domains
        try:
            url = f"{self.base_url}/ranking/top?limit=10"
            req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            
            for domain in data.get("result", {}).get("top", []):
                content = {
                    "domain": domain.get("domain"),
                    "rank": domain.get("rank"),
                    "score": domain.get("score"),
                }
                observations.append(self.create_observation(content, url))
        except Exception as e:
            observations.append({
                "observation_id": f"obs_error_{hashlib.sha256(str(e).encode()).hexdigest()[:12]}",
                "error": str(e),
                "observed_at": datetime.now(timezone.utc).isoformat(),
            })
        
        return observations
