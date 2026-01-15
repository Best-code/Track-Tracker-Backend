"""
Database query utilities and analytics functions.

This module provides helper functions for querying track data,
generating statistics, and analyzing popularity trends.
"""

from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db_context
from app.db.models import Track, TrackSnapshot


def get_track_count(db: Session) -> int:
    """Return total number of tracks in the database."""
    return db.query(Track).count()


def get_snapshot_count(db: Session) -> int:
    """Return total number of snapshots in the database."""
    return db.query(TrackSnapshot).count()


def get_top_tracks(db: Session, limit: int = 10) -> list[Track]:
    """
    Retrieve tracks with highest popularity scores.

    Args:
        db: Database session
        limit: Maximum number of tracks to return

    Returns:
        List of Track objects ordered by popularity descending
    """
    return (
        db.query(Track)
        .order_by(Track.popularity.desc())
        .limit(limit)
        .all()
    )


def get_recent_snapshots(db: Session, limit: int = 5) -> list[TrackSnapshot]:
    """
    Retrieve most recent popularity snapshots with track data.

    Uses eager loading to avoid N+1 queries when accessing track info.

    Args:
        db: Database session
        limit: Maximum number of snapshots to return

    Returns:
        List of TrackSnapshot objects with loaded track relationships
    """
    return (
        db.query(TrackSnapshot)
        .options(joinedload(TrackSnapshot.track))
        .order_by(TrackSnapshot.timestamp.desc())
        .limit(limit)
        .all()
    )


def show_stats() -> None:
    """
    Print summary statistics to stdout.

    Displays:
    - Total track and snapshot counts
    - Top 10 tracks by popularity
    - 5 most recent snapshots
    """
    with get_db_context() as db:
        track_count = get_track_count(db)
        snapshot_count = get_snapshot_count(db)
        print(f"Total tracks: {track_count}")
        print(f"Total snapshots: {snapshot_count}")

        print("\nTop 10 tracks by popularity:")
        for track in get_top_tracks(db, limit=10):
            pop = track.popularity if track.popularity else 0
            print(f"  {pop:3d} | {track.name[:40]:<40} | {track.artist}")

        print("\nMost recent snapshots:")
        for snapshot in get_recent_snapshots(db, limit=5):
            track = snapshot.track
            track_name = track.name[:30] if track else "Unknown"
            artist = track.artist if track else "Unknown"
            print(f"  {snapshot.timestamp} | {track_name} | {artist} | pop: {snapshot.popularity}")


if __name__ == "__main__":
    show_stats()