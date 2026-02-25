from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from TikTokApi.api import sound

@dataclass
class Video:
    # Required Fields
    sound: Sound

    # Optional Fields
    author: Optional[Author] = None
    stats: Optional[dict] = None
    create_time: Optional[datetime] = None


@dataclass
class Author:
    # Required Fields
    username: str

    # Optional Fields
    tiktok_id: Optional[str] = None
    followers: Optional[int] = None


@dataclass
class Sound:
    # Required fields
    name: str

    # Optional fields
    author: Optional[Author] = None
    tiktok_id: Optional[str] = None
    duration_s: Optional[int] = None
    is_original: Optional[bool] = None
