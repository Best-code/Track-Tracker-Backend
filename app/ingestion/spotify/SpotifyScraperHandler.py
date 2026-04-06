"""
Scrapes stream counts from Spotify's web player.

Spotify's public API deprecated the popularity field and does not expose
raw stream counts. This module uses Playwright to load the track page on
open.spotify.com and extract the play count shown to listeners.
"""

import re

from playwright.async_api import async_playwright

from app.logging_config import get_logger

logger = get_logger(__name__)

STREAM_COUNT_SELECTOR = '[data-testid="playcount"]'


async def get_spotify_stream_count(spotify_id: str) -> int | None:
    """
    Scrape the stream count for a track from open.spotify.com.

    Args:
        spotify_id: The Spotify track ID (e.g. "5N3HkzE2tHAMaKMlnLfRVq").

    Returns:
        Stream count as an integer, or None if it cannot be found.
    """
    url = f"https://open.spotify.com/track/{spotify_id}"
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)

            element = await page.query_selector(STREAM_COUNT_SELECTOR)
            if not element:
                logger.warning(f"Stream count element not found for track {spotify_id}")
                return None

            text = await element.inner_text()
            # Strip commas/periods from formatted numbers like "1,234,567" or "1.234.567"
            count = int(re.sub(r"[,.]", "", text.strip()))
            logger.info(f"Stream count for {spotify_id}: {count:,}")
            return count
    except Exception as e:
        logger.error(f"Failed to scrape stream count for {spotify_id}: {e}")
        return None
