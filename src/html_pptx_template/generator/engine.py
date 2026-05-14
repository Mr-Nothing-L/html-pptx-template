"""GeneratorEngine - parses content and generates PPTX files."""

import re
from pathlib import Path
from typing import List, Dict

from pptx import Presentation

from html_pptx_template.templates.schema import LayoutSlide, LayoutElement
from html_pptx_template.generator.slide_builder import SlideBuilder


class GeneratorEngine:
    """Parse user markdown into slides and generate PPTX files."""

    # Map explicit layout hints to internal layout names
    _LAYOUT_HINT_MAP = {
        "title": "title",
        "section": "section_divider",
        "content": "content",
        "image": "image_left",
        "image-left": "image_left",
        "image_left": "image_left",
        "two_column": "two_column",
        "two-column": "two_column",
        "table": "table",
        "chart": "chart",
        "image_gallery": "image_gallery",
        "image-gallery": "image_gallery",
        "gallery": "image_gallery",
    }

    _IMAGE_RE = re.compile(r"!\[(.*?)\]\((.*?)\)")
    _COLS_PLACEHOLDER = "\x00COLS\x00"

    # Regex to split on standalone `---` lines only (not inside table rows like `| --- | --- |`)
    _SLIDE_SEP_RE = re.compile(r"^\s*---\s*$", re.MULTILINE)

    def parse_content(self, markdown: str) -> List[Dict]:
        """Parse user markdown into list of {layout, content} dicts.

        Split by standalone '---' lines. Parse # title, ## subtitle, - bullets, | tables, body text.
        Supports !layout: hints, ![alt](path) images, and ---cols--- separators.
        """
        if not markdown or not markdown.strip():
            return []

        # Protect ---cols--- from the outer --- slide separator split
        protected = markdown.replace("---cols---", self._COLS_PLACEHOLDER)
        raw_slides = self._SLIDE_SEP_RE.split(protected)
        result = []

        for idx, raw_slide in enumerate(raw_slides):
            raw_slide = raw_slide.strip()
            if not raw_slide:
                continue

            # Restore the column separator
            raw_slide = raw_slide.replace(self._COLS_PLACEHOLDER, "---cols---")
            lines = raw_slide.split("\n")
            explicit_layout = self._extract_layout_hint(lines)

            if any(line.strip() == "---cols---" for line in lines):
                content = self._parse_two_column_slide(lines)
            else:
                content = self._parse_slide_lines(lines)

            layout = explicit_layout or self._infer_layout_from_content(
                content, slide_index=idx, total_slides=len(raw_slides)
            )
            result.append({"layout": layout, "content": content})

        return result

    def _extract_layout_hint(self, lines: List[str]) -> str | None:
        """Extract and remove !layout: hint from lines. Returns mapped layout name or None."""
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("!layout:"):
                hint = stripped[8:].strip().lower()
                lines.pop(i)
                return self._LAYOUT_HINT_MAP.get(hint)
        return None

    def _parse_slide_lines(self, lines: List[str]) -> Dict:
        """Parse lines of a single slide into content dict."""
        content = {}
        bullets = []
        body_lines = []
        table_lines = []
        images = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("!layout:"):
                continue

            if line.startswith("!chart:"):
                chart_type = line[7:].strip().lower()
                content["chart"] = {"type": chart_type}
                continue

            if line.startswith("# ") and not line.startswith("## "):
                content["title"] = line[2:].strip()
            elif line.startswith("## "):
                content["subtitle"] = line[3:].strip()
            elif line.startswith("- ") or line.startswith("* "):
                bullets.append(line[2:].strip())
            elif line.startswith("|"):
                table_lines.append(line)
            else:
                line_images = self._extract_images(line)
                if line_images:
                    images.extend(line_images)
                    text_only = self._strip_image_markdown(line)
                    if text_only.strip():
                        body_lines.append(text_only.strip())
                else:
                    body_lines.append(line)

        if bullets:
            content["bullets"] = bullets

        if table_lines:
            table = self._parse_table(table_lines)
            if table:
                content["table"] = table

        if body_lines:
            content["body"] = " ".join(body_lines)

        if images:
            content["images"] = images
            if len(images) >= 2:
                content["gallery"] = images

        return content

    def _parse_two_column_slide(self, lines: List[str]) -> Dict:
        """Parse a slide with ---cols--- separator into left/right content."""
        left_lines = []
        right_lines = []
        current = left_lines

        for line in lines:
            if line.strip() == "---cols---":
                current = right_lines
                continue
            current.append(line)

        return {
            "left": self._parse_slide_lines(left_lines),
            "right": self._parse_slide_lines(right_lines),
        }

    def _extract_images(self, line: str) -> List[Dict]:
        """Extract image references from a line."""
        return [
            {"alt": alt.strip(), "path": path.strip()}
            for alt, path in self._IMAGE_RE.findall(line)
        ]

    def _strip_image_markdown(self, line: str) -> str:
        """Remove image markdown from a line, leaving only plain text."""
        return self._IMAGE_RE.sub("", line).strip()

    def _parse_table(self, lines: List[str]) -> Dict | None:
        """Parse table lines into headers and rows dict."""
        rows = []
        for line in lines:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells:
                continue
            if all(set(c.strip()) <= {"-", ":", " "} for c in cells):
                continue
            rows.append(cells)

        if not rows:
            return None

        return {
            "headers": rows[0],
            "rows": rows[1:] if len(rows) > 1 else [],
        }

    def _infer_layout_from_content(
        self, content: Dict, slide_index: int = 0, total_slides: int = 1
    ) -> str:
        """Infer layout name from content structure.

        Priority order:
        1. two_column (left/right keys)
        2. table
        3. chart
        4. image_gallery
        5. image_full
        6. image_left
        7. title (first slide with title+subtitle, or title+subtitle+no other content)
        8. section_divider (heading-only, not first slide)
        9. content (default)
        """
        if "left" in content and "right" in content:
            return "two_column"

        has_title = "title" in content
        has_subtitle = "subtitle" in content
        has_bullets = "bullets" in content
        has_body = "body" in content
        has_images = "images" in content
        has_table = "table" in content
        has_chart = "chart" in content
        has_gallery = "gallery" in content

        if has_table:
            return "table"

        if has_chart:
            return "chart"

        if has_gallery:
            return "image_gallery"

        if has_images and not has_body and not has_bullets and not has_title and not has_subtitle:
            return "image_full"

        if has_images and (has_body or has_bullets or has_title):
            return "image_left"

        # First slide (index 0) with title + subtitle → title layout
        if slide_index == 0 and has_title and has_subtitle and not has_bullets and not has_body:
            return "title"

        # First slide with only title (no subtitle) → section_divider (unusual but possible)
        if slide_index == 0 and has_title and not has_subtitle and not has_bullets and not has_body and not has_images:
            return "section_divider"

        # Non-first slides with only heading → section_divider
        if slide_index > 0 and has_title and not has_subtitle and not has_bullets and not has_body and not has_images:
            return "section_divider"

        # Title + subtitle + no other content (any slide position) → title
        if has_title and has_subtitle and not has_bullets and not has_body and not has_images:
            return "title"

        return "content"

    def generate(self, template, slides_data: List[Dict], output_path: str, assets_dir: Path = None):
        """Generate PPTX file from template + slides data."""
        prs = Presentation()
        prs.slide_width = int(template.theme.slide_width * 914400)
        prs.slide_height = int(template.theme.slide_height * 914400)

        builder = SlideBuilder(template.theme, prs, assets_dir=assets_dir)

        for slide_data in slides_data:
            layout_name = slide_data.get("layout")
            content = slide_data.get("content", {})

            layout = None
            for lo in template.layouts:
                if lo.name == layout_name or lo.slide_type == layout_name:
                    layout = lo
                    break

            if layout is None:
                layout = self._create_fallback_layout(layout_name)

            builder.build(layout, content)

        prs.save(output_path)

    def _create_fallback_layout(self, layout_name: str) -> LayoutSlide:
        """Create a fallback LayoutSlide for any supported layout type."""
        if layout_name == "title":
            return LayoutSlide(
                name="title",
                slide_type="title",
                background="surface",
                elements=[
                    LayoutElement(type="title", style={"level": "h1", "align": "centered"}),
                    LayoutElement(type="subtitle", style={"level": "body", "align": "centered"}),
                ],
            )
        if layout_name == "section_divider":
            return LayoutSlide(
                name="section_divider",
                slide_type="section_divider",
                background="primary",
                elements=[
                    LayoutElement(type="title", style={"level": "h1", "align": "centered"}),
                ],
            )
        if layout_name == "two_column":
            return LayoutSlide(
                name="two_column",
                slide_type="two_column",
                background="background",
                elements=[
                    LayoutElement(type="title", style={"level": "h2", "align": "left"}),
                    LayoutElement(type="content", style={"level": "body", "align": "left"}),
                ],
            )
        if layout_name == "image_left":
            return LayoutSlide(
                name="image_left",
                slide_type="image_left",
                background="background",
                elements=[
                    LayoutElement(type="title", style={"level": "h2", "align": "left"}),
                    LayoutElement(type="content", style={"level": "body", "align": "left"}),
                ],
            )
        if layout_name == "image_full":
            return LayoutSlide(
                name="image_full",
                slide_type="image_full",
                background="background",
                elements=[
                    LayoutElement(type="content", style={"level": "body", "align": "centered"}),
                ],
            )
        if layout_name == "table":
            return LayoutSlide(
                name="table",
                slide_type="table",
                background="background",
                elements=[
                    LayoutElement(type="title", style={"level": "h2", "align": "left"}),
                    LayoutElement(type="content", style={"level": "body", "align": "left"}),
                ],
            )
        if layout_name == "chart":
            return LayoutSlide(
                name="chart",
                slide_type="chart",
                background="background",
                elements=[
                    LayoutElement(type="title", style={"level": "h2", "align": "left"}),
                    LayoutElement(type="content", style={"level": "body", "align": "centered"}),
                ],
            )
        if layout_name == "image_gallery":
            return LayoutSlide(
                name="image_gallery",
                slide_type="image_gallery",
                background="background",
                elements=[
                    LayoutElement(type="title", style={"level": "h2", "align": "left"}),
                ],
            )
        # Default fallback
        return LayoutSlide(
            name="content",
            slide_type="content",
            background="background",
            elements=[
                LayoutElement(type="title", style={"level": "h2", "align": "left"}),
                LayoutElement(type="content", style={"level": "body", "align": "left"}),
            ],
        )

    def _infer_layout(self, content_type: str) -> str:
        """Map content type to layout name."""
        mapping = {
            "title": "title",
            "content": "content",
            "section_divider": "section_divider",
            "two_column": "two_column",
            "image_left": "image_left",
            "image_full": "image_full",
            "table": "table",
            "chart": "chart",
            "image_gallery": "image_gallery",
        }
        return mapping.get(content_type, "content")
