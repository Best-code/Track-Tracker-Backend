"""
Spotify data ingestion pipeline.

This module handles fetching track data from Spotify's API and persisting
it to the database. Designed for scheduled execution via Airflow or cron.

Features:
- Batched database operations for efficiency
- Configurable release limits
- Structured logging for monitoring
- Error handling with partial commit support

Usage:
    uv run python -m app.ingestion.spotify.ingest_to_db
"""

import logging
import os
from dataclasses import dataclass

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from app.db.database import get_db_context
from app.db.models import Track, TrackSnapshot


# Configure module logger
logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    """Results from an ingestion run."""
    tracks_processed: int
    snapshots_created: int
    errors: int


def get_spotify_client() -> spotipy.Spotify:
    """
    Create an authenticated Spotify API client.

    Requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables.

    Returns:
        Authenticated Spotify client instance

    Raises:
        KeyError: If required environment variables are not set
    """
    client_id = os.environ["SPOTIFY_CLIENT_ID"]
    client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def ingest_new_releases(limit: int = 20, batch_size: int = 50) -> IngestionResult:
    """
    Fetch new releases from Spotify and store in database.

    Retrieves recent album releases, extracts all tracks with popularity
    metrics, and creates both Track records (upserted) and TrackSnapshot
    records (appended) for time-series analysis.

    Args:
        limit: Maximum number of albums to fetch from new releases
        batch_size: Number of records to accumulate before flushing to DB

    Returns:
        IngestionResult with counts of processed records
    """
    sp = get_spotify_client()

    result = IngestionResult(tracks_processed=0, snapshots_created=0, errors=0)

    logger.info(f"Starting ingestion of {limit} new releases")

    # Get new releases
    releases = sp.new_releases(limit=limit)
    albums = releases["albums"]["items"]

    with get_db_context() as db:
        pending_count = 0

        for album in albums:
            try:
                album_tracks = sp.album_tracks(album["id"])

                for item in album_tracks["items"]:
                    try:
                        # Get full track info (includes popularity)
                        track_data = sp.track(item["id"])

                        # Upsert track record
                        track = Track(
                            id=track_data["id"],
                            name=track_data["name"],
                            artist=track_data["artists"][0]["name"],
                            album=album["name"],
                            popularity=track_data["popularity"]
                        )
                        db.merge(track)
                        result.tracks_processed += 1

                        # Create snapshot for time-series tracking
                        snapshot = TrackSnapshot(
                            track_id=track_data["id"],
                            popularity=track_data["popularity"]
                        )
                        db.add(snapshot)
                        result.snapshots_created += 1

                        pending_count += 1

                        # Flush in batches to manage memory
                        if pending_count >= batch_size:
                            db.flush()
                            pending_count = 0
                            logger.debug(f"Flushed batch, processed {result.tracks_processed} tracks")

                    except Exception as e:
                        logger.error(f"Error processing track {item.get('id', 'unknown')}: {e}")
                        result.errors += 1

            except Exception as e:
                logger.error(f"Error processing album {album.get('id', 'unknown')}: {e}")
                result.errors += 1

    logger.info(
        f"Ingestion complete: {result.tracks_processed} tracks, "
        f"{result.snapshots_created} snapshots, {result.errors} errors"
    )

    return result


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    result = ingest_new_releases()
    print(f"Ingested {result.tracks_processed} tracks, {result.snapshots_created} snapshots")