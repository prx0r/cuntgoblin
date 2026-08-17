"""MVP builder from templates."""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.product import Product


class MVPBuilder:
    """Build MVPs from templates."""
    
    def __init__(self, templates_dir: str, builds_dir: str):
        self.templates_dir = Path(templates_dir)
        self.builds_dir = Path(builds_dir)
        self.builds_dir.mkdir(parents=True, exist_ok=True)
    
    def build(self, product: Product, archetype: str = "data-oracle") -> Path:
        """Build an MVP from a template."""
        template_dir = self.templates_dir / archetype
        
        if not template_dir.exists():
            raise ValueError(f"Template {archetype} not found")
        
        # Create build directory
        build_dir = self.builds_dir / product.id
        if build_dir.exists():
            shutil.rmtree(build_dir)
        
        # Copy template
        shutil.copytree(template_dir, build_dir)
        
        # Customize with product info
        self._customize(build_dir, product)
        
        return build_dir
    
    def _customize(self, build_dir: Path, product: Product):
        """Customize template with product info."""
        # Update README
        readme = build_dir / "README.md"
        if readme.exists():
            content = readme.read_text()
            content = content.replace("{{PRODUCT_NAME}}", product.name)
            content = content.replace("{{PRODUCT_DESCRIPTION}}", product.description)
            readme.write_text(content)
        
        # Update factory.yaml if exists
        factory_yaml = build_dir / "factory.yaml"
        if factory_yaml.exists():
            content = factory_yaml.read_text()
            content = content.replace("{{PRODUCT_ID}}", product.id)
            content = content.replace("{{PRODUCT_NAME}}", product.name)
            factory_yaml.write_text(content)
