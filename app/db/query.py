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
        snapshot_count = session.query(TrackSnapshot).count()
        link_count = session.query(TrackArtist).count()
        video_count = session.query(Video).count()
        stat_count = session.query(VideoStat).count()

    print("=" * 40)
    print("  Track Tracker — Database Statistics")
    print("=" * 40)
    print(f"  Artists:         {artist_count}")
    print(f"  Tracks:          {track_count}")
    print(f"  Track Snapshots: {snapshot_count}")
    print(f"  Track-Artist:    {link_count}")
    print(f"  Videos:          {video_count}")
    print(f"  Video Stats:     {stat_count}")
    print("=" * 40)
