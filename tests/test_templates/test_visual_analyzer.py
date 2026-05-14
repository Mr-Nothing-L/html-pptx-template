"""Tests for VisualAnalyzer."""

import yaml
from pathlib import Path

import pytest

from html_pptx_template.templates.visual_analyzer import VisualAnalyzer


SAMPLE_VISUAL_ANALYSIS = """\
# Visual Style Analysis

> AI visual analysis based on screenshots in `assets/`.

## Overall Impression

- **Mood/Vibe**: Minimalist, bold, editorial, gallery-like

## Slide Design Recommendations

Based on the above analysis, describe how slides should look:

- **Title Slide**: Light gray background with massive bold black centered title. All caps. No subtitle or minimal small subtitle below.
- **Content Slide**: White or light gray background, black left-aligned text. Large headings, sparse bullet points. No colored header bars.
- **Section Divider**: Solid black background with white centered text. Dramatic contrast.
- **Image Slide**: Full-bleed dark image card with rounded corners on light background. Minimal caption below.
- **Data Slide**: Clean white background, black data visualizations. No colored charts — monochrome preferred.

## Asset Suggestions

- **Recommended Image Types**: Dark-themed screenshots
"""


class TestVisualAnalyzer:
    """Tests for VisualAnalyzer."""

    @pytest.fixture
    def sample_file(self, tmp_path):
        path = tmp_path / "visual_analysis.md"
        path.write_text(SAMPLE_VISUAL_ANALYSIS, encoding="utf-8")
        return path

    def test_parse_extracts_all_slide_types(self, sample_file):
        analyzer = VisualAnalyzer(sample_file)
        result = analyzer.parse()

        assert set(result.keys()) == {
            "title",
            "content",
            "section_divider",
            "image_slide",
            "data_slide",
        }

    def test_parse_title_slide(self, sample_file):
        analyzer = VisualAnalyzer(sample_file)
        result = analyzer.parse()
        title = result["title"]

        assert title["background"] == "surface"
        assert title["title_uppercase"] is True
        assert title["title_align"] == "center"
        assert title["title_size_level"] == "h1"
        assert title["has_subtitle"] is True
        assert title["subtitle_size_level"] == "caption"
        assert title["spacing"] == "normal"

    def test_parse_content_slide(self, sample_file):
        analyzer = VisualAnalyzer(sample_file)
        result = analyzer.parse()
        content = result["content"]

        assert content["background"] == "surface"
        assert content["title_uppercase"] is False
        assert content["title_align"] == "left"
        assert content["title_size_level"] == "h2"
        assert content["has_bullets"] is True
        assert content["bullet_spacing"] == "generous"
        assert content["has_header_bar"] is False

    def test_parse_section_divider(self, sample_file):
        analyzer = VisualAnalyzer(sample_file)
        result = analyzer.parse()
        section = result["section_divider"]

        assert section["background"] == "primary"
        assert section["title_uppercase"] is False
        assert section["title_align"] == "center"
        assert section["title_size_level"] == "h2"
        assert section["text_color"] == "text_on_primary"

    def test_parse_image_slide(self, sample_file):
        analyzer = VisualAnalyzer(sample_file)
        result = analyzer.parse()
        image = result["image_slide"]

        assert image["background"] == "surface"
        assert image["image_position"] == "full_bleed"
        assert image["image_style"] == "rounded_corners"
        assert image["caption_position"] == "below"

    def test_parse_data_slide(self, sample_file):
        analyzer = VisualAnalyzer(sample_file)
        result = analyzer.parse()
        data = result["data_slide"]

        assert data["background"] == "background"
        assert data["chart_style"] == "monochrome"
        assert data["text_color"] == "text_primary"

    def test_generate_layouts_yaml(self, sample_file, tmp_path):
        analyzer = VisualAnalyzer(sample_file)
        output = analyzer.generate_layouts_yaml(tmp_path)

        assert output.exists()
        assert output.name == "layouts.yaml"

        with open(output, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)

        assert "title" in loaded
        assert loaded["title"]["title_uppercase"] is True
        assert loaded["content"]["has_header_bar"] is False

    def test_parse_empty_section(self, tmp_path):
        path = tmp_path / "empty.md"
        path.write_text("# No slide section here\n", encoding="utf-8")
        analyzer = VisualAnalyzer(path)
        result = analyzer.parse()
        assert result == {}

    def test_parse_no_subtitle(self, tmp_path):
        path = tmp_path / "no_sub.md"
        path.write_text(
            "## Slide Design Recommendations\n\n"
            "- **Title Slide**: White background. All caps. No subtitle.\n",
            encoding="utf-8",
        )
        analyzer = VisualAnalyzer(path)
        result = analyzer.parse()
        assert result["title"]["has_subtitle"] is False
