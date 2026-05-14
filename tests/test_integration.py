"""End-to-end integration tests using real components (no mocks)."""

from pathlib import Path

from html_pptx_template.templates.manager import TemplateManager
from html_pptx_template.templates.schema import (
    ColorPalette,
    FontConfig,
    Spacing,
    Theme,
    Typography,
)
from html_pptx_template.generator.engine import GeneratorEngine


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_end_to_end_generate(self, tmp_path):
        """Create a template, then generate a PPTX from markdown content."""
        templates_dir = tmp_path / "templates"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Step 1: Create a TemplateManager
        manager = TemplateManager(templates_dir, config_dir)

        # Step 2: Create a Theme manually
        theme = Theme(
            colors=ColorPalette(
                primary="#1E3A5F",
                secondary="#4A90D9",
                accent="#E67E22",
                background="#FFFFFF",
                surface="#F5F7FA",
                text_primary="#2C3E50",
                text_secondary="#7F8C8D",
                text_on_primary="#FFFFFF",
            ),
            fonts=Typography(
                heading=FontConfig(
                    family="Arial",
                    sizes={"h1": 44, "h2": 32, "h3": 24},
                    weight="bold",
                    color="text_primary",
                ),
                body=FontConfig(
                    family="Arial",
                    size=18,
                    weight="normal",
                    color="text_primary",
                ),
                caption=FontConfig(
                    family="Arial",
                    size=14,
                    color="text_secondary",
                ),
            ),
            spacing=Spacing(
                slide_padding=[40, 40, 40, 40],
                content_gap=20,
                line_spacing=1.5,
            ),
        )

        # Step 3: Create a template
        template = manager.create(
            url="https://example.com",
            name="Integration Test Template",
            theme=theme,
        )

        assert template is not None
        assert template.meta.name == "Integration Test Template"

        # Step 4: Use GeneratorEngine to parse markdown and generate PPTX
        engine = GeneratorEngine()
        markdown = (
            "# Welcome Slide\n\n"
            "This is the welcome presentation.\n\n"
            "---\n\n"
            "# Agenda\n\n"
            "- Point one\n"
            "- Point two\n"
            "- Point three\n"
        )

        slides_data = engine.parse_content(markdown)
        assert len(slides_data) == 2

        output_path = output_dir / "presentation.pptx"
        engine.generate(template, slides_data, str(output_path))

        # Step 5: Assert output file exists and has content
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_template_save_and_load(self, tmp_path):
        """Create template with custom theme, save, load back, verify all properties."""
        templates_dir = tmp_path / "templates"
        config_dir = tmp_path / "config"

        manager = TemplateManager(templates_dir, config_dir)

        # Create a custom theme with different colors/fonts than default
        custom_theme = Theme(
            colors=ColorPalette(
                primary="#FF5733",
                secondary="#33FF57",
                accent="#3357FF",
                background="#F0F0F0",
                surface="#E0E0E0",
                text_primary="#111111",
                text_secondary="#555555",
                text_on_primary="#FFFFFF",
            ),
            fonts=Typography(
                heading=FontConfig(
                    family="Helvetica",
                    sizes={"h1": 48, "h2": 36, "h3": 28},
                    weight="bold",
                    color="text_primary",
                ),
                body=FontConfig(
                    family="Helvetica",
                    size=20,
                    weight="normal",
                    color="text_primary",
                ),
                caption=FontConfig(
                    family="Helvetica",
                    size=16,
                    color="text_secondary",
                ),
            ),
            spacing=Spacing(
                slide_padding=[50, 50, 50, 50],
                content_gap=25,
                line_spacing=1.6,
            ),
            aspect_ratio="16:9",
            slide_width=13.333,
            slide_height=7.5,
        )

        # Create template
        created = manager.create(
            url="https://custom-example.com",
            name="Custom Theme Template",
            theme=custom_theme,
        )

        template_id = created.meta.id

        # Load it back
        loaded = manager.load(template_id)

        # Assert all properties match
        assert loaded is not None
        assert loaded.meta.id == template_id
        assert loaded.meta.name == "Custom Theme Template"
        assert loaded.meta.source_url == "https://custom-example.com"

        # Colors
        assert loaded.theme.colors.primary == "#FF5733"
        assert loaded.theme.colors.secondary == "#33FF57"
        assert loaded.theme.colors.accent == "#3357FF"
        assert loaded.theme.colors.background == "#F0F0F0"
        assert loaded.theme.colors.surface == "#E0E0E0"
        assert loaded.theme.colors.text_primary == "#111111"
        assert loaded.theme.colors.text_secondary == "#555555"
        assert loaded.theme.colors.text_on_primary == "#FFFFFF"

        # Fonts
        assert loaded.theme.fonts.heading.family == "Helvetica"
        assert loaded.theme.fonts.body.family == "Helvetica"
        assert loaded.theme.fonts.caption.family == "Helvetica"
        assert loaded.theme.fonts.heading.weight == "bold"
        assert loaded.theme.fonts.body.weight == "normal"
        assert loaded.theme.fonts.body.size == 20
        assert loaded.theme.fonts.caption.size == 16

        # Spacing
        assert loaded.theme.spacing.slide_padding == [50, 50, 50, 50]
        assert loaded.theme.spacing.content_gap == 25
        assert loaded.theme.spacing.line_spacing == 1.6

        # Dimensions
        assert loaded.theme.aspect_ratio == "16:9"
        assert loaded.theme.slide_width == 13.333
        assert loaded.theme.slide_height == 7.5
