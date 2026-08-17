"""OpenRouter adapter - fetches model pricing and availability data."""

import json
import urllib.request
from typing import List, Dict

from .base import BaseAdapter


class OpenRouterAdapter(BaseAdapter):
    """Adapter for OpenRouter API."""
    
    def __init__(self):
        super().__init__("openrouter", "OpenRouter")
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def fetch_observations(self) -> List[Dict]:
        """Fetch observations from OpenRouter."""
        observations = []
        
        # Fetch models
        try:
            url = f"{self.base_url}/models"
            req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            
            for model in data.get("data", []):
                content = {
                    "model_id": model.get("id"),
                    "name": model.get("name"),
                    "pricing": model.get("pricing", {}),
                    "context_length": model.get("context_length"),
                }
                observations.append(self.create_observation(content, url))
        except Exception as e:
            observations.append({
                "observation_id": f"obs_error_{hashlib.sha256(str(e).encode()).hexdigest()[:12]}",
                "error": str(e),
                "observed_at": datetime.now(timezone.utc).isoformat(),
            })
        
        return observations
