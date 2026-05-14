"""Tests for ScreenshotCapture."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from html_pptx_template.extractor.screenshot import ScreenshotCapture


@pytest.fixture
def mock_page():
    """Create a mocked Playwright Page."""
    page = MagicMock()
    page.screenshot = AsyncMock()
    return page


@pytest.fixture
def capture(mock_page):
    return ScreenshotCapture(mock_page)


@pytest.mark.asyncio
async def test_capture_fullpage(mock_page, capture, tmp_path):
    """Verify full_page=True screenshot."""
    output_path = str(tmp_path / "screenshots" / "fullpage.png")

    result = await capture.capture_fullpage(output_path)

    assert result == Path(output_path)
    mock_page.screenshot.assert_called_once_with(path=output_path, full_page=True)
    assert Path(output_path).parent.exists()


@pytest.mark.asyncio
async def test_capture_element(mock_page, capture, tmp_path):
    """Verify element screenshot with locator."""
    output_path = str(tmp_path / "screenshots" / "element.png")

    mock_locator = MagicMock()
    mock_locator.screenshot = AsyncMock()
    mock_page.locator = MagicMock(return_value=mock_locator)

    result = await capture.capture_element("#hero", output_path)

    assert result == Path(output_path)
    mock_page.locator.assert_called_once_with("#hero")
    mock_locator.screenshot.assert_called_once_with(path=output_path)
    assert Path(output_path).parent.exists()


@pytest.mark.asyncio
async def test_capture_element_not_found(mock_page, capture, tmp_path):
    """Verify element screenshot returns None when element not found."""
    output_path = str(tmp_path / "screenshots" / "missing.png")

    mock_locator = MagicMock()
    mock_locator.screenshot = AsyncMock(side_effect=Exception("Element not found"))
    mock_page.locator = MagicMock(return_value=mock_locator)

    result = await capture.capture_element("#nonexistent", output_path)

    assert result is None


@pytest.mark.asyncio
async def test_capture_viewport(mock_page, capture, tmp_path):
    """Verify viewport screenshot (no full_page)."""
    output_path = str(tmp_path / "screenshots" / "viewport.png")

    result = await capture.capture_viewport(output_path)

    assert result == Path(output_path)
    mock_page.screenshot.assert_called_once_with(path=output_path, full_page=False)
    assert Path(output_path).parent.exists()
