"""
Database query utilities for Track Tracker.

This module provides helper functions for querying the database.
It uses SessionLocal from session.py to create sessions and run queries.

Usage:
    # From the CLI
    uv run python main.py stats

    # From Python
    from app.db.query import show_stats
    show_stats()
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Artist, Track, TrackArtist, TrackSnapshot, Video, VideoStat
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


def show_stats() -> None:
    """
    Print a summary of how many rows are in each table.

    This demonstrates the basic pattern for using sessions:
        1. Create a session with SessionLocal()
        2. Use the session to run queries
        3. Close the session when done (the 'with' block does this automatically)
    """
    # The 'with' statement ensures the session is closed when we're done,
    # even if an error occurs. This is important — unclosed sessions leak
    # database connections.
    with SessionLocal() as session:
        artist_count = session.query(Artist).count()
        track_count = session.query(Track).count()
        link_count = session.query(TrackArtist).count()
        video_count = session.query(Video).count()
        stat_count = session.query(VideoStat).count()

    print("=" * 40)
    print("  Track Tracker — Database Statistics")
    print("=" * 40)
    print(f"  Artists:       {artist_count}")
    print(f"  Tracks:        {track_count}")
    print(f"  Track-Artist:  {link_count}")
    print(f"  Videos:        {video_count}")
    print(f"  Video Stats:   {stat_count}")
    print("=" * 40)


# === Track Growth Stats ===


def _nearest_snapshot_before(
    session: Session, track_id: int, cutoff: datetime
) -> TrackSnapshot | None:
    """Return the most recent snapshot at or before cutoff, or None."""
    return (
        session.query(TrackSnapshot)
        .filter(
            TrackSnapshot.track_id == track_id,
            TrackSnapshot.recorded_at <= cutoff,
        )
        .order_by(TrackSnapshot.recorded_at.desc())
        .first()
    )


def _growth(old_val: int | None, new_val: int | None) -> dict:
    """Return absolute and percentage change between two values."""
    if old_val is None or new_val is None:
        return {"absolute": None, "percent": None}
    absolute = new_val - old_val
    percent = round((absolute / old_val) * 100, 2) if old_val != 0 else None
    return {"absolute": absolute, "percent": percent}


def get_track_stats(track_id: int, session: Session) -> dict | None:
    """
    Calculate growth stats for a track across standard time windows.

    Uses TrackSnapshot rows (appended each pipeline run) to compute how
    much spotify_streams has changed over the past day, week, month, year,
    and all-time. Returns None if the track does not exist.
    """
    track = session.query(Track).filter(Track.id == track_id).first()
    if not track:
        return None

    # Use naive UTC datetime to match the naive TIMESTAMP column
    now = datetime.utcnow()

    latest = _nearest_snapshot_before(session, track_id, now)
    if not latest:
        return {
            "track_id": track_id,
            "track_name": track.name,
            "spotify_id": track.spotify_id,
            "snapshot_count": 0,
            "latest_streams": None,
            "latest_recorded_at": None,
            "growth": {},
        }

    earliest = (
        session.query(TrackSnapshot)
        .filter(TrackSnapshot.track_id == track_id)
        .order_by(TrackSnapshot.recorded_at.asc())
        .first()
    )

    windows = {
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "year": timedelta(days=365),
    }
    growth = {}
    for label, delta in windows.items():
        old = _nearest_snapshot_before(session, track_id, now - delta)
        growth[label] = _growth(
            old.spotify_streams if old else None,
            latest.spotify_streams,
        )
    growth["all_time"] = _growth(
        earliest.spotify_streams if earliest else None,
        latest.spotify_streams,
    )

    snapshot_count = (
        session.query(func.count(TrackSnapshot.id))
        .filter(TrackSnapshot.track_id == track_id)
        .scalar()
    )

    return {
        "track_id": track_id,
        "track_name": track.name,
        "spotify_id": track.spotify_id,
        "snapshot_count": snapshot_count,
        "latest_streams": latest.spotify_streams,
        "latest_recorded_at": latest.recorded_at.isoformat(),
        "growth": growth,
    }
