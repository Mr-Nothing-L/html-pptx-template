"""Screenshot capture utilities using Playwright."""

from pathlib import Path
from typing import Optional

from playwright.async_api import Page


class ScreenshotCapture:
    """Capture screenshots of webpages or elements."""

    def __init__(self, page: Page):
        self.page = page

    async def capture_fullpage(self, output_path: str) -> Path:
        """Capture a full-page screenshot.

        Args:
            output_path: Path to save the screenshot.

        Returns:
            Path to the saved screenshot.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        await self.page.screenshot(path=str(path), full_page=True)
        return path

    async def capture_element(self, selector: str, output_path: str) -> Optional[Path]:
        """Capture a screenshot of a specific element.

        Args:
            selector: CSS selector for the element.
            output_path: Path to save the screenshot.

        Returns:
            Path to the saved screenshot, or None if element not found.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            locator = self.page.locator(selector)
            await locator.screenshot(path=str(path))
            return path
        except Exception:
            return None

    async def capture_viewport(self, output_path: str) -> Path:
        """Capture a viewport screenshot.

        Args:
            output_path: Path to save the screenshot.

        Returns:
            Path to the saved screenshot.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        await self.page.screenshot(path=str(path), full_page=False)
        return path
