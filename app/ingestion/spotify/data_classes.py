from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Artist:
    # Required Fields
    id: str
    href: str

    # Optional Fields
    name: Optional[str] = None
    uri: Optional[str] = None
    type: Optional[str] = None
    external_urls: Optional[dict] = None
    followers: Optional[dict] = None
    genres: list[str] = field(default_factory=list)
    images: list[dict] = field(default_factory=list)
    popularity: Optional[int] = None


@dataclass
class IndividualTrack:
    # Required fields
    id: str
    href: str
    artist_ids: list[str] = field(default_factory=list)

    # Optional fields
    artists: list[Artist] = field(default_factory=list)
    name: Optional[str] = None
    uri: Optional[str] = None
    type: Optional[str] = None
    duration_ms: Optional[int] = None
    explicit: Optional[bool] = None
    popularity: Optional[int] = None
    disc_number: Optional[int] = None
    track_number: Optional[int] = None
    is_local: Optional[bool] = None
    preview_url: Optional[str] = None
    available_markets: list[str] = field(default_factory=list)
    external_urls: Optional[dict] = None
    external_ids: Optional[dict] = None
