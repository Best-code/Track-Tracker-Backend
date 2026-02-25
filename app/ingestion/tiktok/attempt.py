from .data_classes import Author, Sound, Video
from .exceptions import TikTokSoundCreationError, TikTokAuthorCreationError

from TikTokApi import TikTokApi
from TikTokApi.api import sound
import asyncio
import os

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# get your own ms_token from your cookies on tiktok.com
ms_token = os.environ.get("ms_token", None)


def sound_from_tiktok_sound(tiktok_sound: sound.Sound) -> Sound | None:
    if not getattr(tiktok_sound, "title"):
        raise TikTokSoundCreationError("Sound class lacks a Name")

    if tiktok_sound.title == "original sound":
        return None

    if not getattr(tiktok_sound, "author", None):
        # raise TikTokAuthorCreationError("Sound class lacks an Author")
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
        is_original=tiktok_sound.original
    )


async def trending_videos():
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
                if parsed_sound := sound_from_tiktok_sound(tiktok_sound=current_sound):
                    print(parsed_sound)
            except (TikTokSoundCreationError, TikTokAuthorCreationError) as e:
                logger.error(
                    f"Failed to create Sound : {current_sound.id} | {str(e)}")

if __name__ == "__main__":
    asyncio.run(trending_videos())
