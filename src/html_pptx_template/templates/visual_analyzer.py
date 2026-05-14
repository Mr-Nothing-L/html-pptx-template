"""VisualAnalyzer - parses visual_analysis.md into structured layout configs."""

import re
from pathlib import Path
from typing import Dict, Optional

import yaml


class VisualAnalyzer:
    """Parse visual_analysis.md and extract layout recommendations."""

    def __init__(self, visual_path: Path):
        self.visual_path = Path(visual_path)

    def parse(self) -> Dict:
        """Parse visual_analysis.md and return structured layout configs."""
        text = self.visual_path.read_text(encoding="utf-8")
        section = self._extract_slide_design_section(text)
        if not section:
            return {}

        configs = {}
        for line in section.splitlines():
            line = line.strip()
            if not line.startswith("-"):
                continue

            slide_type, description = self._parse_bullet(line)
            if slide_type and description:
                configs[slide_type] = self._extract_config(slide_type, description)

        return configs

    def generate_layouts_yaml(self, template_dir: Path) -> Path:
        """Generate layouts.yaml in template_dir from parsed recommendations."""
        configs = self.parse()
        output_path = Path(template_dir) / "layouts.yaml"
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(configs, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        return output_path

    def _extract_slide_design_section(self, text: str) -> str:
        """Extract the '## Slide Design Recommendations' section."""
        match = re.search(
            r"##\s+Slide Design Recommendations\s*\n(.*?)(?=\n##\s|\Z)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        return match.group(1) if match else ""

    def _parse_bullet(self, line: str) -> tuple:
        """Parse a bullet like '- **Title Slide**: description'."""
        match = re.match(r"-\s*\*\*(.+?)\*\*\s*:\s*(.+)", line)
        if not match:
            return None, None
        slide_type = self._normalize_slide_type(match.group(1))
        return slide_type, match.group(2).strip()

    def _normalize_slide_type(self, raw: str) -> str:
        """Convert slide type names to snake_case keys."""
        mapping = {
            "title slide": "title",
            "content slide": "content",
            "section divider": "section_divider",
            "image slide": "image_slide",
            "image-heavy slide": "image_slide",
            "data slide": "data_slide",
            "chart/data slide": "data_slide",
        }
        key = raw.lower().strip()
        return mapping.get(key, key.replace(" ", "_"))

    def _extract_config(self, slide_type: str, description: str) -> Dict:
        """Extract structured config from a description string."""
        desc_lower = description.lower()
        config: Dict = {}

        # Background color
        config["background"] = self._detect_background(desc_lower)

        # Text alignment
        config["title_align"] = self._detect_alignment(desc_lower)

        # Uppercase
        config["title_uppercase"] = self._detect_uppercase(desc_lower)

        # Title size
        config["title_size_level"] = self._detect_size(desc_lower)

        # Text color
        text_color = self._detect_text_color(desc_lower)
        if text_color:
            config["text_color"] = text_color

        # Slide-type-specific fields
        if slide_type == "title":
            config["has_subtitle"] = "no subtitle" not in desc_lower or "small subtitle" in desc_lower
            if config["has_subtitle"]:
                config["subtitle_size_level"] = (
                    "caption" if "small subtitle" in desc_lower else "body"
                )
            config["spacing"] = self._detect_spacing(desc_lower)

        elif slide_type == "content":
            config["has_bullets"] = "bullet" in desc_lower or "bullets" in desc_lower
            config["bullet_spacing"] = self._detect_spacing(desc_lower)
            config["has_header_bar"] = "header bar" in desc_lower and "no " not in desc_lower

        elif slide_type == "section_divider":
            pass  # Already handled above

        elif slide_type == "image_slide":
            config["image_position"] = self._detect_image_position(desc_lower)
            config["image_style"] = self._detect_image_style(desc_lower)
            config["caption_position"] = self._detect_caption_position(desc_lower)

        elif slide_type == "data_slide":
            config["chart_style"] = self._detect_chart_style(desc_lower)

        return config

    def _detect_background(self, desc: str) -> str:
        """Map background color hints to theme tokens."""
        if "black background" in desc or "dark navy" in desc or "navy background" in desc:
            return "primary"
        if "light gray" in desc or "warm gray" in desc or "gray background" in desc:
            return "surface"
        if "light background" in desc:
            return "surface"
        if "white" in desc:
            return "background"
        if "gradient" in desc:
            return "primary"
        return "background"

    def _detect_alignment(self, desc: str) -> str:
        """Map alignment hints."""
        if "centered" in desc or "center-aligned" in desc or "center" in desc:
            return "center"
        if "left-aligned" in desc or "left aligned" in desc:
            return "left"
        return "center"

    def _detect_uppercase(self, desc: str) -> bool:
        """Detect all-caps / uppercase."""
        return "all caps" in desc or "uppercase" in desc or "all-caps" in desc

    def _detect_size(self, desc: str) -> str:
        """Map size adjectives to size levels."""
        if "massive" in desc:
            return "h1"
        if "large" in desc or "bold" in desc:
            return "h2"
        if "small" in desc or "minimal" in desc:
            return "caption"
        return "h2"

    def _detect_text_color(self, desc: str) -> Optional[str]:
        """Detect explicit text color hints."""
        if "white" in desc and ("text" in desc or "title" in desc or "bold" in desc):
            return "text_on_primary"
        if "black" in desc and ("text" in desc or "data" in desc):
            return "text_primary"
        return None

    def _detect_spacing(self, desc: str) -> str:
        """Map spacing hints."""
        if "sparse" in desc or "generous" in desc or "airy" in desc:
            return "generous"
        return "normal"

    def _detect_image_position(self, desc: str) -> str:
        """Map image position hints."""
        if "full-bleed" in desc or "full bleed" in desc:
            return "full_bleed"
        if "one side" in desc:
            return "side"
        return "center"

    def _detect_image_style(self, desc: str) -> str:
        """Map image style hints."""
        if "rounded corners" in desc or "rounded" in desc:
            return "rounded_corners"
        return "default"

    def _detect_caption_position(self, desc: str) -> str:
        """Map caption position hints."""
        if "caption below" in desc or "below" in desc:
            return "below"
        return "none"

    def _detect_chart_style(self, desc: str) -> str:
        """Map chart style hints."""
        if "monochrome" in desc or "black data" in desc:
            return "monochrome"
        if "gradient" in desc:
            return "gradient"
        return "default"
