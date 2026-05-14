"""Tests for CLI entry point."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from html_pptx_template.cli import cli


def _async_result(value):
    """Return a coroutine that returns value."""
    async def coro():
        return value
    return coro()


class TestCLI:
    """Tests for the CLI commands."""

    def test_list_empty(self):
        """Empty template list shows appropriate message."""
        runner = CliRunner()

        with patch("html_pptx_template.cli.TemplateManager") as MockManager:
            mock_manager = MagicMock()
            mock_manager.list.return_value = []
            MockManager.return_value = mock_manager

            result = runner.invoke(cli, ["--templates-dir", "/tmp/templates", "list-templates"])

        assert result.exit_code == 0
        assert "No templates found" in result.output

    def test_list_templates(self):
        """List templates shows table with name, source, created."""
        runner = CliRunner()

        with patch("html_pptx_template.cli.TemplateManager") as MockManager:
            mock_manager = MagicMock()
            meta1 = MagicMock()
            meta1.name = "Test Template"
            meta1.source_url = "https://example.com"
            meta1.created_at = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_manager.list.return_value = [meta1]
            MockManager.return_value = mock_manager

            result = runner.invoke(cli, ["--templates-dir", "/tmp/templates", "list-templates"])

        assert result.exit_code == 0
        assert "Test Template" in result.output
        assert "https://example.com" in result.output

    def test_create_template(self):
        """Create template command works end-to-end."""
        runner = CliRunner()

        mock_theme = MagicMock()
        mock_theme.colors.primary = "#1E3A5F"
        mock_theme.fonts.heading.family = "Arial"

        mock_template = MagicMock()
        mock_template.meta.id = "my-template-20250101"
        mock_template.meta.name = "My Template"
        mock_template.theme = mock_theme

        with patch("html_pptx_template.cli.BrowserExtractor") as MockBrowser, \
             patch("html_pptx_template.cli.CSSParser") as MockCSS, \
             patch("html_pptx_template.cli.StyleAnalyzer") as MockAnalyzer, \
             patch("html_pptx_template.cli.TemplateManager") as MockManager:

            # BrowserExtractor returns raw styles
            mock_browser = MagicMock()
            mock_browser.extract_styles.return_value = _async_result({
                "colors": ["#1E3A5F"],
                "fonts": ["Arial"],
                "font_sizes": [18, 24],
                "spacing": [10],
                "page_title": "My Page Title",
            })
            MockBrowser.return_value = mock_browser

            # CSSParser returns parsed styles
            mock_css = MagicMock()
            mock_css.parse.return_value = {
                "normalized_colors": ["#1E3A5F"],
                "font_frequency": {"Arial": 5},
                "font_size_hierarchy": {"h1": 24, "body": 18},
                "spacing_values": [10],
                "page_title": "My Page Title",
            }
            MockCSS.return_value = mock_css

            # StyleAnalyzer returns theme
            mock_analyzer = MagicMock()
            mock_analyzer.build_theme.return_value = mock_theme
            MockAnalyzer.return_value = mock_analyzer

            # TemplateManager returns template
            mock_manager = MagicMock()
            mock_manager.create.return_value = mock_template
            MockManager.return_value = mock_manager

            result = runner.invoke(
                cli,
                ["--templates-dir", "/tmp/templates", "create-template", "https://example.com", "--name", "My Template"],
            )

        assert result.exit_code == 0
        assert "my-template-20250101" in result.output
        assert "My Template" in result.output
        assert "#1E3A5F" in result.output
        assert "Arial" in result.output

    def test_create_template_uses_page_title(self):
        """Create template without --name uses page title."""
        runner = CliRunner()

        mock_theme = MagicMock()
        mock_theme.colors.primary = "#1E3A5F"
        mock_theme.fonts.heading.family = "Arial"

        mock_template = MagicMock()
        mock_template.meta.id = "my-page-title-20250101"
        mock_template.meta.name = "My Page Title"
        mock_template.theme = mock_theme

        with patch("html_pptx_template.cli.BrowserExtractor") as MockBrowser, \
             patch("html_pptx_template.cli.CSSParser") as MockCSS, \
             patch("html_pptx_template.cli.StyleAnalyzer") as MockAnalyzer, \
             patch("html_pptx_template.cli.TemplateManager") as MockManager:

            mock_browser = MagicMock()
            mock_browser.extract_styles.return_value = _async_result({
                "colors": ["#1E3A5F"],
                "fonts": ["Arial"],
                "font_sizes": [18, 24],
                "spacing": [10],
                "page_title": "My Page Title",
            })
            MockBrowser.return_value = mock_browser

            mock_css = MagicMock()
            mock_css.parse.return_value = {
                "normalized_colors": ["#1E3A5F"],
                "font_frequency": {"Arial": 5},
                "font_size_hierarchy": {"h1": 24, "body": 18},
                "spacing_values": [10],
                "page_title": "My Page Title",
            }
            MockCSS.return_value = mock_css

            mock_analyzer = MagicMock()
            mock_analyzer.build_theme.return_value = mock_theme
            MockAnalyzer.return_value = mock_analyzer

            mock_manager = MagicMock()
            mock_manager.create.return_value = mock_template
            MockManager.return_value = mock_manager

            result = runner.invoke(
                cli,
                ["--templates-dir", "/tmp/templates", "create-template", "https://example.com"],
            )

        assert result.exit_code == 0
        # Manager.create should be called with page title as name
        mock_manager.create.assert_called_once()
        call_args = mock_manager.create.call_args
        assert call_args.kwargs["name"] == "My Page Title"

    def test_generate_ppt_with_default_template(self):
        """Generate PPTX with default template when no --template specified."""
        runner = CliRunner()

        mock_template = MagicMock()
        mock_template.meta.id = "default-template"
        mock_template.theme.slide_width = 10.0
        mock_template.theme.slide_height = 5.625

        with runner.isolated_filesystem() as fs:
            content_file = Path(fs) / "content.md"
            content_file.write_text("# Slide 1\n\nSome content\n")

            with patch("html_pptx_template.cli.TemplateManager") as MockManager, \
                 patch("html_pptx_template.cli.GeneratorEngine") as MockEngine:

                mock_manager = MagicMock()
                mock_manager.get_default.return_value = mock_template
                mock_manager.load.return_value = mock_template
                MockManager.return_value = mock_manager

                mock_engine = MagicMock()
                mock_engine.parse_content.return_value = [
                    {"layout": "title", "content": {"title": "Slide 1"}},
                ]
                MockEngine.return_value = mock_engine

                result = runner.invoke(
                    cli,
                    [
                        "--templates-dir", "/tmp/templates",
                        "generate-ppt",
                        str(content_file),
                        "--output", "output.pptx",
                    ],
                )

            assert result.exit_code == 0
            assert "output.pptx" in result.output
            mock_engine.generate.assert_called_once()

    def test_generate_ppt_select_with_multiple_templates(self):
        """Force template selection with --select when multiple templates exist."""
        runner = CliRunner()

        meta1 = MagicMock()
        meta1.id = "template-a"
        meta1.name = "Template A"

        meta2 = MagicMock()
        meta2.id = "template-b"
        meta2.name = "Template B"

        with runner.isolated_filesystem() as fs:
            content_file = Path(fs) / "content.md"
            content_file.write_text("# Slide 1\n\nSome content\n")

            with patch("html_pptx_template.cli.TemplateManager") as MockManager:
                mock_manager = MagicMock()
                mock_manager.get_default.return_value = None
                mock_manager.list.return_value = [meta1, meta2]
                MockManager.return_value = mock_manager

                result = runner.invoke(
                    cli,
                    [
                        "--templates-dir", "/tmp/templates",
                        "generate-ppt",
                        str(content_file),
                        "--select",
                    ],
                )

            assert result.exit_code == 1
            assert "Multiple templates available" in result.output
            assert "Template A" in result.output
            assert "Template B" in result.output

    def test_generate_ppt_no_templates(self):
        """Generate PPTX with no templates shows error."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            content_file = Path(fs) / "content.md"
            content_file.write_text("# Slide 1\n\nSome content\n")

            with patch("html_pptx_template.cli.TemplateManager") as MockManager:
                mock_manager = MagicMock()
                mock_manager.get_default.return_value = None
                mock_manager.list.return_value = []
                MockManager.return_value = mock_manager

                result = runner.invoke(
                    cli,
                    [
                        "--templates-dir", "/tmp/templates",
                        "generate-ppt",
                        str(content_file),
                        "--select",
                    ],
                )

            assert result.exit_code == 1
            assert "No templates available" in result.output

    def test_generate_ppt_single_template_auto_select(self):
        """With 1 template and --select, auto-use it."""
        runner = CliRunner()

        meta1 = MagicMock()
        meta1.id = "only-template"
        meta1.name = "Only Template"

        mock_template = MagicMock()
        mock_template.meta.id = "only-template"
        mock_template.theme.slide_width = 10.0
        mock_template.theme.slide_height = 5.625

        with runner.isolated_filesystem() as fs:
            content_file = Path(fs) / "content.md"
            content_file.write_text("# Slide 1\n\nSome content\n")

            with patch("html_pptx_template.cli.TemplateManager") as MockManager, \
                 patch("html_pptx_template.cli.GeneratorEngine") as MockEngine:

                mock_manager = MagicMock()
                mock_manager.get_default.return_value = None
                mock_manager.list.return_value = [meta1]
                mock_manager.load.return_value = mock_template
                MockManager.return_value = mock_manager

                mock_engine = MagicMock()
                mock_engine.parse_content.return_value = [
                    {"layout": "title", "content": {"title": "Slide 1"}},
                ]
                MockEngine.return_value = mock_engine

                result = runner.invoke(
                    cli,
                    [
                        "--templates-dir", "/tmp/templates",
                        "generate-ppt",
                        str(content_file),
                        "--select",
                    ],
                )

            assert result.exit_code == 0
            assert "presentation.pptx" in result.output
            mock_manager.load.assert_called_once_with("only-template")

    def test_set_default(self):
        """Set default template command works."""
        runner = CliRunner()

        with patch("html_pptx_template.cli.TemplateManager") as MockManager:
            mock_manager = MagicMock()
            mock_manager.set_default.return_value = True
            MockManager.return_value = mock_manager

            result = runner.invoke(
                cli,
                ["--templates-dir", "/tmp/templates", "set-default", "my-template"],
            )

        assert result.exit_code == 0
        assert "my-template" in result.output
        mock_manager.set_default.assert_called_once_with("my-template")

    def test_set_default_invalid_template(self):
        """Set default with non-existent template shows error."""
        runner = CliRunner()

        with patch("html_pptx_template.cli.TemplateManager") as MockManager:
            mock_manager = MagicMock()
            mock_manager.set_default.return_value = False
            MockManager.return_value = mock_manager

            result = runner.invoke(
                cli,
                ["--templates-dir", "/tmp/templates", "set-default", "nonexistent"],
            )

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "does not exist" in result.output.lower()

    def test_generate_ppt_with_explicit_template(self):
        """Generate PPTX with --template uses specified template."""
        runner = CliRunner()

        mock_template = MagicMock()
        mock_template.meta.id = "explicit-template"
        mock_template.theme.slide_width = 10.0
        mock_template.theme.slide_height = 5.625

        with runner.isolated_filesystem() as fs:
            content_file = Path(fs) / "content.md"
            content_file.write_text("# Slide 1\n\nSome content\n")

            with patch("html_pptx_template.cli.TemplateManager") as MockManager, \
                 patch("html_pptx_template.cli.GeneratorEngine") as MockEngine:

                mock_manager = MagicMock()
                mock_manager.load.return_value = mock_template
                MockManager.return_value = mock_manager

                mock_engine = MagicMock()
                mock_engine.parse_content.return_value = [
                    {"layout": "title", "content": {"title": "Slide 1"}},
                ]
                MockEngine.return_value = mock_engine

                result = runner.invoke(
                    cli,
                    [
                        "--templates-dir", "/tmp/templates",
                        "generate-ppt",
                        str(content_file),
                        "--template", "explicit-template",
                        "--output", "output.pptx",
                    ],
                )

            assert result.exit_code == 0
            assert "output.pptx" in result.output
            mock_manager.load.assert_called_once_with("explicit-template")
