"""CSS parser for normalizing raw computed styles."""

from collections import Counter
from typing import Dict, List

from html_pptx_template.utils.color import normalize_color


class CSSParser:
    """Parse raw computed styles into normalized format."""

    DEFAULT_SIZE_HIERARCHY = {"h1": 44, "h2": 32, "h3": 24, "body": 18}

    def parse(self, raw_styles: dict) -> dict:
        """Parse raw computed styles into normalized format.

        Args:
            raw_styles: Dict with colors, fonts, font_sizes, spacing, page_title.

        Returns:
            Dict with: normalized_colors, font_frequency, font_size_hierarchy,
            spacing_values, page_title.
        """
        return {
            "normalized_colors": self._normalize_colors(raw_styles.get("colors", [])),
            "font_frequency": self._count_fonts(raw_styles.get("fonts", [])),
            "font_size_hierarchy": self._build_size_hierarchy(
                raw_styles.get("font_sizes", [])
            ),
            "spacing_values": raw_styles.get("spacing", []),
            "page_title": raw_styles.get("page_title", ""),
        }

    def _normalize_colors(self, colors: List[str]) -> List[str]:
        """Normalize colors using normalize_color, deduplicate.

        Args:
            colors: List of raw color strings.

        Returns:
            List of normalized unique hex color strings.
        """
        normalized = []
        seen = set()
        for c in colors:
            try:
                hex_color = normalize_color(c)
                if hex_color not in seen:
                    seen.add(hex_color)
                    normalized.append(hex_color)
            except ValueError:
                continue
        return normalized

    def _count_fonts(self, fonts: List[str]) -> Dict[str, int]:
        """Count font frequency using collections.Counter.

        Args:
            fonts: List of font family strings.

        Returns:
            Dict mapping font family to occurrence count.
        """
        # Extract first family from comma-separated lists
        first_families = []
        for f in fonts:
            first = f.split(",")[0].strip()
            if first:
                first_families.append(first)
        return dict(Counter(first_families))

    def _build_size_hierarchy(self, sizes: List[int]) -> Dict[str, int]:
        """Map sorted sizes to h1, h2, h3, body levels.

        Args:
            sizes: List of font sizes in pixels.

        Returns:
            Dict with h1, h2, h3, body keys.
        """
        if not sizes:
            return dict(self.DEFAULT_SIZE_HIERARCHY)

        sorted_sizes = sorted(set(sizes), reverse=True)

        if len(sorted_sizes) >= 4:
            return {
                "h1": min(sorted_sizes[0], 80),
                "h2": sorted_sizes[1],
                "h3": sorted_sizes[2],
                "body": sorted_sizes[len(sorted_sizes) // 2],
            }
        elif len(sorted_sizes) >= 2:
            return {
                "h1": sorted_sizes[0],
                "h2": sorted_sizes[0],
                "h3": sorted_sizes[len(sorted_sizes) // 2],
                "body": sorted_sizes[-1],
            }
        else:
            # 1 size: use defaults with the one size as body
            result = dict(self.DEFAULT_SIZE_HIERARCHY)
            result["body"] = sorted_sizes[0]
            return result
