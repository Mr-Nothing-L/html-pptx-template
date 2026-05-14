"""Tests for StyleAnalyzer."""

import pytest

from html_pptx_template.extractor.style_analyzer import StyleAnalyzer
from html_pptx_template.templates.schema import Theme, ColorPalette, Typography, FontConfig, Spacing


@pytest.fixture
def analyzer():
    return StyleAnalyzer()


class TestClassifyColors:
    def test_classify_colors(self, analyzer):
        """Full palette classification with diverse colors."""
        colors = [
            "#FFFFFF",  # background - lightest
            "#F5F7FA",  # surface - second lightest
            "#1E3A5F",  # primary - dark with moderate saturation
            "#4A90D9",  # secondary
            "#E67E22",  # accent - high saturation
            "#2C3E50",  # text_primary - dark
            "#7F8C8D",  # text_secondary - gray
        ]
        palette = analyzer._classify_colors(colors)

        assert isinstance(palette, ColorPalette)
        assert palette.background == "#FFFFFF"
        assert palette.surface == "#F5F7FA"
        assert palette.primary == "#1E3A5F"
        assert palette.accent == "#E67E22"
        assert palette.text_primary == "#2C3E50"
        assert palette.text_secondary == "#7F8C8D"
        # text_on_primary should be white since primary is dark
        assert palette.text_on_primary == "#FFFFFF"

    def test_classify_colors_fallback(self, analyzer):
        """Fallback when few colors provided."""
        colors = ["#1E3A5F", "#FFFFFF"]
        palette = analyzer._classify_colors(colors)

        assert isinstance(palette, ColorPalette)
        assert palette.background == "#FFFFFF"
        assert palette.primary == "#1E3A5F"
        # Should fill in defaults for missing slots
        assert palette.text_on_primary in ["#FFFFFF", "#000000"]

    def test_empty_colors(self, analyzer):
        """Empty input uses defaults."""
        palette = analyzer._classify_colors([])

        assert isinstance(palette, ColorPalette)
        assert palette.background == "#FFFFFF"
        assert palette.primary == "#1E3A5F"
        assert palette.text_primary == "#2C3E50"


class TestClassifyFonts:
    def test_classify_fonts(self, analyzer):
        """Pick most frequent font, build heading/body/caption config."""
        font_freq = {"Arial": 10, "Helvetica": 5, "Times New Roman": 2}
        size_hierarchy = {"h1": 44, "h2": 32, "h3": 24, "body": 18}

        typography = analyzer._classify_fonts(font_freq, size_hierarchy)

        assert isinstance(typography, Typography)
        assert typography.heading.family == "Arial"
        assert typography.heading.sizes == {"h1": 44, "h2": 32, "h3": 24}
        assert typography.heading.weight == "bold"
        assert typography.body.family == "Arial"
        assert typography.body.size == 18
        assert typography.caption.family == "Arial"
        assert typography.caption.size == 14

    def test_classify_fonts_empty(self, analyzer):
        """Empty font freq uses defaults."""
        font_freq = {}
        size_hierarchy = {"h1": 44, "h2": 32, "h3": 24, "body": 18}

        typography = analyzer._classify_fonts(font_freq, size_hierarchy)

        assert isinstance(typography, Typography)
        assert typography.heading.family == "Arial"
        assert typography.body.family == "Arial"


class TestClassifySpacing:
    def test_classify_spacing(self, analyzer):
        """Infer spacing from extracted values."""
        spacing_values = [8, 16, 24, 32, 48]

        spacing = analyzer._classify_spacing(spacing_values)

        assert isinstance(spacing, Spacing)
        assert spacing.slide_padding == [40, 40, 40, 40]
        assert spacing.content_gap == 24
        assert spacing.line_spacing == 1.5

    def test_classify_spacing_empty(self, analyzer):
        """Empty spacing uses defaults."""
        spacing = analyzer._classify_spacing([])

        assert isinstance(spacing, Spacing)
        assert spacing.slide_padding == [40, 40, 40, 40]
        assert spacing.content_gap == 20
        assert spacing.line_spacing == 1.5


class TestBuildTheme:
    def test_build_theme(self, analyzer):
        """Build Theme from parsed CSS data."""
        parsed = {
            "normalized_colors": [
                "#FFFFFF",
                "#F5F7FA",
                "#1E3A5F",
                "#4A90D9",
                "#E67E22",
                "#2C3E50",
                "#7F8C8D",
            ],
            "font_frequency": {"Arial": 10, "Helvetica": 5},
            "font_size_hierarchy": {"h1": 44, "h2": 32, "h3": 24, "body": 18},
            "spacing_values": [8, 16, 24, 32, 48],
            "page_title": "Test Page",
        }

        theme = analyzer.build_theme(parsed)

        assert isinstance(theme, Theme)
        assert theme.colors.background == "#FFFFFF"
        assert theme.colors.primary == "#1E3A5F"
        assert theme.fonts.heading.family == "Arial"
        assert theme.fonts.body.size == 18
        assert theme.spacing.content_gap == 24
