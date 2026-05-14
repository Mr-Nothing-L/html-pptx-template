"""Browser-based style extraction using Playwright."""

from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright


class BrowserExtractor:
    """Extract visual styles from a webpage using headless browser."""

    def __init__(self, viewport_width: int = 1920, viewport_height: int = 1080):
        self.viewport = {"width": viewport_width, "height": viewport_height}

    async def extract_styles(
        self,
        url: str,
        screenshot_dir: Optional[str] = None,
        wait_for: str = "networkidle",
    ) -> dict:
        """Launch headless Chromium, navigate to URL, extract computed styles and screenshots.

        Args:
            url: The URL to navigate to.
            screenshot_dir: Optional directory to save multiple screenshots.
            wait_for: Playwright wait_until option.

        Returns:
            Dict with: colors, fonts, font_sizes, spacing, page_title, screenshots.
        """
        screenshots = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport=self.viewport,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0",
            )
            page = await context.new_page()

            # Try navigation with fallback - even on timeout, page may be partially loaded
            page_loaded = False
            try:
                await page.goto(url, wait_until=wait_for, timeout=60000)
                page_loaded = True
            except Exception:
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page_loaded = True
                except Exception:
                    try:
                        await page.goto(url, timeout=90000)
                        page_loaded = True
                    except Exception:
                        # Navigation failed completely - but page may still have content
                        # Try to wait a bit for any rendered content
                        await page.wait_for_timeout(5000)

            # Wait a bit for any lazy-loaded content
            if page_loaded:
                await page.wait_for_timeout(2000)
            else:
                # If navigation failed, wait longer for any partial render
                await page.wait_for_timeout(8000)

            # Capture multiple screenshots
            if screenshot_dir:
                assets_dir = Path(screenshot_dir)
                assets_dir.mkdir(parents=True, exist_ok=True)

                # 1. Full page screenshot
                fullpage_path = assets_dir / "fullpage.png"
                try:
                    await page.screenshot(path=str(fullpage_path), full_page=True)
                    screenshots.append(str(fullpage_path))
                except Exception:
                    pass

                # 2. First viewport (hero section)
                viewport_path = assets_dir / "viewport_1.png"
                try:
                    await page.screenshot(path=str(viewport_path), full_page=False)
                    screenshots.append(str(viewport_path))
                except Exception:
                    pass

                # 3. Second viewport (scroll down)
                try:
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await page.wait_for_timeout(500)
                    viewport2_path = assets_dir / "viewport_2.png"
                    await page.screenshot(path=str(viewport2_path), full_page=False)
                    screenshots.append(str(viewport2_path))
                except Exception:
                    pass

                # 4. Third viewport (scroll down more)
                try:
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await page.wait_for_timeout(500)
                    viewport3_path = assets_dir / "viewport_3.png"
                    await page.screenshot(path=str(viewport3_path), full_page=False)
                    screenshots.append(str(viewport3_path))
                except Exception:
                    pass

                # 5. Scroll back to top for style extraction
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(300)

            # Extract computed styles via JS
            result = await page.evaluate(
                """() => {
                    const elements = document.querySelectorAll('*');
                    const total = elements.length;
                    const step = Math.max(1, Math.floor(total / 500));
                    const sampled = [];

                    for (let i = 0; i < total && sampled.length < 500; i += step) {
                        sampled.push(elements[i]);
                    }

                    const colors = new Set();
                    const fonts = new Set();
                    const fontSizes = new Set();
                    const spacing = new Set();

                    for (const el of sampled) {
                        const style = window.getComputedStyle(el);

                        const bg = style.backgroundColor;
                        if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                            colors.add(bg);
                        }

                        const color = style.color;
                        if (color) colors.add(color);

                        const borderColor = style.borderColor;
                        if (borderColor && borderColor !== 'rgba(0, 0, 0, 0)') {
                            colors.add(borderColor);
                        }

                        const fontFamily = style.fontFamily;
                        if (fontFamily) {
                            const first = fontFamily.split(',')[0].trim().replace(/["']/g, '');
                            if (first && first !== 'monospace') fonts.add(first);
                        }

                        const fontSize = style.fontSize;
                        if (fontSize) {
                            const px = parseInt(fontSize, 10);
                            if (px >= 10 && px <= 120) {
                                fontSizes.add(px);
                            }
                        }

                        const pt = style.paddingTop;
                        if (pt) {
                            const px = parseInt(pt, 10);
                            if (px >= 1 && px <= 100) spacing.add(px);
                        }

                        const mt = style.marginTop;
                        if (mt) {
                            const px = parseInt(mt, 10);
                            if (px >= 1 && px <= 100) spacing.add(px);
                        }
                    }

                    return {
                        colors: Array.from(colors).slice(0, 50),
                        fonts: Array.from(fonts).slice(0, 20),
                        font_sizes: Array.from(fontSizes),
                        spacing: Array.from(spacing),
                        page_title: document.title || '',
                    };
                }"""
            )

            await context.close()
            await browser.close()

            result["screenshots"] = screenshots
            return result
