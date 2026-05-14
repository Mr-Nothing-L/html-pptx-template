"""Color utility functions for HTML-PPTX template extraction."""

import re
from typing import Tuple

import numpy as np
from colour import CCS_ILLUMINANTS, RGB_to_XYZ, XYZ_to_Lab, delta_E
from colour.models import RGB_COLOURSPACE_sRGB


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert a hex color string to an (R, G, B) tuple.

    Args:
        hex_color: A hex color string, with or without leading '#'.

    Returns:
        A tuple of three integers in the range 0-255.

    Raises:
        ValueError: If the input is not a valid 6-digit hex color.
    """
    hex_color = hex_color.strip()
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]

    if len(hex_color) != 6:
        raise ValueError(f"Hex color must be 6 digits, got: {hex_color!r}")

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        raise ValueError(f"Invalid hex color: {hex_color!r}")

    return (r, g, b)


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert an (R, G, B) tuple to a hex color string.

    Args:
        rgb: A tuple of three integers in the range 0-255.

    Returns:
        A hex color string with leading '#'.
    """
    r, g, b = rgb
    return f"#{r:02X}{g:02X}{b:02X}"


def _parse_rgb_string(color_str: str) -> Tuple[int, int, int]:
    """Parse an rgb() or rgba() string into (R, G, B).

    Args:
        color_str: A string like 'rgb(255, 87, 51)' or 'rgba(255, 87, 51, 0.5)'.

    Returns:
        A tuple of three integers in the range 0-255.

    Raises:
        ValueError: If the string is malformed or values are out of range.
    """
    # Match rgb(r, g, b) or rgba(r, g, b, a)
    match = re.match(r"rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)", color_str)
    if not match:
        raise ValueError(f"Invalid rgb/rgba format: {color_str!r}")

    r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))

    if not all(0 <= v <= 255 for v in (r, g, b)):
        raise ValueError(f"RGB values must be in range 0-255: {color_str!r}")

    return (r, g, b)


def normalize_color(color_str: str) -> str:
    """Normalize a color string to #RRGGBB hex format.

    Handles hex colors (with or without '#'), rgb(), and rgba() strings.

    Args:
        color_str: A color string in various formats.

    Returns:
        A normalized hex color string with leading '#'.

    Raises:
        ValueError: If the input is not a recognized color format.
    """
    color_str = color_str.strip()

    # Check for rgb() or rgba()
    if color_str.lower().startswith("rgb"):
        rgb = _parse_rgb_string(color_str)
        return rgb_to_hex(rgb)

    # Treat as hex
    return rgb_to_hex(hex_to_rgb(color_str))


def color_distance(color1: str, color2: str) -> float:
    """Compute the CIEDE2000 color distance between two colors.

    Args:
        color1: First color string (hex, rgb, or rgba).
        color2: Second color string (hex, rgb, or rgba).

    Returns:
        The CIEDE2000 delta E distance between the two colors.
    """
    rgb1 = normalize_color(color1)
    rgb2 = normalize_color(color2)

    # Convert hex to normalized RGB (0-1)
    r1, g1, b1 = np.array(hex_to_rgb(rgb1)) / 255.0
    r2, g2, b2 = np.array(hex_to_rgb(rgb2)) / 255.0

    # Convert to Lab via XYZ using the sRGB colourspace
    illuminant = CCS_ILLUMINANTS["CIE 1931 2 Degree Standard Observer"]["D65"]

    xyz1 = RGB_to_XYZ(
        np.array([r1, g1, b1]),
        colourspace=RGB_COLOURSPACE_sRGB,
    )
    lab1 = XYZ_to_Lab(xyz1, illuminant)

    xyz2 = RGB_to_XYZ(
        np.array([r2, g2, b2]),
        colourspace=RGB_COLOURSPACE_sRGB,
    )
    lab2 = XYZ_to_Lab(xyz2, illuminant)

    return float(delta_E(lab1, lab2, method="CIE 2000"))
