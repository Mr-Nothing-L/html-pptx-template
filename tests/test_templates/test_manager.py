"""Tests for TemplateManager class."""

from datetime import datetime, timezone
from pathlib import Path

import yaml
import pytest

from html_pptx_template.templates.manager import TemplateManager
from html_pptx_template.templates.schema import Theme, TemplateMeta


class TestTemplateManager:
    """Tests for TemplateManager."""

    def test_create_template(self, temp_dir):
        """Create template, verify files exist."""
        config_dir = temp_dir / "config"
        templates_dir = temp_dir / "templates"
        manager = TemplateManager(templates_dir, config_dir)

        theme = Theme.model_validate({
            "colors": {
                "primary": "#1E3A5F",
                "secondary": "#4A90D9",
                "accent": "#E67E22",
                "background": "#FFFFFF",
                "surface": "#F5F7FA",
                "text_primary": "#2C3E50",
                "text_secondary": "#7F8C8D",
                "text_on_primary": "#FFFFFF",
            },
            "fonts": {
                "heading": {"family": "Arial", "sizes": {"h1": 44}, "weight": "bold", "color": "text_primary"},
                "body": {"family": "Arial", "size": 18, "weight": "normal", "color": "text_primary"},
                "caption": {"family": "Arial", "size": 14, "color": "text_secondary"},
            },
            "spacing": {
                "slide_padding": [40, 40, 40, 40],
                "content_gap": 20,
                "line_spacing": 1.5,
            },
        })

        template = manager.create(
            url="https://example.com",
            name="My Awesome Template",
            theme=theme,
        )

        # Verify template returned
        assert template is not None
        assert template.meta.name == "My Awesome Template"
        assert template.meta.source_url == "https://example.com"
        assert template.theme.colors.primary == "#1E3A5F"

        # Verify files on disk
        template_dir = templates_dir / template.meta.id
        assert template_dir.exists()
        assert (template_dir / "meta.yaml").exists()
        assert (template_dir / "theme.yaml").exists()
        assert (template_dir / "layout.md").exists()
        assert (template_dir / "assets").is_dir()

        # Verify meta.yaml content
        with open(template_dir / "meta.yaml") as f:
            meta_data = yaml.safe_load(f)
        assert meta_data["name"] == "My Awesome Template"
        assert meta_data["source_url"] == "https://example.com"
        assert meta_data["id"] == template.meta.id

        # Verify theme.yaml content
        with open(template_dir / "theme.yaml") as f:
            theme_data = yaml.safe_load(f)
        assert theme_data["colors"]["primary"] == "#1E3A5F"

        # Verify layout.md exists and has content
        layout_content = (template_dir / "layout.md").read_text()
        assert "# Slide Layouts" in layout_content
        assert (template_dir / "visual_analysis.md").exists()
        assert (template_dir / "layouts.yaml").exists()

    def test_list_templates(self, temp_dir):
        """Create 2 templates, list them."""
        templates_dir = temp_dir / "templates"
        config_dir = temp_dir / "config"
        manager = TemplateManager(templates_dir, config_dir)

        theme = Theme.model_validate({
            "colors": {
                "primary": "#1E3A5F",
                "secondary": "#4A90D9",
                "accent": "#E67E22",
                "background": "#FFFFFF",
                "surface": "#F5F7FA",
                "text_primary": "#2C3E50",
                "text_secondary": "#7F8C8D",
                "text_on_primary": "#FFFFFF",
            },
            "fonts": {
                "heading": {"family": "Arial", "sizes": {"h1": 44}, "weight": "bold", "color": "text_primary"},
                "body": {"family": "Arial", "size": 18, "weight": "normal", "color": "text_primary"},
                "caption": {"family": "Arial", "size": 14, "color": "text_secondary"},
            },
            "spacing": {
                "slide_padding": [40, 40, 40, 40],
                "content_gap": 20,
                "line_spacing": 1.5,
            },
        })

        t1 = manager.create(url="https://example.com/1", name="Template One", theme=theme)
        t2 = manager.create(url="https://example.com/2", name="Template Two", theme=theme)

        results = manager.list()
        assert len(results) == 2
        ids = {r.id for r in results}
        assert t1.meta.id in ids
        assert t2.meta.id in ids

    def test_load_template(self, temp_dir):
        """Create and load back, verify theme colors."""
        templates_dir = temp_dir / "templates"
        config_dir = temp_dir / "config"
        manager = TemplateManager(templates_dir, config_dir)

        theme = Theme.model_validate({
            "colors": {
                "primary": "#FF5733",
                "secondary": "#33FF57",
                "accent": "#3357FF",
                "background": "#FFFFFF",
                "surface": "#F5F7FA",
                "text_primary": "#2C3E50",
                "text_secondary": "#7F8C8D",
                "text_on_primary": "#FFFFFF",
            },
            "fonts": {
                "heading": {"family": "Arial", "sizes": {"h1": 44}, "weight": "bold", "color": "text_primary"},
                "body": {"family": "Arial", "size": 18, "weight": "normal", "color": "text_primary"},
                "caption": {"family": "Arial", "size": 14, "color": "text_secondary"},
            },
            "spacing": {
                "slide_padding": [40, 40, 40, 40],
                "content_gap": 20,
                "line_spacing": 1.5,
            },
        })

        created = manager.create(url="https://example.com", name="Load Test", theme=theme)
        loaded = manager.load(created.meta.id)

        assert loaded is not None
        assert loaded.meta.id == created.meta.id
        assert loaded.meta.name == "Load Test"
        assert loaded.theme.colors.primary == "#FF5733"
        assert loaded.theme.colors.secondary == "#33FF57"
        assert loaded.theme.colors.accent == "#3357FF"

    def test_delete_template(self, temp_dir):
        """Create, delete, verify gone."""
        templates_dir = temp_dir / "templates"
        config_dir = temp_dir / "config"
        manager = TemplateManager(templates_dir, config_dir)

        theme = Theme.model_validate({
            "colors": {
                "primary": "#1E3A5F",
                "secondary": "#4A90D9",
                "accent": "#E67E22",
                "background": "#FFFFFF",
                "surface": "#F5F7FA",
                "text_primary": "#2C3E50",
                "text_secondary": "#7F8C8D",
                "text_on_primary": "#FFFFFF",
            },
            "fonts": {
                "heading": {"family": "Arial", "sizes": {"h1": 44}, "weight": "bold", "color": "text_primary"},
                "body": {"family": "Arial", "size": 18, "weight": "normal", "color": "text_primary"},
                "caption": {"family": "Arial", "size": 14, "color": "text_secondary"},
            },
            "spacing": {
                "slide_padding": [40, 40, 40, 40],
                "content_gap": 20,
                "line_spacing": 1.5,
            },
        })

        created = manager.create(url="https://example.com", name="Delete Test", theme=theme)
        template_id = created.meta.id

        # Verify it exists
        assert (templates_dir / template_id).exists()

        # Delete it
        result = manager.delete(template_id)
        assert result is True

        # Verify it's gone
        assert not (templates_dir / template_id).exists()

        # Deleting again should return False
        assert manager.delete(template_id) is False

    def test_set_and_get_default(self, temp_dir):
        """Set default, verify it persists."""
        templates_dir = temp_dir / "templates"
        config_dir = temp_dir / "config"
        manager = TemplateManager(templates_dir, config_dir)

        theme = Theme.model_validate({
            "colors": {
                "primary": "#1E3A5F",
                "secondary": "#4A90D9",
                "accent": "#E67E22",
                "background": "#FFFFFF",
                "surface": "#F5F7FA",
                "text_primary": "#2C3E50",
                "text_secondary": "#7F8C8D",
                "text_on_primary": "#FFFFFF",
            },
            "fonts": {
                "heading": {"family": "Arial", "sizes": {"h1": 44}, "weight": "bold", "color": "text_primary"},
                "body": {"family": "Arial", "size": 18, "weight": "normal", "color": "text_primary"},
                "caption": {"family": "Arial", "size": 14, "color": "text_secondary"},
            },
            "spacing": {
                "slide_padding": [40, 40, 40, 40],
                "content_gap": 20,
                "line_spacing": 1.5,
            },
        })

        created = manager.create(url="https://example.com", name="Default Test", theme=theme)
        template_id = created.meta.id

        # Set as default
        result = manager.set_default(template_id)
        assert result is True

        # Get default
        default = manager.get_default()
        assert default is not None
        assert default.id == template_id
        assert default.name == "Default Test"

        # Verify config file was written
        config_file = config_dir / "config.yaml"
        assert config_file.exists()
        with open(config_file) as f:
            config_data = yaml.safe_load(f)
        assert config_data["default_template"] == template_id

    def test_get_default_none(self, temp_dir):
        """No default returns None."""
        templates_dir = temp_dir / "templates"
        config_dir = temp_dir / "config"
        manager = TemplateManager(templates_dir, config_dir)

        default = manager.get_default()
        assert default is None

    def test_create_duplicate_id(self, temp_dir):
        """Creating template with same name on same day appends -1, -2, etc."""
        templates_dir = temp_dir / "templates"
        config_dir = temp_dir / "config"
        manager = TemplateManager(templates_dir, config_dir)

        theme = Theme.model_validate({
            "colors": {
                "primary": "#1E3A5F",
                "secondary": "#4A90D9",
                "accent": "#E67E22",
                "background": "#FFFFFF",
                "surface": "#F5F7FA",
                "text_primary": "#2C3E50",
                "text_secondary": "#7F8C8D",
                "text_on_primary": "#FFFFFF",
            },
            "fonts": {
                "heading": {"family": "Arial", "sizes": {"h1": 44}, "weight": "bold", "color": "text_primary"},
                "body": {"family": "Arial", "size": 18, "weight": "normal", "color": "text_primary"},
                "caption": {"family": "Arial", "size": 14, "color": "text_secondary"},
            },
            "spacing": {
                "slide_padding": [40, 40, 40, 40],
                "content_gap": 20,
                "line_spacing": 1.5,
            },
        })

        t1 = manager.create(url="https://example.com", name="Duplicate", theme=theme)
        t2 = manager.create(url="https://example.com", name="Duplicate", theme=theme)
        t3 = manager.create(url="https://example.com", name="Duplicate", theme=theme)

        # IDs should be unique
        assert t1.meta.id != t2.meta.id
        assert t2.meta.id != t3.meta.id
        assert t1.meta.id != t3.meta.id

        # The second and third should have suffixes
        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        assert t1.meta.id == f"duplicate-{today_str}"
        assert t2.meta.id == f"duplicate-{today_str}-1"
        assert t3.meta.id == f"duplicate-{today_str}-2"
