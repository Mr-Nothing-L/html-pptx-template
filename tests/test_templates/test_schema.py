"""Tests for template schema models."""

import pytest
from html_pptx_template.templates.schema import Theme, TemplateMeta, Template, LayoutSlide


def test_theme_from_dict(sample_theme_dict):
    """Create Theme from a dict, verify all fields."""
    theme = Theme.model_validate(sample_theme_dict)
    assert theme.colors.primary == "#1E3A5F"
    assert theme.colors.secondary == "#4A90D9"
    assert theme.colors.accent == "#E67E22"
    assert theme.colors.background == "#FFFFFF"
    assert theme.colors.surface == "#F5F7FA"
    assert theme.colors.text_primary == "#2C3E50"
    assert theme.colors.text_secondary == "#7F8C8D"
    assert theme.colors.text_on_primary == "#FFFFFF"
    assert theme.fonts.heading.family == "Arial, sans-serif"
    assert theme.fonts.heading.sizes == {"h1": 44, "h2": 32, "h3": 24}
    assert theme.fonts.heading.weight == "bold"
    assert theme.fonts.body.size == 18
    assert theme.fonts.caption.size == 14
    assert theme.spacing.slide_padding == [40, 40, 40, 40]
    assert theme.spacing.content_gap == 20
    assert theme.spacing.line_spacing == 1.5
    assert theme.aspect_ratio == "16:9"
    assert theme.slide_width == 10.0
    assert theme.slide_height == 5.625


def test_theme_color_validation():
    """Invalid color should raise ValueError."""
    with pytest.raises(ValueError):
        Theme.model_validate({
            "colors": {
                "primary": "not-a-color",
                "secondary": "#4A90D9",
                "accent": "#E67E22",
                "background": "#FFFFFF",
                "surface": "#F5F7FA",
                "text_primary": "#2C3E50",
                "text_secondary": "#7F8C8D",
                "text_on_primary": "#FFFFFF",
            },
            "fonts": {
                "heading": {"family": "Arial"},
                "body": {"family": "Arial"},
                "caption": {"family": "Arial"},
            },
            "spacing": {
                "slide_padding": [40, 40, 40, 40],
                "content_gap": 20,
                "line_spacing": 1.5,
            },
        })


def test_template_meta():
    """Create TemplateMeta, verify fields."""
    meta = TemplateMeta(
        id="test-template",
        name="Test Template",
        source_url="https://example.com",
        source_title="Example",
        description="A test template",
    )
    assert meta.id == "test-template"
    assert meta.name == "Test Template"
    assert meta.source_url == "https://example.com"
    assert meta.source_title == "Example"
    assert meta.description == "A test template"
    assert meta.version == 1
    assert meta.tags == []


def test_template_full(sample_theme_dict):
    """Create full Template with meta + theme."""
    theme = Theme.model_validate(sample_theme_dict)
    meta = TemplateMeta(
        id="test-template",
        name="Test",
        source_url="https://example.com",
    )
    template = Template(meta=meta, theme=theme, layouts=[])
    assert template.meta.id == "test-template"
    assert template.theme.colors.primary == "#1E3A5F"
    assert template.layouts == []
