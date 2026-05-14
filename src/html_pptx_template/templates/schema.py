"""Pydantic schema models for HTML-PPTX templates."""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from html_pptx_template.utils.color import normalize_color


class ColorPalette(BaseModel):
    """Color palette for a theme."""

    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text_primary: str
    text_secondary: str
    text_on_primary: str

    @field_validator("*", mode="before")
    @classmethod
    def validate_colors(cls, v):
        if isinstance(v, str):
            return normalize_color(v)
        return v


class FontConfig(BaseModel):
    """Font configuration for a text element."""

    family: str
    size: Optional[int] = None
    sizes: Optional[dict] = None
    weight: str = "normal"
    color: str = "text_primary"


class Typography(BaseModel):
    """Typography settings for a theme."""

    heading: FontConfig
    body: FontConfig
    caption: FontConfig


class Spacing(BaseModel):
    """Spacing settings for slides."""

    slide_padding: List[int] = Field(default=[40, 40, 40, 40])
    content_gap: int = 20
    line_spacing: float = 1.5


class Theme(BaseModel):
    """Visual theme for a presentation template."""

    colors: ColorPalette
    fonts: Typography
    spacing: Spacing
    aspect_ratio: str = "16:9"
    slide_width: float = 10.0
    slide_height: float = 5.625


class LayoutElement(BaseModel):
    """An element within a slide layout."""

    type: str
    style: dict = Field(default_factory=dict)
    position: Optional[dict] = None


class LayoutSlide(BaseModel):
    """A slide layout definition."""

    name: str
    slide_type: str
    background: Optional[str] = None
    elements: List[LayoutElement] = Field(default_factory=list)


class TemplateMeta(BaseModel):
    """Metadata for a template."""

    id: str
    name: str
    source_url: str
    source_title: Optional[str] = None
    source_favicon: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = Field(default_factory=list)
    version: int = 1


class Template(BaseModel):
    """A complete presentation template."""

    meta: TemplateMeta
    theme: Theme
    layouts: List[LayoutSlide] = Field(default_factory=list)


# Alias for backward compatibility
Layout = LayoutSlide
