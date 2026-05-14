"""Tests for GeneratorEngine - Task 13."""

import pytest
from pathlib import Path

from html_pptx_template.templates.schema import Theme, Template, TemplateMeta, LayoutSlide, LayoutElement
from html_pptx_template.generator.engine import GeneratorEngine


@pytest.fixture
def sample_theme():
    return Theme(
        colors={
            "primary": "#1E3A5F",
            "secondary": "#4A90D9",
            "accent": "#E67E22",
            "background": "#FFFFFF",
            "surface": "#F5F7FA",
            "text_primary": "#2C3E50",
            "text_secondary": "#7F8C8D",
            "text_on_primary": "#FFFFFF",
        },
        fonts={
            "heading": {
                "family": "Arial, sans-serif",
                "sizes": {"h1": 44, "h2": 32, "h3": 24},
                "weight": "bold",
                "color": "text_primary",
            },
            "body": {
                "family": "Arial, sans-serif",
                "size": 18,
                "weight": "normal",
                "color": "text_primary",
            },
            "caption": {
                "family": "Arial, sans-serif",
                "size": 14,
                "color": "text_secondary",
            },
        },
        spacing={
            "slide_padding": [40, 40, 40, 40],
            "content_gap": 20,
            "line_spacing": 1.5,
        },
        aspect_ratio="16:9",
        slide_width=10.0,
        slide_height=5.625,
    )


@pytest.fixture
def sample_template(sample_theme):
    return Template(
        meta=TemplateMeta(
            id="test-template",
            name="Test Template",
            source_url="https://example.com",
        ),
        theme=sample_theme,
        layouts=[
            LayoutSlide(
                name="title",
                slide_type="title",
                background="background",
                elements=[
                    LayoutElement(type="title", style={"level": "h1", "align": "centered"}),
                    LayoutElement(type="subtitle", style={"level": "body", "align": "centered"}),
                ],
            ),
            LayoutSlide(
                name="content",
                slide_type="content",
                background="background",
                elements=[
                    LayoutElement(type="header_bar", style={"level": "h2", "align": "left"}),
                    LayoutElement(type="content", style={"level": "body", "align": "left"}),
                ],
            ),
            LayoutSlide(
                name="section_divider",
                slide_type="section_divider",
                background="primary",
                elements=[
                    LayoutElement(type="title", style={"level": "h1", "align": "centered"}),
                ],
            ),
        ],
    )


@pytest.fixture
def engine():
    return GeneratorEngine()


class TestParseMarkdownContent:
    def test_parse_markdown_content(self, engine):
        """Parse full markdown with multiple slides."""
        markdown = """# My Presentation

## A subtitle here

---

# First Content Slide

- Bullet one
- Bullet two
- Bullet three

---

# Section Divider

---

# Second Content Slide

Some body text here.
More body text.
"""
        slides_data = engine.parse_content(markdown)
        assert len(slides_data) == 4

        # First slide: title slide
        assert slides_data[0]["content"]["title"] == "My Presentation"
        assert slides_data[0]["content"]["subtitle"] == "A subtitle here"
        assert "bullets" not in slides_data[0]["content"] or len(slides_data[0]["content"].get("bullets", [])) == 0

        # Second slide: content with bullets
        assert slides_data[1]["content"]["title"] == "First Content Slide"
        assert "Bullet one" in slides_data[1]["content"]["bullets"]
        assert "Bullet two" in slides_data[1]["content"]["bullets"]

        # Third slide: section divider
        assert slides_data[2]["content"]["title"] == "Section Divider"

        # Fourth slide: body text
        assert slides_data[3]["content"]["title"] == "Second Content Slide"
        assert "body" in slides_data[3]["content"]

    def test_parse_bullet_variants(self, engine):
        """Parse both - and * bullet styles."""
        markdown = """# Slide Title

- Dash bullet
* Star bullet
- Another dash
"""
        slides_data = engine.parse_content(markdown)
        assert len(slides_data) == 1
        bullets = slides_data[0]["content"]["bullets"]
        assert "Dash bullet" in bullets
        assert "Star bullet" in bullets
        assert "Another dash" in bullets

    def test_parse_table_rows(self, engine):
        """Parse table rows into structured table data."""
        markdown = """# Slide Title

| Col1 | Col2 | Col3 |
| A | B | C |
"""
        slides_data = engine.parse_content(markdown)
        assert len(slides_data) == 1
        assert "table" in slides_data[0]["content"]
        table = slides_data[0]["content"]["table"]
        assert table["headers"] == ["Col1", "Col2", "Col3"]
        assert table["rows"] == [["A", "B", "C"]]
        assert slides_data[0]["layout"] == "table"


class TestInferLayoutFromContent:
    def test_infer_title_layout(self, engine):
        """Title + subtitle, no bullets → title layout."""
        content = {"title": "My Title", "subtitle": "My Subtitle"}
        layout = engine._infer_layout_from_content(content)
        assert layout == "title"

    def test_infer_section_divider(self, engine):
        """Title only, no body/bullets → section_divider."""
        content = {"title": "Section Title"}
        layout = engine._infer_layout_from_content(content)
        assert layout == "section_divider"

    def test_infer_content_layout(self, engine):
        """Title with bullets → content layout."""
        content = {"title": "Content Title", "bullets": ["a", "b"]}
        layout = engine._infer_layout_from_content(content)
        assert layout == "content"

    def test_infer_content_with_body(self, engine):
        """Title with body text → content layout."""
        content = {"title": "Content Title", "body": "Some text"}
        layout = engine._infer_layout_from_content(content)
        assert layout == "content"


class TestGeneratePptx:
    def test_generate_pptx(self, engine, sample_template, tmp_path):
        """Generate actual PPTX file, verify exists and non-empty."""
        slides_data = [
            {"layout": "title", "content": {"title": "Hello", "subtitle": "World"}},
            {"layout": "content", "content": {"title": "Content", "bullets": ["A", "B", "C"]}},
        ]
        output_path = tmp_path / "test_output.pptx"
        engine.generate(sample_template, slides_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_generate_infer_layouts(self, engine, sample_template, tmp_path):
        """Generate with layout inference."""
        slides_data = [
            {"content": {"title": "Hello", "subtitle": "World"}},
            {"content": {"title": "Section"}},
            {"content": {"title": "Content", "bullets": ["A", "B"]}},
        ]
        output_path = tmp_path / "test_inferred.pptx"
        engine.generate(sample_template, slides_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_infer_layout_method(self, engine):
        """Test _infer_layout mapping method."""
        assert engine._infer_layout("title") == "title"
        assert engine._infer_layout("content") == "content"
        assert engine._infer_layout("section_divider") == "section_divider"
