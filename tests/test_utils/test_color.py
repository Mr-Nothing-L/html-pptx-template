"""Tests for color utility functions."""

import pytest

from html_pptx_template.utils.color import hex_to_rgb, rgb_to_hex, normalize_color, color_distance


class TestHexToRgb:
    """Tests for hex_to_rgb function."""

    def test_valid_six_digit_hex(self):
        """Convert standard 6-digit hex color to RGB tuple."""
        assert hex_to_rgb("#FF5733") == (255, 87, 51)

    def test_valid_hex_without_hash(self):
        """Convert hex color without leading # to RGB tuple."""
        assert hex_to_rgb("FF5733") == (255, 87, 51)

    def test_black(self):
        """Convert black hex to RGB."""
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_white(self):
        """Convert white hex to RGB."""
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_invalid_hex_too_short(self):
        """Raise ValueError for hex string with fewer than 6 digits."""
        with pytest.raises(ValueError):
            hex_to_rgb("#FFF")

    def test_invalid_hex_non_hex_chars(self):
        """Raise ValueError for hex string with non-hex characters."""
        with pytest.raises(ValueError):
            hex_to_rgb("#GGGGGG")

    def test_invalid_hex_empty_string(self):
        """Raise ValueError for empty string."""
        with pytest.raises(ValueError):
            hex_to_rgb("")


class TestRgbToHex:
    """Tests for rgb_to_hex function."""

    def test_standard_rgb(self):
        """Convert RGB tuple to hex string with leading #."""
        assert rgb_to_hex((255, 87, 51)) == "#FF5733"

    def test_black(self):
        """Convert black RGB to hex."""
        assert rgb_to_hex((0, 0, 0)) == "#000000"

    def test_white(self):
        """Convert white RGB to hex."""
        assert rgb_to_hex((255, 255, 255)) == "#FFFFFF"

    def test_lowercase_values(self):
        """Convert low RGB values to zero-padded hex."""
        assert rgb_to_hex((0, 15, 255)) == "#000FFF"


class TestNormalizeColor:
    """Tests for normalize_color function."""

    def test_hex_with_hash(self):
        """Return hex color unchanged when already normalized."""
        assert normalize_color("#FF5733") == "#FF5733"

    def test_hex_without_hash(self):
        """Add leading # to hex color missing it."""
        assert normalize_color("FF5733") == "#FF5733"

    def test_rgb_function(self):
        """Convert rgb() string to #RRGGBB hex."""
        assert normalize_color("rgb(255, 87, 51)") == "#FF5733"

    def test_rgb_function_with_spaces(self):
        """Handle rgb() with extra whitespace."""
        assert normalize_color("rgb( 255 , 87 , 51 )") == "#FF5733"

    def test_rgba_function(self):
        """Convert rgba() string to #RRGGBB hex (drop alpha)."""
        assert normalize_color("rgba(255, 87, 51, 0.5)") == "#FF5733"

    def test_rgba_function_opaque(self):
        """Convert opaque rgba() to hex."""
        assert normalize_color("rgba(0, 0, 0, 1.0)") == "#000000"

    def test_invalid_color_raises(self):
        """Raise ValueError for unrecognized color format."""
        with pytest.raises(ValueError):
            normalize_color("not-a-color")

    def test_invalid_rgb_raises(self):
        """Raise ValueError for malformed rgb() string."""
        with pytest.raises(ValueError):
            normalize_color("rgb(999, 0, 0)")


class TestColorDistance:
    """Tests for color_distance function."""

    def test_identical_colors(self):
        """Distance between identical colors is zero."""
        assert color_distance("#FF5733", "#FF5733") == 0.0

    def test_different_colors(self):
        """Distance between different colors is greater than zero."""
        assert color_distance("#FF0000", "#00FF00") > 0.0

    def test_black_white_distance(self):
        """Distance between black and white is large."""
        dist = color_distance("#000000", "#FFFFFF")
        assert dist > 50.0

    def test_similar_colors_small_distance(self):
        """Distance between similar colors is small."""
        dist = color_distance("#FF0000", "#FE0000")
        assert dist < 5.0

    def test_rgb_input_accepted(self):
        """Accept rgb() string as input."""
        dist = color_distance("rgb(255, 0, 0)", "#FF0000")
        assert dist == 0.0

    def test_rgba_input_accepted(self):
        """Accept rgba() string as input."""
        dist = color_distance("rgba(255, 0, 0, 0.5)", "#FF0000")
        assert dist == 0.0
