"""Tests for TemplateIndex class."""

from datetime import datetime, timezone
from pathlib import Path

import yaml
import pytest

from html_pptx_template.templates.index import TemplateIndex
from html_pptx_template.templates.schema import TemplateMeta


class TestTemplateIndex:
    """Tests for TemplateIndex."""

    def test_scan_finds_templates(self, temp_dir):
        """Create 2 mock templates with meta.yaml, verify scan finds both."""
        # Create template directories with meta.yaml files
        template1_dir = temp_dir / "my-template-20240115"
        template1_dir.mkdir()
        meta1 = {
            "id": "my-template-20240115",
            "name": "My Template",
            "source_url": "https://example.com",
            "created_at": datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc).isoformat(),
            "version": 1,
        }
        with open(template1_dir / "meta.yaml", "w") as f:
            yaml.dump(meta1, f, allow_unicode=True, sort_keys=False)

        template2_dir = temp_dir / "another-template-20240220"
        template2_dir.mkdir()
        meta2 = {
            "id": "another-template-20240220",
            "name": "Another Template",
            "source_url": "https://example.org",
            "created_at": datetime(2024, 2, 20, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
            "version": 1,
        }
        with open(template2_dir / "meta.yaml", "w") as f:
            yaml.dump(meta2, f, allow_unicode=True, sort_keys=False)

        index = TemplateIndex(temp_dir)
        results = index.scan()

        assert len(results) == 2
        # Should be sorted newest first
        assert results[0].id == "another-template-20240220"
        assert results[1].id == "my-template-20240115"
        assert results[0].name == "Another Template"
        assert results[1].name == "My Template"

    def test_scan_empty_dir(self, temp_dir):
        """Empty directory returns empty list."""
        index = TemplateIndex(temp_dir)
        results = index.scan()
        assert results == []

    def test_get_meta(self, temp_dir):
        """Load specific template meta."""
        template_dir = temp_dir / "test-template-20240115"
        template_dir.mkdir()
        meta = {
            "id": "test-template-20240115",
            "name": "Test Template",
            "source_url": "https://example.com",
            "created_at": datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc).isoformat(),
            "version": 1,
        }
        with open(template_dir / "meta.yaml", "w") as f:
            yaml.dump(meta, f, allow_unicode=True, sort_keys=False)

        index = TemplateIndex(temp_dir)
        result = index.get_meta("test-template-20240115")

        assert result is not None
        assert result.id == "test-template-20240115"
        assert result.name == "Test Template"
        assert result.source_url == "https://example.com"

    def test_get_meta_missing(self, temp_dir):
        """Missing template returns None."""
        index = TemplateIndex(temp_dir)
        result = index.get_meta("nonexistent-template")
        assert result is None

    def test_template_exists(self, temp_dir):
        """Check if template directory exists."""
        template_dir = temp_dir / "existing-template"
        template_dir.mkdir()
        (template_dir / "meta.yaml").write_text("dummy")

        index = TemplateIndex(temp_dir)
        assert index.template_exists("existing-template") is True
        assert index.template_exists("nonexistent-template") is False

    def test_get_template_path(self, temp_dir):
        """Return Path to template directory."""
        index = TemplateIndex(temp_dir)
        path = index.get_template_path("some-template")
        assert path == temp_dir / "some-template"
