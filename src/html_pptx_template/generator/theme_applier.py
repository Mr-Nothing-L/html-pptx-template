"""ThemeApplier - applies theme styles to PPTX slides."""

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from html_pptx_template.utils.color import hex_to_rgb


class ThemeApplier:
    """Apply theme colors, fonts, and spacing to PPTX elements."""

    def __init__(self, theme):
        self.theme = theme

    def apply_slide_background(self, slide, color_key: str = "background"):
        """Apply solid color background to slide."""
        background = slide.background
        fill = background.fill
        fill.solid()
        color_hex = getattr(self.theme.colors, color_key, self.theme.colors.background)
        r, g, b = hex_to_rgb(color_hex)
        fill.fore_color.rgb = RGBColor(r, g, b)

    def is_dark_color(self, color_hex: str) -> bool:
        """Determine if a color is dark based on luminance."""
        r, g, b = hex_to_rgb(color_hex)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5

    def get_contrast_text_color(self, bg_color_key: str) -> str:
        """Return appropriate text color key for a background color."""
        color_hex = getattr(self.theme.colors, bg_color_key, self.theme.colors.background)
        if self.is_dark_color(color_hex):
            return "text_on_primary"
        return "text_primary"

    def apply_text_style(self, run, text_type: str = "body", level: str = None,
                         uppercase: bool = False, letter_spacing: float = None):
        """Apply theme font, size, weight, color to a text run.

        text_type: 'heading', 'body', 'caption'
        level: for heading, 'h1', 'h2', 'h3'
        uppercase: convert text to uppercase
        letter_spacing: placeholder — python-pptx does not support letter spacing
        """
        font_config = getattr(self.theme.fonts, text_type, self.theme.fonts.body)

        # Font family - take first font name
        font_family = font_config.family
        if "," in font_family:
            font_family = font_family.split(",")[0].strip()
        run.font.name = font_family

        # Font size
        if text_type == "heading" and level and font_config.sizes:
            size_pt = font_config.sizes.get(level, 24)
        else:
            size_pt = font_config.size or 18
        run.font.size = Pt(size_pt)

        # Font weight / style
        weight = font_config.weight or "normal"
        run.font.bold = "bold" in weight.lower()
        run.font.italic = "italic" in weight.lower()

        # Uppercase
        if uppercase:
            run.text = run.text.upper()

        # Letter spacing is not supported by python-pptx; parameter reserved for future use.
        _ = letter_spacing

        # Font color
        color_key = font_config.color
        color_hex = getattr(self.theme.colors, color_key, self.theme.colors.text_primary)
        r, g, b = hex_to_rgb(color_hex)
        run.font.color.rgb = RGBColor(r, g, b)

    def add_shape_with_fill(self, slide, shape_type, left, top, width, height, color_key: str = "primary"):
        """Add a shape with solid fill from theme color."""
        shape = slide.shapes.add_shape(shape_type, left, top, width, height)
        fill = shape.fill
        fill.solid()
        color_hex = getattr(self.theme.colors, color_key, self.theme.colors.primary)
        r, g, b = hex_to_rgb(color_hex)
        fill.fore_color.rgb = RGBColor(r, g, b)
        # Remove line/border
        shape.line.fill.background()
        return shape

    def get_slide_dimensions(self):
        """Return (width, height) as Inches tuples."""
        return (Inches(self.theme.slide_width), Inches(self.theme.slide_height))
