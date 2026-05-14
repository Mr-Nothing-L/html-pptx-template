"""Template manager for creating, loading, and managing templates."""

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import yaml

from html_pptx_template.templates.index import TemplateIndex
from html_pptx_template.templates.schema import (
    LayoutSlide,
    Template,
    TemplateMeta,
    Theme,
)
from html_pptx_template.utils.validators import sanitize_template_id, validate_url


class TemplateManager:
    """Manager for creating, listing, loading, and deleting templates."""

    def __init__(self, templates_dir: Path, config_dir: Optional[Path] = None):
        """Initialize manager. config_dir defaults to ~/.config/html-pptx-template/"""
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        if config_dir is None:
            config_dir = Path.home() / ".config" / "html-pptx-template"
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.index = TemplateIndex(self.templates_dir)

    def create(
        self,
        url: str,
        name: str,
        theme: Theme,
        layouts: Optional[List[LayoutSlide]] = None,
        screenshots: Optional[List[str]] = None,
    ) -> Template:
        """Create new template from URL+name+theme. Auto-generates unique ID (name-YYYYMMDD[-N]).
        Saves meta.yaml, theme.yaml, layout.md, visual_analysis.md, creates assets/ dir."""
        validate_url(url)
        template_id = self._generate_unique_id(name)

        template_dir = self.templates_dir / template_id
        template_dir.mkdir(parents=True, exist_ok=True)

        # Create meta
        meta = TemplateMeta(
            id=template_id,
            name=name,
            source_url=url,
        )

        # Create template object
        template = Template(
            meta=meta,
            theme=theme,
            layouts=layouts or [],
        )

        # Write meta.yaml
        meta_dict = meta.model_dump(mode="json")
        self._write_yaml(template_dir / "meta.yaml", meta_dict)

        # Write theme.yaml
        theme_dict = self._theme_to_dict(theme)
        self._write_yaml(template_dir / "theme.yaml", theme_dict)

        # Write layout.md
        layout_path = template_dir / "layout.md"
        layout_path.write_text(self._default_layout_md(), encoding="utf-8")

        # Create assets directory
        assets_dir = template_dir / "assets"
        assets_dir.mkdir(exist_ok=True)

        # Write visual_analysis.md template
        visual_path = template_dir / "visual_analysis.md"
        visual_path.write_text(self._visual_analysis_template(), encoding="utf-8")

        # Generate layouts.yaml from visual analysis
        from html_pptx_template.templates.visual_analyzer import VisualAnalyzer

        analyzer = VisualAnalyzer(visual_path)
        analyzer.generate_layouts_yaml(template_dir)

        return template

    def list(self) -> List[TemplateMeta]:
        """List all templates (delegates to index)."""
        return self.index.scan()

    def load(self, template_id: str) -> Optional[Template]:
        """Load full template (meta + theme)."""
        template_dir = self.templates_dir / template_id
        if not template_dir.exists():
            return None

        meta = self.index.get_meta(template_id)
        if meta is None:
            return None

        theme_path = template_dir / "theme.yaml"
        if not theme_path.exists():
            return None

        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                theme_data = yaml.safe_load(f)
            theme = Theme.model_validate(theme_data)
        except (yaml.YAMLError, OSError, ValueError):
            return None

        return Template(meta=meta, theme=theme)

    def delete(self, template_id: str) -> bool:
        """Delete template directory and clear default if needed."""
        template_dir = self.templates_dir / template_id
        if not template_dir.exists():
            return False

        import shutil

        shutil.rmtree(template_dir)

        # Clear default if this was the default template
        config = self._read_config()
        if config.get("default_template") == template_id:
            config.pop("default_template", None)
            self._write_config(config)

        return True

    def set_default(self, template_id: str) -> bool:
        """Set default template in ~/.config/html-pptx-template/config.yaml"""
        if not self.index.template_exists(template_id):
            return False

        config = self._read_config()
        config["default_template"] = template_id
        self._write_config(config)
        return True

    def get_default(self) -> Optional[TemplateMeta]:
        """Get default template from config."""
        config = self._read_config()
        default_id = config.get("default_template")
        if default_id is None:
            return None
        return self.index.get_meta(default_id)

    def _read_config(self) -> dict:
        """Read config file, return empty dict if not exists."""
        config_path = self.config_dir / "config.yaml"
        if not config_path.exists():
            return {}
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
        except (yaml.YAMLError, OSError):
            return {}

    def _write_config(self, config: dict):
        """Write config to config file."""
        config_path = self.config_dir / "config.yaml"
        self._write_yaml(config_path, config)

    def _write_yaml(self, path: Path, data: dict):
        """Write data as YAML to path."""
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    def _theme_to_dict(self, theme: Theme) -> dict:
        """Convert Theme to a dictionary for YAML serialization."""
        return theme.model_dump(mode="json")

    def _default_layout_md(self) -> str:
        """Return default layout.md content."""
        return (
            "# Slide Layouts\n\n"
            "## title\n"
            "- Type: title slide\n"
            "- Background: primary color\n"
            "- Elements:\n"
            "  - Title (h1, centered)\n"
            "  - Subtitle (body, centered)\n\n"
            "## content\n"
            "- Type: content slide\n"
            "- Background: background color\n"
            "- Elements:\n"
            "  - Header bar: primary color\n"
            "  - Slide title (h3, left-aligned)\n"
            "  - Content area: body text with bullets\n\n"
            "## section_divider\n"
            "- Type: section divider\n"
            "- Background: secondary color\n"
            "- Elements:\n"
            "  - Section title (h2, centered, white text)\n\n"
            "## two_column\n"
            "- Type: content slide\n"
            "- Background: background color\n"
            "- Elements:\n"
            "  - Header bar: primary color\n"
            "  - Left column: 50% width (body text)\n"
            "  - Right column: 50% width (body text)\n\n"
            "## image_left\n"
            "- Type: content slide with image\n"
            "- Background: background color\n"
            "- Elements:\n"
            "  - Header bar: primary color\n"
            "  - Left 40%: image placeholder\n"
            "  - Right 60%: text content\n"
        )

    def _visual_analysis_template(self) -> str:
        """Return visual_analysis.md template for AI-assisted style analysis."""
        return (
            "# Visual Style Analysis\n\n"
            "> This file is meant to be filled in by AI visual analysis of the screenshots in `assets/`.\n"
            "> The AI should view the screenshots and describe the visual style in detail.\n\n"
            "## Overall Impression\n\n"
            "- **Mood/Vibe**: [e.g., Professional, Playful, Minimalist, Bold, Elegant]\n"
            "- **Design Era**: [e.g., Modern flat, Brutalist, Skeuomorphic, Glassmorphism]\n"
            "- **Target Audience**: [e.g., Enterprise, Creative professionals, General consumers]\n\n"
            "## Color Usage\n\n"
            "- **Color Strategy**: [e.g., Monochromatic, Complementary, Triadic, Neutral with accent]\n"
            "- **Background Patterns**: [e.g., Solid colors, Gradients, Subtle textures, White space heavy]\n"
            "- **Color Temperature**: [e.g., Warm, Cool, Neutral]\n"
            "- **Dark/Light Mode**: [e.g., Light dominant, Dark dominant, Mixed]\n\n"
            "## Typography\n\n"
            "- **Type Style**: [e.g., Sans-serif modern, Serif classic, Mixed, Display-heavy]\n"
            "- **Hierarchy Clarity**: [e.g., Strong contrast, Subtle, Flat]\n"
            "- **Text Density**: [e.g., Sparse, Medium, Dense]\n"
            "- **Special Treatments**: [e.g., Uppercase headings, Italic accents, Letter spacing]\n\n"
            "## Layout & Structure\n\n"
            "- **Grid System**: [e.g., 12-column, Asymmetric, Full-bleed, Card-based]\n"
            "- **Spacing Rhythm**: [e.g., Generous whitespace, Compact, Structured padding]\n"
            "- **Alignment**: [e.g., Centered, Left-aligned, Mixed]\n"
            "- **Content Density**: [e.g., Minimal, Balanced, Content-heavy]\n\n"
            "## Imagery & Graphics\n\n"
            "- **Image Style**: [e.g., Photography, Illustration, 3D render, Abstract, Icons-only]\n"
            "- **Image Treatment**: [e.g., Full-color, Black & white, Duotone, Filtered, Rounded corners]\n"
            "- **Graphic Elements**: [e.g., Geometric shapes, Organic curves, Lines/dividers, Decorative patterns]\n"
            "- **Icon Style**: [e.g., Outline, Filled, Two-tone, Custom]\n\n"
            "## Decorative Details\n\n\n"
            "- **Corner Styles**: [e.g., Sharp, Rounded (small), Rounded (large), Pill-shaped]\n"
            "- **Shadow Usage**: [e.g., None, Subtle drop shadows, Heavy shadows, Glow effects]\n"
            "- **Border Style**: [e.g., No borders, Hairline, Thick, Dashed/dotted]\n"
            "- **Motion/Animation Feel**: [e.g., Static, Subtle transitions, Dynamic, Playful]\n"
            "- **Texture**: [e.g., Flat, Subtle grain, Glass effect, Gradient overlays]\n\n"
            "## Slide Design Recommendations\n\n"
            "Based on the above analysis, describe how slides should look:\n\n"
            "- **Title Slide**: [Describe ideal title slide design]\n"
            "- **Content Slide**: [Describe ideal content slide design]\n"
            "- **Section Divider**: [Describe ideal section divider design]\n"
            "- **Image Slide**: [Describe ideal image-heavy slide design]\n"
            "- **Data Slide**: [Describe ideal chart/data slide design]\n\n"
            "## Asset Suggestions\n\n"
            "- **Recommended Image Types**: [e.g., Lifestyle photography, Abstract backgrounds, Product shots]\n"
            "- **Color Overlay Suggestions**: [e.g., Dark overlay for text readability, Gradient overlays]\n"
            "- **Icon Recommendations**: [e.g., Use outline icons, Use filled icons, Avoid icons]\n"
        )

    def _generate_unique_id(self, name: str) -> str:
        """Generate a unique template ID from name and current date."""
        base_id = sanitize_template_id(name)
        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        candidate = f"{base_id}-{today_str}"

        if not (self.templates_dir / candidate).exists():
            return candidate

        # Append -1, -2, etc. until unique
        n = 1
        while True:
            candidate = f"{base_id}-{today_str}-{n}"
            if not (self.templates_dir / candidate).exists():
                return candidate
            n += 1
