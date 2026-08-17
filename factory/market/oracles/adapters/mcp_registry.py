"""MCP Registry adapter - fetches MCP server data."""

import json
import urllib.request
from typing import List, Dict

from .base import BaseAdapter


class MCPRegistryAdapter(BaseAdapter):
    """Adapter for MCP Registry API."""
    
    def __init__(self):
        super().__init__("mcp_registry", "MCP Registry")
        self.base_url = "https://registry.modelcontextprotocol.io"
    
    async def fetch_observations(self) -> List[Dict]:
        """Fetch observations from MCP Registry."""
        observations = []
        
        # Fetch MCP servers
        try:
            url = f"{self.base_url}/servers?limit=10"
            req = urllib.request.Request(url, headers={"User-Agent": "venturelab/1.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            
            for server in data.get("servers", []):
                content = {
                    "server_id": server.get("id"),
                    "name": server.get("name"),
                    "description": server.get("description"),
                    "tools": server.get("tools", []),
                }
                observations.append(self.create_observation(content, url))
        except Exception as e:
            observations.append({
                "observation_id": f"obs_error_{hashlib.sha256(str(e).encode()).hexdigest()[:12]}",
                "error": str(e),
                "observed_at": datetime.now(timezone.utc).isoformat(),
            })
        
        return observations
