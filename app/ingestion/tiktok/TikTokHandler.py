import os

from TikTokApi import TikTokApi
from TikTokApi.api import sound

from .constants import HASHTAGS
from .data_classes import Author, Sound
from app.logging_config import get_logger

logger = get_logger(__name__)


class TikTokHandler:
    def __init__(self):
        self._ms_token = os.environ.get("ms_token", None)
        self._browser = os.getenv("TIKTOK_BROWSER", "chromium")
        self._api: TikTokApi | None = None

    async def __aenter__(self):
        self._api = TikTokApi()
        await self._api.__aenter__()
        await self._api.create_sessions(
            ms_tokens=[self._ms_token],
            num_sessions=1,
            browser=self._browser,
            headless=False,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._api:
            await self._api.__aexit__(exc_type, exc_val, exc_tb)
            self._api = None

    @property
    def api(self) -> TikTokApi:
        if self._api is None:
            raise RuntimeError("TikTokHandler must be used as an async context manager")
        return self._api

    async def search_hashtags(self, count_per_hashtag: int = 50) -> list[Sound]:
        """Search TikTok for hashtag terms targeting small/midsize artists with new releases."""
        seen_ids: set[str] = set()
        discovered_sounds: list[Sound] = []

        for tag in HASHTAGS:
            search_term = f"#{tag}"
            logger.info(f"Searching TikTok for: {search_term}")
            video_count = 0
            try:
                async for video in self.api.search.search_type(
                    search_term, "item", count=count_per_hashtag
                ):
                    video_count += 1
                    current_sound: sound.Sound = video.sound
                    parsed_sound = self._parse_sound(current_sound)
                    if parsed_sound and parsed_sound.tiktok_id not in seen_ids:
                        seen_ids.add(parsed_sound.tiktok_id)
                        discovered_sounds.append(parsed_sound)
                        logger.info(
                            f"Found sound: {parsed_sound.name} "
                            f"(id: {parsed_sound.tiktok_id})"
                        )
            except Exception as e:
                logger.warning(f"Search failed for {search_term}: {e}")
            logger.info(f"Search '{search_term}': {video_count} videos returned")

        logger.info(
            f"Discovered {len(discovered_sounds)} unique sounds "
            f"across {len(HASHTAGS)} hashtag searches"
        )
        return discovered_sounds

    @staticmethod
    def _parse_sound(tiktok_sound: sound.Sound) -> Sound | None:
        """Parse a TikTok sound into our Sound dataclass. Returns None for original/untitled sounds."""
        if not getattr(tiktok_sound, "title"):
            return None

        if tiktok_sound.title == "original sound":
            return None

        if tiktok_sound.original:
            return None

        author = None
        if getattr(tiktok_sound, "author", None):
            author = Author(
                username=tiktok_sound.author.username,
                tiktok_id=tiktok_sound.author.user_id,
            )

        return Sound(
            name=tiktok_sound.title,
            author=author,
            tiktok_id=tiktok_sound.id,
        )
