"""
NOT database models
Transport containers for the pipeline
"""

from dataclasses import dataclass, field

from app.db.models import Artist, Track


@dataclass
class ParsedTrack:
    """
    A Spotify track and its associated artists.
    """

    track: Track
    artists: list[Artist] = field(default_factory=list)