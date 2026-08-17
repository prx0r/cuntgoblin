"""Structured market research format."""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


class MarketResearch:
    """Structured market research entry."""
    
    def __init__(self, topic: str, vertical: str):
        self.topic = topic
        self.vertical = vertical
        self.signals = {}
        self.findings = []
        self.meta_tags = []
        self.collected_at = datetime.now(timezone.utc).isoformat()
    
    def add_signal(self, category: str, key: str, value):
        if category not in self.signals:
            self.signals[category] = {}
        self.signals[category][key] = value
    
    def add_finding(self, finding: str, source: str, confidence: float = 0.8):
        self.findings.append({
            "finding": finding,
            "source": source,
            "confidence": confidence,
            "hash": hashlib.sha256(finding.encode()).hexdigest()[:16],
        })
    
    def add_meta_tag(self, tag: str):
        if tag not in self.meta_tags:
            self.meta_tags.append(tag)
    
    def to_yaml(self) -> str:
        lines = []
        lines.append(f"topic: {self.topic}")
        lines.append(f"vertical: {self.vertical}")
        lines.append(f"collected_at: {self.collected_at}")
        lines.append("")
        lines.append("signals:")
        for category, signals in self.signals.items():
            lines.append(f"  {category}:")
            for key, value in signals.items():
                lines.append(f"    {key}: {value}")
        lines.append("")
        lines.append("findings:")
        for finding in self.findings:
            lines.append(f"  - finding: \"{finding['finding']}\"")
            lines.append(f"    source: \"{finding['source']}\"")
            lines.append(f"    confidence: {finding['confidence']}")
        lines.append("")
        lines.append(f"meta_tags: {self.meta_tags}")
        return "\n".join(lines)
    
    def save(self, filepath: str):
        with open(filepath, "w") as f:
            f.write(self.to_yaml())
