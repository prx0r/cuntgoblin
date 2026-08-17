"""Signal Engine - computes signals from market observations."""

import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


def robust_zscore(values: List[float], threshold: float = 3.0) -> Optional[float]:
    """Compute robust z-score using median absolute deviation."""
    if len(values) < 3:
        return None
    
    median = sorted(values)[len(values) // 2]
    mad = sorted([abs(v - median) for v in values])[len(values) // 2]
    
    if mad == 0:
        return None
    
    return (values[-1] - median) / (1.4826 * mad)


def log_growth(current: float, previous: float) -> float:
    """Compute log growth rate (robust to zero)."""
    if previous <= 0:
        return math.log1p(current) if current > 0 else 0.0
    return math.log(current / previous)


def compute_velocity(values: List[float], window: int = 7) -> float:
    """Compute velocity (recent trend)."""
    if len(values) < 2:
        return 0.0
    recent = values[-window:] if len(values) >= window else values
    return log_growth(recent[-1], recent[0]) if len(recent) >= 2 else 0.0


def compute_acceleration(values: List[float], window: int = 7) -> float:
    """Compute acceleration (change in velocity)."""
    if len(values) < window * 2:
        return 0.0
    v1 = compute_velocity(values[:len(values)//2], window)
    v2 = compute_velocity(values[len(values)//2:], window)
    return v2 - v1


def compute_burst(values: List[float], threshold: float = 3.0) -> bool:
    """Detect burst using robust z-score."""
    z = robust_zscore(values, threshold)
    return z is not None and z > threshold


def compute_persistence(values: List[float], threshold: float = 0.5) -> float:
    """Compute persistence (fraction of time above threshold)."""
    if not values:
        return 0.0
    above = sum(1 for v in values if v > threshold)
    return above / len(values)


def compute_source_breadth(sources: List[str]) -> float:
    """Compute source breadth (unique sources / total)."""
    if not sources:
        return 0.0
    unique = len(set(sources))
    return unique / len(sources)


class SignalEngine:
    """Signal engine for market observations."""
    
    def compute_signals(self, observations: List[Dict]) -> Dict[str, Any]:
        """Compute signals from observations."""
        # Group by topic
        topics = {}
        for obs in observations:
            topic = obs.get("topic", "unknown")
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(obs)
        
        signals = {}
        for topic, topic_obs in topics.items():
            # Extract values
            values = [o.get("value", 0) for o in topic_obs if "value" in o]
            sources = [o.get("source", {}).get("type", "unknown") for o in topic_obs]
            
            signals[topic] = {
                "velocity": compute_velocity(values),
                "acceleration": compute_acceleration(values),
                "burst": compute_burst(values),
                "persistence": compute_persistence(values),
                "source_breadth": compute_source_breadth(sources),
                "observation_count": len(topic_obs),
            }
        
        return signals
