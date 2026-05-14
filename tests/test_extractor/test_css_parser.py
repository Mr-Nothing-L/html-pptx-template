"""Tests for CSSParser."""

import pytest

from html_pptx_template.extractor.css_parser import CSSParser


@pytest.fixture
def parser():
    return CSSParser()


class TestParseColors:
    def test_extract_colors_from_styles(self, parser):
        """Verify colors normalized correctly."""
        raw_styles = {
            "colors": ["rgb(255, 255, 255)", "#1E3A5F", "rgba(74, 144, 217, 1)", "rgb(255, 255, 255)"],
            "fonts": ["Arial", "Helvetica"],
            "font_sizes": [16, 24, 32],
            "spacing": [8, 16],
            "page_title": "Test Page",
        }
        result = parser.parse(raw_styles)

        assert "normalized_colors" in result
        assert "font_frequency" in result
        assert "font_size_hierarchy" in result
        assert "spacing_values" in result
        assert "page_title" in result

        # Colors should be normalized and deduplicated
        colors = result["normalized_colors"]
        assert "#FFFFFF" in colors
        assert "#1E3A5F" in colors
        assert "#4A90D9" in colors
        # rgb(255,255,255) and #FFFFFF should be deduplicated
        assert len(colors) == 3

    def test_extract_colors_empty(self, parser):
        """Verify empty colors handled."""
        raw_styles = {
            "colors": [],
            "fonts": [],
            "font_sizes": [],
            "spacing": [],
            "page_title": "Test",
        }
        result = parser.parse(raw_styles)
        assert result["normalized_colors"] == []


class TestExtractFonts:
    def test_extract_fonts(self, parser):
        """Verify font frequency counting."""
        raw_styles = {
            "colors": [],
            "fonts": ["Arial", "Helvetica", "Arial", "Times New Roman", "Helvetica", "Arial"],
            "font_sizes": [],
            "spacing": [],
            "page_title": "Test",
        }
        result = parser.parse(raw_styles)

        freq = result["font_frequency"]
        assert freq["Arial"] == 3
        assert freq["Helvetica"] == 2
        assert freq["Times New Roman"] == 1

    def test_extract_fonts_first_family_only(self, parser):
        """Verify only first font family is used from fontFamily strings."""
        raw_styles = {
            "colors": [],
            "fonts": ["Arial, sans-serif", "Helvetica, Arial, sans-serif", "Arial"],
            "font_sizes": [],
            "spacing": [],
            "page_title": "Test",
        }
        result = parser.parse(raw_styles)

        freq = result["font_frequency"]
        # Should extract "Arial" from "Arial, sans-serif"
        assert "Arial" in freq
        assert "Helvetica" in freq


class TestExtractFontSizes:
    def test_extract_font_sizes_four_plus(self, parser):
        """Verify size hierarchy with 4+ sizes."""
        raw_styles = {
            "colors": [],
            "fonts": [],
            "font_sizes": [12, 16, 24, 32, 48, 64],
            "spacing": [],
            "page_title": "Test",
        }
        result = parser.parse(raw_styles)

        hierarchy = result["font_size_hierarchy"]
        assert hierarchy["h1"] == 64
        assert hierarchy["h2"] == 48
        assert hierarchy["h3"] == 32
        assert hierarchy["body"] == 24

    def test_extract_font_sizes_two_to_three(self, parser):
        """Verify size hierarchy with 2-3 sizes."""
        raw_styles = {
            "colors": [],
            "fonts": [],
            "font_sizes": [16, 32],
            "spacing": [],
            "page_title": "Test",
        }
        result = parser.parse(raw_styles)

        hierarchy = result["font_size_hierarchy"]
        assert hierarchy["h1"] == 32
        assert hierarchy["h2"] == 32
        assert hierarchy["h3"] == 16
        assert hierarchy["body"] == 16

    def test_extract_font_sizes_one(self, parser):
        """Verify size hierarchy with 1 size uses defaults with that size as body."""
        raw_styles = {
            "colors": [],
            "fonts": [],
            "font_sizes": [20],
            "spacing": [],
            "page_title": "Test",
        }
        result = parser.parse(raw_styles)

        hierarchy = result["font_size_hierarchy"]
        assert hierarchy["h1"] == 44
        assert hierarchy["h2"] == 32
        assert hierarchy["h3"] == 24
        assert hierarchy["body"] == 20

    def test_extract_font_sizes_empty(self, parser):
        """Verify size hierarchy with empty uses all defaults."""
        raw_styles = {
            "colors": [],
            "fonts": [],
            "font_sizes": [],
            "spacing": [],
            "page_title": "Test",
        }
        result = parser.parse(raw_styles)

        hierarchy = result["font_size_hierarchy"]
        assert hierarchy["h1"] == 44
        assert hierarchy["h2"] == 32
        assert hierarchy["h3"] == 24
        assert hierarchy["body"] == 18

    def test_extract_font_sizes_h1_capped_at_80(self, parser):
        """Verify h1 is capped at 80px even if larger sizes exist."""
        raw_styles = {
            "colors": [],
            "fonts": [],
            "font_sizes": [16, 24, 48, 100],
            "spacing": [],
            "page_title": "Test",
        }
        result = parser.parse(raw_styles)

        hierarchy = result["font_size_hierarchy"]
        assert hierarchy["h1"] == 80  # capped
        assert hierarchy["h2"] == 48
        assert hierarchy["h3"] == 24
        assert hierarchy["body"] == 24  # median of [16, 24, 48, 100]


class TestSpacing:
    def test_extract_spacing(self, parser):
        """Verify spacing values are extracted."""
        raw_styles = {
            "colors": [],
            "fonts": [],
            "font_sizes": [],
            "spacing": [8, 16, 24, 32],
            "page_title": "Test",
        }
        result = parser.parse(raw_styles)
        assert result["spacing_values"] == [8, 16, 24, 32]
