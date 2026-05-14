"""Tests for LayoutParser - Task 11."""

import pytest

from html_pptx_template.generator.layout_parser import LayoutParser
from html_pptx_template.templates.schema import LayoutSlide, LayoutElement


@pytest.fixture
def parser():
    return LayoutParser()


class TestParseSimpleLayout:
    def test_parse_simple_layout(self, parser):
        """Parse title and content layouts."""
        markdown = """## Title Slide
Type: title
Background: background
Elements:
- Title (h1, centered)
- Subtitle (body, centered)

## Content Slide
Type: content
Background: background
Elements:
- Header Bar (h2, left)
- Content (body, left)
"""
        slides = parser.parse(markdown)
        assert len(slides) == 2

        # First slide
        assert slides[0].name == "Title Slide"
        assert slides[0].slide_type == "title"
        assert slides[0].background == "background"
        assert len(slides[0].elements) == 2
        assert slides[0].elements[0].type == "title"
        assert slides[0].elements[0].style.get("level") == "h1"
        assert slides[0].elements[0].style.get("align") == "centered"
        assert slides[0].elements[1].type == "subtitle"
        assert slides[0].elements[1].style.get("level") == "body"

        # Second slide
        assert slides[1].name == "Content Slide"
        assert slides[1].slide_type == "content"
        assert slides[1].elements[0].type == "header_bar"
        assert slides[1].elements[1].type == "content"


class TestParseLayoutWithPosition:
    def test_parse_two_column_layout(self, parser):
        """Parse two_column layout with width percentages."""
        markdown = """## Two Column
Type: two_column
Background: background
Elements:
- Title (h2, left)
- Left Column (body, left, 50%)
- Right Column (body, left, 50%)
"""
        slides = parser.parse(markdown)
        assert len(slides) == 1
        assert slides[0].name == "Two Column"
        assert slides[0].slide_type == "two_column"
        assert len(slides[0].elements) == 3
        assert slides[0].elements[1].style.get("width_pct") == "50%"
        assert slides[0].elements[2].style.get("width_pct") == "50%"


class TestParseEmpty:
    def test_parse_empty(self, parser):
        """Empty string returns empty list."""
        slides = parser.parse("")
        assert slides == []

    def test_parse_whitespace_only(self, parser):
        """Whitespace-only string returns empty list."""
        slides = parser.parse("   \n\n  ")
        assert slides == []


class TestParseNoElements:
    def test_parse_no_elements(self, parser):
        """Layout without elements list."""
        markdown = """## Section Divider
Type: section_divider
Background: primary
"""
        slides = parser.parse(markdown)
        assert len(slides) == 1
        assert slides[0].name == "Section Divider"
        assert slides[0].slide_type == "section_divider"
        assert slides[0].background == "primary"
        assert slides[0].elements == []


class TestParseElement:
    def test_parse_title_element(self, parser):
        """Parse element text into LayoutElement."""
        elem = parser._parse_element("Title (h1, centered)")
        assert elem.type == "title"
        assert elem.style["level"] == "h1"
        assert elem.style["align"] == "centered"

    def test_parse_content_element(self, parser):
        """Parse content element with width."""
        elem = parser._parse_element("Content (body, left, 50%)")
        assert elem.type == "content"
        assert elem.style["level"] == "body"
        assert elem.style["align"] == "left"
        assert elem.style["width_pct"] == "50%"

    def test_parse_image_element(self, parser):
        """Parse image element."""
        elem = parser._parse_element("Image (body, left)")
        assert elem.type == "image"

    def test_parse_column_element(self, parser):
        """Parse column element."""
        elem = parser._parse_element("Left Column (body, left, 50%)")
        assert elem.type == "column"
