from .constants import HASHTAGS, SEARCH_QUERIES
from .data_classes import Author, Sound
from .exceptions import TikTokSoundCreationError, TikTokAuthorCreationError

from TikTokApi import TikTokApi
from TikTokApi.api import sound
import asyncio
import os

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# get your own ms_token from your cookies on tiktok.com
ms_token = os.environ.get("ms_token", None)


async def search_new_releases(count_per_query: int = 20) -> list[Sound]:
    """Search TikTok for videos related to new music releases and extract their sounds."""
    seen_ids: set[str] = set()
    discovered_sounds: list[Sound] = []

    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=False,
        )

        for query in SEARCH_QUERIES:
            logger.info(f"Searching TikTok for: '{query}'")
            async for video in api.search.search_type(
                query, "item", count=count_per_query
            ):
                current_sound: sound.Sound = video.sound
                try:
                    parsed_sound = _sound_from_tiktok_sound(
                        tiktok_sound=current_sound)
                    if parsed_sound and parsed_sound.tiktok_id not in seen_ids:
                        seen_ids.add(parsed_sound.tiktok_id)
                        discovered_sounds.append(parsed_sound)
                        logger.info(
                            f"Found sound: {parsed_sound.name} "
                            f"(id: {parsed_sound.tiktok_id})"
                        )
                except (TikTokSoundCreationError, TikTokAuthorCreationError) as e:
                    logger.error(
                        f"Failed to create Sound : {current_sound.id} | {str(e)}"
                    )

    logger.info(
        f"Discovered {len(discovered_sounds)} unique sounds across {len(SEARCH_QUERIES)} queries")
    return discovered_sounds


async def search_hashtags(count_per_hashtag: int = 20) -> list[Sound]:
    """Search TikTok hashtags targeting small/midsize artists with new releases."""
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
            logger.info(f"Searching hashtag: #{tag}")
            async for video in api.hashtag(name=tag).videos(count=count_per_hashtag):
                current_sound: sound.Sound = video.sound
                try:
                    parsed_sound = _sound_from_tiktok_sound(
                        tiktok_sound=current_sound)
                    if parsed_sound and parsed_sound.tiktok_id not in seen_ids:
                        seen_ids.add(parsed_sound.tiktok_id)
                        discovered_sounds.append(parsed_sound)
                        logger.info(
                            f"Found sound: {parsed_sound.name} "
                            f"(id: {parsed_sound.tiktok_id})"
                        )
                except (TikTokSoundCreationError, TikTokAuthorCreationError) as e:
                    logger.error(
                        f"Failed to create Sound : {current_sound.id} | {str(e)}"
                    )

    logger.info(
        f"Discovered {len(discovered_sounds)} unique sounds across {len(HASHTAGS)} hashtags")
    return discovered_sounds


async def trending_videos():
    trending_sounds: list[Sound] = []
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=False,
        )

        async for video in api.trending.videos(count=30):
            current_sound: sound.Sound = video.sound
            try:
                if parsed_sound := _sound_from_tiktok_sound(tiktok_sound=current_sound):
                    trending_sounds.append(parsed_sound)
            except (TikTokSoundCreationError, TikTokAuthorCreationError) as e:
                logger.error(
                    f"Failed to create Sound : {current_sound.id} | {str(e)}")

        return trending_sounds


def _sound_from_tiktok_sound(tiktok_sound: sound.Sound) -> Sound | None:
    if not getattr(tiktok_sound, "title"):
        raise TikTokSoundCreationError("Sound class lacks a Name")

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
        duration_s=tiktok_sound.duration,
        is_original=tiktok_sound.original,
    )


if __name__ == "__main__":
    sounds = asyncio.run(search_hashtags())
    for s in sounds:
        print(f"  {s.name} | by {s.author.username if s.author else 'Unknown'} | id: {s.tiktok_id}")
