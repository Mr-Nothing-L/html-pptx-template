"""LayoutParser - parses layout markdown into LayoutSlide objects."""

import re
from typing import List

from html_pptx_template.templates.schema import LayoutSlide, LayoutElement


class LayoutParser:
    """Parse layout.md into list of LayoutSlide objects."""

    def parse(self, markdown: str) -> List[LayoutSlide]:
        """Parse layout.md into list of LayoutSlide objects.

        Split by ## headings. Parse Type, Background, Elements.
        """
        if not markdown or not markdown.strip():
            return []

        slides = []
        # Split by ## headings
        sections = re.split(r'\n## ', markdown.strip())

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # First section may not start with ##
            lines = section.split('\n')
            name = lines[0].strip().lstrip('#').strip()

            slide_type = "content"
            background = "background"
            elements = []
            in_elements = False

            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue

                if line.lower().startswith("type:"):
                    slide_type = line.split(':', 1)[1].strip()
                elif line.lower().startswith("background:"):
                    background = line.split(':', 1)[1].strip()
                elif line.lower() == "elements:":
                    in_elements = True
                elif in_elements and line.startswith('-'):
                    elem_text = line[1:].strip()
                    elem = self._parse_element(elem_text)
                    if elem:
                        elements.append(elem)

            slides.append(
                LayoutSlide(
                    name=name,
                    slide_type=slide_type,
                    background=background,
                    elements=elements,
                )
            )

        return slides

    def _parse_element(self, text: str) -> LayoutElement:
        """Parse element text like 'Title (h1, centered)' into LayoutElement."""
        text = text.strip()

        # Extract parenthetical content
        match = re.match(r'(.+?)\s*\(([^)]+)\)\s*$', text)
        if match:
            name_part = match.group(1).strip()
            params = [p.strip() for p in match.group(2).split(',')]
        else:
            name_part = text
            params = []

        # Detect type from name
        name_lower = name_part.lower()
        if 'header' in name_lower or 'bar' in name_lower:
            elem_type = "header_bar"
        elif 'subtitle' in name_lower:
            elem_type = "subtitle"
        elif 'title' in name_lower:
            elem_type = "title"
        elif 'content' in name_lower:
            elem_type = "content"
        elif 'column' in name_lower:
            elem_type = "column"
        elif 'image' in name_lower:
            elem_type = "image"
        else:
            elem_type = "content"

        style = {}
        for param in params:
            param = param.strip()
            if param in ('h1', 'h2', 'h3', 'body'):
                style['level'] = param
            elif param in ('centered', 'left', 'right'):
                style['align'] = param
            elif param.endswith('%'):
                style['width_pct'] = param

        return LayoutElement(type=elem_type, style=style)
