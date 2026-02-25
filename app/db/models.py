"""
Defines the PostgreSQL schema for tracking rising music tracks
across Spotify and TikTok platforms.
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, JSON, ForeignKey, TIMESTAMP,
    create_engine, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# === Core Entities ===

class Artist(Base):
    """
    Music artists and TikTok creators.

    Stores metadata from both Spotify and TikTok. All platform-specific
    columns are nullable because an artist may only exist on one platform
    initially.
    """
    __tablename__ = "Artist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)

    # Spotify fields
    spotify_id = Column(String, nullable=True, unique=True)
    spotify_href = Column(String, nullable=True)
    spotify_uri = Column(String, nullable=True)
    spotify_type = Column(String, nullable=True)
    spotify_popularity = Column(Integer, nullable=True)
    spotify_external_urls = Column(JSON, nullable=True)
    spotify_genres = Column(JSON, nullable=True)
    spotify_images = Column(JSON, nullable=True)

    # TikTok fields
    tiktok_id = Column(String, nullable=True, unique=True)
    tiktok_username = Column(String, nullable=True)
    tiktok_followers = Column(Integer, nullable=True)

    # Relationships
    track_links = relationship("TrackArtist", back_populates="artist")
    videos = relationship("Video", back_populates="author")


class Track(Base):
    """
    Individual music tracks from Spotify and TikTok.

    spotify_popularity (0-100) is a key signal for detecting rising tracks.
    JSON columns store nested API response data (external_urls, markets, etc).
    """
    __tablename__ = "Track"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)

    # Spotify fields
    spotify_id = Column(String, nullable=True, unique=True)
    spotify_href = Column(String, nullable=True)
    spotify_uri = Column(String, nullable=True)
    spotify_type = Column(String, nullable=True)
    spotify_duration_ms = Column(Integer, nullable=True)
    spotify_explicit = Column(Boolean, nullable=True)
    spotify_popularity = Column(Integer, nullable=True)
    spotify_disc_number = Column(Integer, nullable=True)
    spotify_track_number = Column(Integer, nullable=True)
    spotify_is_local = Column(Boolean, nullable=True)
    spotify_preview_url = Column(String, nullable=True)
    spotify_external_urls = Column(JSON, nullable=True)
    spotify_external_ids = Column(JSON, nullable=True)
    spotify_available_markets = Column(JSON, nullable=True)

    # TikTok fields
    tiktok_sound_id = Column(String, nullable=True, unique=True)
    tiktok_duration_s = Column(Integer, nullable=True)
    tiktok_is_original = Column(Boolean, nullable=True)

    # Relationships
    artist_links = relationship("TrackArtist", back_populates="track")
    videos = relationship("Video", back_populates="track")


# === Junction Tables ===

class TrackArtist(Base):
    """
    Many-to-many relationship between Track and Artist.

    The 'role' column distinguishes credit type:
      - "primary"  : main artist
      - "featured" : featured collaborator
      - "producer" : track producer
    """
    __tablename__ = "TrackArtist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey("Track.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("Artist.id"), nullable=False)
    role = Column(String, nullable=False)

    # Relationships
    track = relationship("Track", back_populates="artist_links")
    artist = relationship("Artist", back_populates="track_links")


# === Platform-Specific Entities ===

class Video(Base):
    """
    TikTok videos that use a tracked song as their sound.

    author_id references Artist because TikTok creators are stored
    in the Artist table alongside music artists.
    """
    __tablename__ = "Video"

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey("Track.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("Artist.id"), nullable=False)
    tiktok_id = Column(String, nullable=True, unique=True)
    create_time = Column(TIMESTAMP, nullable=True)

    # Relationships
    track = relationship("Track", back_populates="videos")
    author = relationship("Artist", back_populates="videos")
    stats = relationship("VideoStat", back_populates="video")


class VideoStat(Base):
    """
    Time-series snapshots of video statistics.

    Uses an EAV (Entity-Attribute-Value) pattern:
      stat_name  = "views", "likes", "shares", "comments"
      stat_value = the count at that point in time
      recorded_at = when the snapshot was taken

    This design is flexible -- if TikTok adds a new metric,
    no schema migration is needed.
    """
    __tablename__ = "VideoStat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("Video.id"), nullable=False)
    stat_name = Column(String, nullable=False)
    stat_value = Column(Integer, nullable=False)
    recorded_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    video = relationship("Video", back_populates="stats")
