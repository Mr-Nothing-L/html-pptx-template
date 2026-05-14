"""Template index for scanning and loading template metadata."""

from pathlib import Path
from typing import List, Optional

import yaml

from html_pptx_template.templates.schema import TemplateMeta


class TemplateIndex:
    """Index for scanning and retrieving template metadata."""

    def __init__(self, templates_dir: Path):
        self.templates_dir = Path(templates_dir)

    def scan(self) -> List[TemplateMeta]:
        """Scan templates_dir for all templates, return sorted list of TemplateMeta (newest first)."""
        results = []
        if not self.templates_dir.exists():
            return results

        for entry in self.templates_dir.iterdir():
            if entry.is_dir():
                meta = self._load_meta(entry)
                if meta is not None:
                    results.append(meta)

        # Sort by created_at descending (newest first)
        results.sort(key=lambda m: m.created_at, reverse=True)
        return results

    def get_meta(self, template_id: str) -> Optional[TemplateMeta]:
        """Load meta.yaml for a specific template ID."""
        template_dir = self.get_template_path(template_id)
        return self._load_meta(template_dir)

    def template_exists(self, template_id: str) -> bool:
        """Check if template directory exists."""
        return self.get_template_path(template_id).exists()

    def get_template_path(self, template_id: str) -> Path:
        """Return Path to template directory."""
        return self.templates_dir / template_id

    def _load_meta(self, template_dir: Path) -> Optional[TemplateMeta]:
        """Load meta.yaml from template directory."""
        meta_path = template_dir / "meta.yaml"
        return self._load_meta_file(meta_path)

    def _load_meta_file(self, path: Path) -> Optional[TemplateMeta]:
        """Load and parse a meta.yaml file."""
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data is None:
                return None
            return TemplateMeta.model_validate(data)
        except (yaml.YAMLError, OSError):
            return None
