"""Product domain model."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime, timezone
import json


@dataclass
class ProductMetrics:
    """Product metrics."""
    unique_users: int = 0
    api_calls: int = 0
    returning_users: int = 0
    revenue: float = 0.0
    latency_p50: float = 0.0
    error_rate: float = 0.0


@dataclass
class Product:
    """A product derived from an idea."""
    id: str
    name: str
    description: str
    stage: str = "idea"  # idea, research, experiment, mvp, published, deployed
    
    # Source
    idea_id: Optional[str] = None
    
    # Repository
    repo_url: Optional[str] = None
    repo_sha: Optional[str] = None
    
    # Deployment
    deploy_url: Optional[str] = None
    deploy_status: str = "not_deployed"
    
    # Certificate
    certificate_status: str = "pending"  # pending, pass, fail
    certificate_details: Optional[dict] = None
    
    # Metrics
    metrics: ProductMetrics = field(default_factory=ProductMetrics)
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "stage": self.stage,
            "idea_id": self.idea_id,
            "repo_url": self.repo_url,
            "repo_sha": self.repo_sha,
            "deploy_url": self.deploy_url,
            "deploy_status": self.deploy_status,
            "certificate_status": self.certificate_status,
            "metrics": {
                "unique_users": self.metrics.unique_users,
                "api_calls": self.metrics.api_calls,
                "returning_users": self.returning_users,
                "revenue": self.metrics.revenue,
            },
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Create from dictionary."""
        metrics_data = data.get("metrics", {})
        metrics = ProductMetrics(
            unique_users=metrics_data.get("unique_users", 0),
            api_calls=metrics_data.get("api_calls", 0),
            returning_users=metrics_data.get("returning_users", 0),
            revenue=metrics_data.get("revenue", 0.0),
        )
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            stage=data.get("stage", "idea"),
            idea_id=data.get("idea_id"),
            repo_url=data.get("repo_url"),
            repo_sha=data.get("repo_sha"),
            deploy_url=data.get("deploy_url"),
            deploy_status=data.get("deploy_status", "not_deployed"),
            certificate_status=data.get("certificate_status", "pending"),
            metrics=metrics,
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
        )
