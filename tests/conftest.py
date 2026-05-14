import pytest
from pathlib import Path


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def sample_theme_dict():
    return {
        "colors": {
            "primary": "#1E3A5F",
            "secondary": "#4A90D9",
            "accent": "#E67E22",
            "background": "#FFFFFF",
            "surface": "#F5F7FA",
            "text_primary": "#2C3E50",
            "text_secondary": "#7F8C8D",
            "text_on_primary": "#FFFFFF",
        },
        "fonts": {
            "heading": {
                "family": "Arial, sans-serif",
                "sizes": {"h1": 44, "h2": 32, "h3": 24},
                "weight": "bold",
                "color": "text_primary",
            },
            "body": {
                "family": "Arial, sans-serif",
                "size": 18,
                "weight": "normal",
                "color": "text_primary",
            },
            "caption": {
                "family": "Arial, sans-serif",
                "size": 14,
                "color": "text_secondary",
            },
        },
        "spacing": {
            "slide_padding": [40, 40, 40, 40],
            "content_gap": 20,
            "line_spacing": 1.5,
        },
        "aspect_ratio": "16:9",
        "slide_width": 10.0,
        "slide_height": 5.625,
    }
