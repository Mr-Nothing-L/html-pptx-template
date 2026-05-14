"""Style analyzer for building Theme from parsed CSS data."""

from typing import Dict, List, Tuple

from html_pptx_template.templates.schema import ColorPalette, FontConfig, Spacing, Theme, Typography
from html_pptx_template.utils.color import hex_to_rgb


class StyleAnalyzer:
    """Analyze parsed styles and build a Theme."""

    DEFAULT_COLORS = {
        "primary": "#1E3A5F",
        "secondary": "#4A90D9",
        "accent": "#E67E22",
        "background": "#FFFFFF",
        "surface": "#F5F7FA",
        "text_primary": "#2C3E50",
        "text_secondary": "#7F8C8D",
        "text_on_primary": "#FFFFFF",
    }

    DEFAULT_FONT_FAMILY = "Arial"

    def build_theme(self, parsed: dict) -> Theme:
        """Build Theme from parsed CSS data.

        Args:
            parsed: Dict with normalized_colors, font_frequency,
                font_size_hierarchy, spacing_values, page_title.

        Returns:
            A Theme instance.
        """
        colors = self._classify_colors(parsed.get("normalized_colors", []))
        fonts = self._classify_fonts(
            parsed.get("font_frequency", {}),
            parsed.get("font_size_hierarchy", {}),
        )
        spacing = self._classify_spacing(parsed.get("spacing_values", []))

        return Theme(colors=colors, fonts=fonts, spacing=spacing)

    def _classify_colors(self, colors: List[str]) -> ColorPalette:
        """Classify colors into primary/secondary/accent/bg/text palette.

        Uses luminance and saturation analysis.

        Args:
            colors: List of normalized hex color strings.

        Returns:
            A ColorPalette instance.
        """
        if not colors:
            return ColorPalette(**self.DEFAULT_COLORS)

        # Compute luminance and saturation for each color
        color_data = []
        for c in colors:
            lum = self._luminance(c)
            sat = self._saturation(c)
            color_data.append((c, lum, sat))

        # Sort by luminance descending
        color_data.sort(key=lambda x: x[1], reverse=True)

        # Background: lightest (luminance > 0.9)
        bg_candidates = [c for c, lum, _ in color_data if lum > 0.9]
        background = bg_candidates[0] if bg_candidates else self.DEFAULT_COLORS["background"]

        # Surface: second lightest (luminance > 0.85)
        surface_candidates = [c for c, lum, _ in color_data if lum > 0.85 and c != background]
        surface = surface_candidates[0] if surface_candidates else self.DEFAULT_COLORS["surface"]

        # Remaining colors for other roles
        remaining = [(c, lum, sat) for c, lum, sat in color_data if c not in (background, surface)]

        # Primary: darkest with moderate saturation (lum < 0.4, not too dark)
        primary_candidates = [(c, lum, sat) for c, lum, sat in remaining if lum < 0.4 and sat > 0.05]
        primary_candidates.sort(key=lambda x: (x[1], -x[2]))  # darkest first, then most saturated
        primary = (
            primary_candidates[0][0]
            if primary_candidates
            else self.DEFAULT_COLORS["primary"]
        )

        # Secondary: next most prominent (moderate luminance, some saturation)
        secondary_candidates = [
            (c, lum, sat) for c, lum, sat in remaining
            if c != primary and 0.2 < lum < 0.7 and sat > 0.1
        ]
        secondary_candidates.sort(key=lambda x: x[2], reverse=True)
        secondary = (
            secondary_candidates[0][0]
            if secondary_candidates
            else self.DEFAULT_COLORS["secondary"]
        )

        # Accent: highest saturation, not too light/dark (0.3 < lum < 0.8, sat > 0.3)
        accent_candidates = [
            (c, lum, sat) for c, lum, sat in remaining
            if c not in (primary, secondary) and 0.3 < lum < 0.8 and sat > 0.3
        ]
        accent_candidates.sort(key=lambda x: x[2], reverse=True)
        accent = (
            accent_candidates[0][0]
            if accent_candidates
            else self.DEFAULT_COLORS["accent"]
        )

        # Text primary: dark color closest to lum=0.15, prefer darker colors
        text_primary_candidates = [
            (c, lum, sat) for c, lum, sat in remaining
            if c not in (primary, secondary, accent)
        ]
        # Sort by: prefer darker (lower lum), then closest to 0.15
        text_primary_candidates.sort(key=lambda x: (x[1], abs(x[1] - 0.15)))
        text_primary = (
            text_primary_candidates[0][0]
            if text_primary_candidates
            else self.DEFAULT_COLORS["text_primary"]
        )

        # Text secondary: gray color closest to lum=0.45
        text_secondary_candidates = [
            (c, lum, sat) for c, lum, sat in remaining
            if 0.3 < lum < 0.6 and sat < 0.15
        ]
        text_secondary_candidates.sort(key=lambda x: abs(x[1] - 0.45))
        text_secondary = (
            text_secondary_candidates[0][0]
            if text_secondary_candidates
            else self.DEFAULT_COLORS["text_secondary"]
        )

        # Text on primary: white/black based on primary luminance
        primary_lum = self._luminance(primary)
        text_on_primary = "#FFFFFF" if primary_lum < 0.5 else "#000000"

        return ColorPalette(
            primary=primary,
            secondary=secondary,
            accent=accent,
            background=background,
            surface=surface,
            text_primary=text_primary,
            text_secondary=text_secondary,
            text_on_primary=text_on_primary,
        )

    def _classify_fonts(
        self, font_freq: Dict[str, int], size_hierarchy: Dict[str, int]
    ) -> Typography:
        """Pick most frequent font, build heading/body/caption config.

        Args:
            font_freq: Dict mapping font family to occurrence count.
            size_hierarchy: Dict with h1, h2, h3, body sizes.

        Returns:
            A Typography instance.
        """
        if font_freq:
            most_frequent = max(font_freq, key=font_freq.get)
        else:
            most_frequent = self.DEFAULT_FONT_FAMILY

        heading_sizes = {}
        for key in ("h1", "h2", "h3"):
            if key in size_hierarchy:
                heading_sizes[key] = size_hierarchy[key]

        heading = FontConfig(
            family=most_frequent,
            sizes=heading_sizes or None,
            weight="bold",
            color="text_primary",
        )
        body = FontConfig(
            family=most_frequent,
            size=size_hierarchy.get("body", 18),
            weight="normal",
            color="text_primary",
        )
        caption = FontConfig(
            family=most_frequent,
            size=max(10, (size_hierarchy.get("body", 18) or 18) - 4),
            color="text_secondary",
        )

        return Typography(heading=heading, body=body, caption=caption)

    def _classify_spacing(self, spacing_values: List[int]) -> Spacing:
        """Infer spacing from extracted values.

        Args:
            spacing_values: List of spacing values in pixels.

        Returns:
            A Spacing instance.
        """
        if spacing_values:
            sorted_vals = sorted(spacing_values)
            n = len(sorted_vals)
            if n % 2 == 1:
                content_gap = sorted_vals[n // 2]
            else:
                content_gap = int((sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2)
        else:
            content_gap = 20

        return Spacing(
            slide_padding=[40, 40, 40, 40],
            content_gap=content_gap,
            line_spacing=1.5,
        )

    @staticmethod
    def _luminance(hex_color: str) -> float:
        """Compute relative luminance of a hex color.

        Args:
            hex_color: Hex color string.

        Returns:
            Relative luminance value (0-1).
        """
        r, g, b = hex_to_rgb(hex_color)
        # Convert to linear RGB
        rs = r / 255.0
        gs = g / 255.0
        bs = b / 255.0

        rl = rs / 12.92 if rs <= 0.03928 else ((rs + 0.055) / 1.055) ** 2.4
        gl = gs / 12.92 if gs <= 0.03928 else ((gs + 0.055) / 1.055) ** 2.4
        bl = bs / 12.92 if bs <= 0.03928 else ((bs + 0.055) / 1.055) ** 2.4

        return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl

    @staticmethod
    def _saturation(hex_color: str) -> float:
        """Compute saturation of a hex color (0-1 scale).

        Args:
            hex_color: Hex color string.

        Returns:
            Saturation value (0-1).
        """
        r, g, b = hex_to_rgb(hex_color)
        max_val = max(r, g, b)
        min_val = min(r, g, b)

        if max_val == 0:
            return 0.0

        return (max_val - min_val) / max_val
