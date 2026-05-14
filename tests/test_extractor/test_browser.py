"""Tests for BrowserExtractor."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from html_pptx_template.extractor.browser import BrowserExtractor


@pytest.fixture
def mock_playwright():
    """Create a fully mocked Playwright context manager."""
    mock_pw = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    # Set up the async context manager chain
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)

    # Mock page methods
    mock_page.goto = AsyncMock()
    mock_page.screenshot = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.evaluate = AsyncMock(return_value={
        "colors": ["rgb(255, 255, 255)", "rgb(0, 0, 0)", "rgb(30, 58, 95)"],
        "fonts": ["Arial", "Helvetica", "Times New Roman"],
        "font_sizes": [16, 24, 32, 48],
        "spacing": [8, 16, 24, 32],
        "page_title": "Test Page",
        "screenshots": [],
    })

    # Mock context/browser close as async
    mock_context.close = AsyncMock()
    mock_browser.close = AsyncMock()

    # Mock JS evaluation return value
    mock_page.evaluate = AsyncMock(return_value={
        "colors": ["rgb(255, 255, 255)", "rgb(0, 0, 0)", "rgb(30, 58, 95)"],
        "fonts": ["Arial", "Helvetica", "Times New Roman"],
        "font_sizes": [16, 24, 32, 48],
        "spacing": [8, 16, 24, 32],
        "page_title": "Test Page",
    })

    # Set up async context manager for playwright
    mock_pw_obj = MagicMock()
    mock_pw_obj.__aenter__ = AsyncMock(return_value=mock_pw)
    mock_pw_obj.__aexit__ = AsyncMock(return_value=None)

    return {
        "pw_obj": mock_pw_obj,
        "pw": mock_pw,
        "browser": mock_browser,
        "context": mock_context,
        "page": mock_page,
    }


@pytest.mark.asyncio
async def test_extract_styles(mock_playwright):
    """Verify extract_styles returns correct dict structure."""
    with patch("html_pptx_template.extractor.browser.async_playwright", return_value=mock_playwright["pw_obj"]):
        extractor = BrowserExtractor(viewport_width=1920, viewport_height=1080)
        result = await extractor.extract_styles("https://example.com")

    assert "colors" in result
    assert "fonts" in result
    assert "font_sizes" in result
    assert "spacing" in result
    assert "page_title" in result
    assert result["page_title"] == "Test Page"
    assert len(result["colors"]) == 3
    assert len(result["fonts"]) == 3
    assert len(result["font_sizes"]) == 4
    assert len(result["spacing"]) == 4

    # Verify page.goto was called with the URL
    mock_playwright["page"].goto.assert_called_once_with(
        "https://example.com", wait_until="networkidle", timeout=60000
    )

    # Verify viewport was set with user_agent
    mock_playwright["browser"].new_context.assert_called_once_with(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0",
    )


@pytest.mark.asyncio
async def test_extract_styles_screenshot(mock_playwright):
    """Verify screenshots are captured when screenshot_dir provided."""
    with patch("html_pptx_template.extractor.browser.async_playwright", return_value=mock_playwright["pw_obj"]):
        extractor = BrowserExtractor()
        result = await extractor.extract_styles(
            "https://example.com",
            screenshot_dir="/tmp/screenshots",
            wait_for="networkidle"
        )

    assert result["page_title"] == "Test Page"
    assert "screenshots" in result
    # Screenshots are attempted (may be mocked paths)
    mock_playwright["page"].screenshot.assert_called()


@pytest.mark.asyncio
async def test_extract_styles_no_screenshot(mock_playwright):
    """Verify screenshots are NOT captured when dir not provided."""
    with patch("html_pptx_template.extractor.browser.async_playwright", return_value=mock_playwright["pw_obj"]):
        extractor = BrowserExtractor()
        result = await extractor.extract_styles("https://example.com")

    # Only viewport screenshot is attempted when no screenshot_dir
    assert result["screenshots"] == []
