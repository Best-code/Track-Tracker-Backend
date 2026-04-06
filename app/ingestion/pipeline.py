from typing import List

from app.ingestion.spotify.SpotifyHandler import SpotifyHandler
from app.ingestion.spotify.SpotifyScraperHandler import get_spotify_stream_count
from app.ingestion.tiktok.TikTokHandler import TikTokHandler
from app.ingestion.data_classes import ParsedTrack, PipelineResult
from app.db.models import Artist, Track, TrackArtist, TrackSnapshot
from app.db.session import SessionLocal
from app.logging_config import get_logger

logger = get_logger(__name__)


async def get_tiktok_song_titles() -> list[str]:
    """Fetch song titles from TikTok hashtag searches."""
    async with TikTokHandler() as tiktok:
        sounds = await tiktok.search_hashtags()

    titles = []
    for s in sounds:
        if s.author:
            titles.append(f"{s.author.username} - {s.name}")
        else:
            titles.append(s.name)
    logger.info(f"Got {len(titles)} song titles from TikTok")
    return titles


def tiktok_to_spotify(titles: list[str]) -> list[ParsedTrack]:
    handler = SpotifyHandler()
    results = []
    for title in titles:
        try:
            result = handler.get_track_by_title(title)
            if result:
                results.append(result)
                logger.info(f"Matched: '{title}' -> {result.track.name}")
        except Exception as e:
            logger.error(f"Spotify lookup failed for '{title}': {e}")
    logger.info(f"Matched {len(results)}/{len(titles)} titles on Spotify")
    return results


async def save_tracks_to_db(parsed_tracks: list[ParsedTrack]) -> None:
    with SessionLocal() as session:
        for parsed in parsed_tracks:
            track: Track = parsed.track
            artists: List[Artist] = parsed.artists
            # Upsert artists
            db_artists: List[Artist] = []
            for artist in artists:
                existing = (
                    session.query(Artist)
                    .filter_by(spotify_id=artist.spotify_id)
                    .first()
                )
                if existing:
                    db_artists.append(existing)
                else:
                    session.add(artist)
                    session.flush()
                    db_artists.append(artist)

            # Upsert track
            existing_track = (
                session.query(Track).filter_by(spotify_id=track.spotify_id).first()
            )
            if existing_track:
                db_track = existing_track
            else:
                session.add(track)
                session.flush()
                db_track = track

            # Create TrackArtist junction rows
            for artist in db_artists:
                exists = (
                    session.query(TrackArtist)
                    .filter_by(track_id=db_track.id, artist_id=artist.id)
                    .first()
                )
                if not exists:
                    # TODO Determine role primary / featured / producer
                    link = TrackArtist(
                        track_id=db_track.id,
                        artist_id=artist.id,
                        role="primary",
                    )
                    session.add(link)

            # Scrape stream count and record snapshot
            stream_count = await get_spotify_stream_count(db_track.spotify_id)
            snapshot = TrackSnapshot(
                track_id=db_track.id,
                spotify_streams=stream_count,
            )
            session.add(snapshot)
            logger.info(
                f"Snapshot recorded for '{db_track.name}' "
                f"(streams={stream_count:,})" if stream_count else
                f"Snapshot recorded for '{db_track.name}' (streams=None)"
            )

        session.commit()


async def run_pipeline() -> PipelineResult:
    titles = await get_tiktok_song_titles()
    parsed_tracks = tiktok_to_spotify(titles)
    await save_tracks_to_db(parsed_tracks)
    return PipelineResult(tracks_processed=len(parsed_tracks))
