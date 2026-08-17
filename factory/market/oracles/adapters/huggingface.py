"""Hugging Face adapter - fetches model data from Hugging Face."""

import json
import urllib.request
from typing import List, Dict

from .base import BaseAdapter


class HuggingFaceAdapter(BaseAdapter):
    """Adapter for Hugging Face API."""
    
    def __init__(self):
        super().__init__("huggingface", "Hugging Face")
        self.base_url = "https://huggingface.co/api"
    
    async def fetch_observations(self) -> List[Dict]:
        """Fetch observations from Hugging Face."""
        observations = []
        
        # Fetch trending models
        try:
            url = f"{self.base_url}/models?sort=downloads&direction=desc&limit=10"
            req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            
            for model in data:
                content = {
                    "model_id": model.get("id"),
                    "downloads": model.get("downloads"),
                    "likes": model.get("likes"),
                    "pipeline_tag": model.get("pipeline_tag"),
                }
                observations.append(self.create_observation(content, url))
        except Exception as e:
            observations.append({
                "observation_id": f"obs_error_{hashlib.sha256(str(e).encode()).hexdigest()[:12]}",
                "error": str(e),
                "observed_at": datetime.now(timezone.utc).isoformat(),
            })
        
        return observations
