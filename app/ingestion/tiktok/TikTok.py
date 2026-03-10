from .constants import HASHTAGS
from .data_classes import Author, Sound
from app.logging_config import get_logger

from TikTokApi import TikTokApi
from TikTokApi.api import sound
import os


logger = get_logger(__name__)

# get your own ms_token from your cookies on tiktok.com
ms_token = os.environ.get("ms_token", None)


async def search_hashtags(count_per_hashtag: int = 20) -> list[Sound]:
    """Search TikTok for hashtag terms targeting small/midsize artists with new releases."""
    seen_ids: set[str] = set()
    discovered_sounds: list[Sound] = []

    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=False,
        )

        for tag in HASHTAGS:
            search_term = f"#{tag}"
            logger.info(f"Searching TikTok for: {search_term}")
            video_count = 0
            try:
                async for video in api.search.search_type(
                    search_term, "item", count=count_per_hashtag
                ):
                    video_count += 1
                    current_sound: sound.Sound = video.sound

                    parsed_sound = _sound_from_tiktok_sound(
                        tiktok_sound=current_sound
                    )
                    if parsed_sound and parsed_sound.tiktok_id not in seen_ids:
                        seen_ids.add(parsed_sound.tiktok_id)
                        discovered_sounds.append(parsed_sound)
                        logger.info(
                            f"Found sound: {parsed_sound.name} "
                            f"(id: {parsed_sound.tiktok_id})"
                        )

            except Exception as e:
                logger.warning(f"Search failed for {search_term}: {e}")
            logger.info(
                f"Search '{search_term}': {video_count} videos returned")

    logger.info(
        f"Discovered {len(discovered_sounds)} unique sounds across {len(HASHTAGS)} hashtag searches"
    )
    return discovered_sounds


def _sound_from_tiktok_sound(tiktok_sound: sound.Sound) -> Sound | None:
    if not getattr(tiktok_sound, "title"):
        return None

    if tiktok_sound.title == "original sound":
        return None

    if tiktok_sound.original:
        return None

    if not getattr(tiktok_sound, "author", None):
        author = None
    else:
        author: Author = Author(
            username=tiktok_sound.author.username,
            tiktok_id=tiktok_sound.author.user_id,
        )

    return Sound(
        name=tiktok_sound.title,
        author=author,
        tiktok_id=tiktok_sound.id,
    )
