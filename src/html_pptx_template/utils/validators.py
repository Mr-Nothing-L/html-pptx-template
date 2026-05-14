"""Validation utility functions for HTML-PPTX template extraction."""

import re


def validate_url(url: str) -> str:
    """Validate that a string is a valid HTTP or HTTPS URL.

    Args:
        url: The URL string to validate.

    Returns:
        The URL string unchanged if valid.

    Raises:
        ValueError: If the URL is not a valid http(s) URL.
    """
    if not isinstance(url, str) or not url:
        raise ValueError("URL must be a non-empty string")

    if not re.match(r"^https?://", url, re.IGNORECASE):
        raise ValueError(f"URL must start with http:// or https://: {url!r}")

    return url


def sanitize_template_id(name: str) -> str:
    """Convert a template name to a kebab-case ID.

    Lowercases the name, replaces spaces with hyphens, and removes
    special characters.

    Args:
        name: The template name to sanitize.

    Returns:
        A kebab-case template ID string.

    Raises:
        ValueError: If sanitization yields an empty string.
    """
    if not isinstance(name, str):
        raise ValueError("Template name must be a string")

    # Lowercase
    sanitized = name.lower()

    # Replace spaces and underscores with hyphens
    sanitized = re.sub(r"[\s_]+", "-", sanitized)

    # Remove non-alphanumeric and non-hyphen characters
    sanitized = re.sub(r"[^a-z0-9-]", "", sanitized)

    # Collapse multiple hyphens
    sanitized = re.sub(r"-+", "-", sanitized)

    # Strip leading/trailing hyphens
    sanitized = sanitized.strip("-")

    if not sanitized:
        raise ValueError("Sanitized template ID is empty")

    return sanitized
